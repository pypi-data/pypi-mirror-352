"""Test module for protocol writing functionality.

This module tests the ability to generate detailed experimental protocols from suggested
study descriptions, ensuring proper structure and completeness.
"""

import pytest
from aria_tools.tools import create_write_protocol
from aria_tools.utils.models import ExperimentalProtocol, ProtocolSection
from conftest import parametrize_model_inputs


@pytest.mark.asyncio
async def test_write_protocol_mock(mocker, suggested_study):
    """Test protocol generation with mocked agent response.

    Verifies that:
    1. The function correctly calls the agent to generate a protocol
    2. The result follows the ExperimentalProtocol schema
    3. The protocol contains expected sections and metadata
    """
    # Mock the ask_agent function
    mock_ask_agent = mocker.patch("aria_tools.tools.protocol_writer.ask_agent")

    # Create expected protocol
    expected_protocol = ExperimentalProtocol(
        protocol_title="Investigation of NAC against aniline-induced hepatotoxicity",
        equipment=[
            "Spectrophotometer",
            "Centrifuge",
            "Microplate reader",
            "pH meter",
            "Electronic balance",
        ],
        sections=[
            ProtocolSection(
                section_name="Animal Preparation",
                steps=[
                    "1. Obtain adult male Sprague-Dawley rats (200-250g)",
                    "2. Acclimatize for one week under standard conditions (23±2°C, 12h light/dark)",
                    "3. Provide standard pellet diet and water ad libitum",
                    "4. Randomly divide into 4 groups (n=6): Control, NAC-only, Aniline-only, NAC+Aniline",
                ],
                references=["https://www.ncbi.nlm.nih.gov/pubmed/12345678"],
            ),
            ProtocolSection(
                section_name="Treatment Administration",
                steps=[
                    "1. Prepare NAC solution (200 mg/kg) in saline",
                    "2. Prepare aniline solution (100 mg/kg) in corn oil",
                    "3. Administer treatments for 14 days as follows:",
                    "   - Control: saline + corn oil vehicle",
                    "   - NAC-only: NAC solution + corn oil vehicle",
                    "   - Aniline-only: saline + aniline solution",
                    "   - NAC+Aniline: NAC solution followed by aniline solution (1 hour apart)",
                ],
                references=["https://www.ncbi.nlm.nih.gov/pubmed/23456789"],
            ),
        ],
        queries=[
            "NAC aniline hepatotoxicity protocol",
            "N-acetylcysteine liver protection methods",
        ],
    )
    mock_ask_agent.return_value = expected_protocol

    # Create tool instance
    write_protocol_fn = create_write_protocol("mock value", None)

    # Call the function with a suggested study
    result = await write_protocol_fn(suggested_study=suggested_study, constraints="")

    # Verify results
    assert isinstance(result, ExperimentalProtocol)
    assert result.protocol_title == expected_protocol.protocol_title
    assert result.template_name == "experimental_protocol.html"
    assert len(result.equipment) == 5
    assert len(result.sections) == 2
    assert all(isinstance(section, ProtocolSection) for section in result.sections)
    mock_ask_agent.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.slow
@parametrize_model_inputs()
async def test_write_protocol(
    config, suggested_study, event_bus, model_input_transformer
):
    """Test protocol generation from a suggested study with different input formats.

    Verifies that:
    1. The function generates a valid experimental protocol from different input formats
    2. The protocol contains all required sections (title, equipment, steps)
    3. The result includes necessary metadata for HTML template rendering

    Args:
        config: Test configuration
        suggested_study: SuggestedStudy fixture
        event_bus: Event bus for communication
        model_input_transformer: Function that transforms the model into the desired format
    """
    protocol_writer_fn = create_write_protocol(config["llm_model"], event_bus)

    # Transform the suggested study using the parametrized transformer function
    input_model = model_input_transformer(suggested_study)

    # Generate protocol with transformed input
    result = await protocol_writer_fn(suggested_study=input_model, constraints="")

    # Verify protocol content directly
    assert isinstance(result, ExperimentalProtocol)
    assert isinstance(result.protocol_title, str)
    assert isinstance(result.equipment, list)
    assert isinstance(result.sections, list)
    assert len(result.sections) > 0
    assert len(result.equipment) > 0
    assert result.template_name == "experimental_protocol.html"
