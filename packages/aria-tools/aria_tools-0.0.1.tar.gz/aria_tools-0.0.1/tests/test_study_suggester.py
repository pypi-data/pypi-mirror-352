"""Test module for study suggestion functionality.

This module tests the ability to generate research study suggestions based on user
requests and available scientific literature, including hypothesis generation and
experimental design.
"""

import pytest
from faker import Faker
from conftest import create_mock_document
from aria_tools.tools import create_study_suggester_function
from aria_tools.utils.models import SuggestedStudy

fake = Faker()


@pytest.mark.asyncio
async def test_suggest_study_mock(mocker):
    """Test study suggestion generation with mocked agent response.

    Verifies that:
    1. The function correctly calls the agent to generate a study suggestion
    2. The result follows the SuggestedStudy schema
    3. The suggestion contains expected components and metadata
    """
    # Mock the call_agent function
    mock_call_agent = mocker.patch("aria_tools.tools.study_suggester.call_agent")

    # Create mock documents
    mock_documents = [create_mock_document() for _ in range(3)]

    # Create user request
    user_request = "How does NAC affect aniline-induced hepatotoxicity?"

    # Create expected study suggestion with required fields and correct reference format
    expected_study = SuggestedStudy(
        experiment_name="Investigation of N-acetylcysteine (NAC) against aniline-induced hepatotoxicity",
        experiment_material=[
            "Adult male Sprague-Dawley rats",
            "N-acetylcysteine (NAC)",
            "Aniline",
            "Liver function test kits (ALT, AST, ALP)",
            "Oxidative stress markers (GSH, MDA, SOD)",
        ],
        experiment_workflow="Divide rats into four groups: control, NAC-only, aniline-only, and NAC+aniline. Administer NAC (200 mg/kg) and aniline (100 mg/kg) for 14 days. Collect blood and liver samples for biochemical and histological analysis.",
        experiment_expected_results="NAC-treated rats will show significantly lower levels of hepatic damage markers (ALT, AST, ALP) and oxidative stress markers compared to the aniline-only group. Histopathological examination will reveal reduced structural damage in liver tissue of the NAC+aniline group.",
        experiment_hypothesis="N-acetylcysteine (NAC) mitigates aniline-induced hepatotoxicity through its antioxidant properties and enhancement of glutathione synthesis.",
        experiment_reasoning="Aniline is known to cause oxidative damage in the liver, while NAC is a glutathione precursor with established hepatoprotective effects. Previous studies have shown NAC's effectiveness against various hepatotoxins, suggesting potential efficacy against aniline-induced damage.",
        description="This study will investigate the hepatoprotective effects of NAC against aniline-induced liver damage using a rat model. We will measure liver function parameters, oxidative stress markers, and histopathological changes to assess the protective mechanisms of NAC.",
        references=[
            "https://www.ncbi.nlm.nih.gov/pubmed/12345678",
            "https://www.ncbi.nlm.nih.gov/pubmed/23456789",
        ],
        user_request=user_request,
    )
    mock_call_agent.return_value = expected_study

    # Create tool instance
    suggest_study_fn = create_study_suggester_function("mock value", None)

    # Call the function
    result = await suggest_study_fn(
        user_request,
        mock_documents,
        "",
    )

    # Verify results
    assert isinstance(result, SuggestedStudy)
    assert result.experiment_name == expected_study.experiment_name
    assert result.experiment_hypothesis == expected_study.experiment_hypothesis
    assert len(result.experiment_material) == 5
    assert result.template_name == "suggested_study.html"
    assert result.user_request == user_request
    assert len(result.references) == 2
    mock_call_agent.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.slow
async def test_suggest_study(config, event_bus):
    """Test study suggestion generation.

    Verifies that:
    1. The function generates a valid study suggestion with all required fields
    2. Generated content follows the SuggestedStudy schema
    3. The original user request is preserved
    4. Relevant metadata for HTML template rendering is included
    """
    suggest_study_fn = create_study_suggester_function(config["llm_model"], event_bus)

    # Create mock documents
    mock_documents = [create_mock_document() for _ in range(3)]

    result = await suggest_study_fn(
        user_request="How does NAC affect aniline-induced hepatotoxicity?",
        documents=mock_documents,
        constraints="",
    )

    # Verify study content directly
    assert isinstance(result, SuggestedStudy)
    assert isinstance(result.experiment_name, str)
    assert isinstance(result.experiment_material, list)
    assert isinstance(result.experiment_workflow, str)
    assert isinstance(result.experiment_hypothesis, str)
    assert isinstance(result.experiment_reasoning, str)
    assert isinstance(result.description, str)
    assert isinstance(result.references, list)
    assert result.template_name == "suggested_study.html"
    assert result.user_request == "How does NAC affect aniline-induced hepatotoxicity?"
