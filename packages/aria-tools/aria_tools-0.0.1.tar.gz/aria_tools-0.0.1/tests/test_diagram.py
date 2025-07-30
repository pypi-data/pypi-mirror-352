"""Test module for study diagram generation functionality.

This module tests the ability to generate Mermaid diagrams representing study workflows from
suggested study descriptions."""

import pytest
from aria_tools.tools import create_diagram_function
from aria_tools.utils.models import StudyWithDiagram, StudyDiagram
from conftest import parametrize_model_inputs


@pytest.mark.asyncio
async def test_create_diagram_mock(mocker, suggested_study):
    """Test diagram generation with mocked agent response.

    Verifies that:
    1. The function correctly calls the agent to generate a diagram
    2. The result follows the StudyWithDiagram schema
    3. The diagram uses Mermaid graph syntax
    """
    # Mock the ask_agent function
    mock_ask_agent = mocker.patch("aria_tools.tools.diagrammer.ask_agent")

    # Create proper StudyDiagram instance for the mock return value
    mock_diagram = StudyDiagram(
        diagram_code="""graph TD
            A[Cell Culture] --> B[Treatment]
            B --> C[Analysis]
            C --> D[Results]"""
    )
    mock_ask_agent.return_value = mock_diagram

    # Create tool instance
    create_diagram_fn = create_diagram_function("mock value", None)

    # Call the function with a suggested study
    result = await create_diagram_fn(suggested_study=suggested_study)

    # Verify results
    assert isinstance(result, StudyWithDiagram)
    assert result.suggested_study == suggested_study
    assert "graph TD" in result.study_diagram.diagram_code
    mock_ask_agent.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.slow
@parametrize_model_inputs()
async def test_create_diagram(
    config, suggested_study, event_bus, model_input_transformer
):
    """Test diagram generation for a suggested study with different input formats.

    Verifies that:
    1. A diagram is successfully created from a suggested study in different formats
    2. The diagram uses Mermaid graph syntax
    3. The original study data is preserved in the result

    Args:
        config: Test configuration
        suggested_study: SuggestedStudy fixture
        event_bus: Event bus for communication
        model_input_transformer: Function that transforms the model into the desired format
    """
    create_diagram_fn = create_diagram_function(config["llm_model"], event_bus)

    # Transform the model using the parametrized transformer function
    input_model = model_input_transformer(suggested_study)

    # Create diagram with transformed input
    result = await create_diagram_fn(suggested_study=input_model)

    # Verify the diagram content directly
    assert isinstance(result, StudyWithDiagram)
    assert result.suggested_study == suggested_study
    assert "graph TD" in result.study_diagram.diagram_code
