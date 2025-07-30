"""Test module for protocol update functionality.

This module tests the ability to update experimental protocols based on reviewer feedback,
incorporating additional details and clarity improvements suggested by reviewers.
"""

import pytest
from conftest import create_mock_document, parametrize_model_inputs
from aria_tools.tools import create_protocol_update_function
from aria_tools.utils.models import (
    ExperimentalProtocol,
    ProtocolSection,
    ProtocolFeedback,
)


@pytest.mark.asyncio
async def test_update_protocol_mock(mocker):
    """Test protocol updating with mocked agent response.

    Verifies that:
    1. The function correctly calls the agent to update a protocol
    2. The result follows the ExperimentalProtocol schema
    3. The updated protocol contains expected components
    """
    # Mock the ask_agent function
    mock_ask_agent = mocker.patch("aria_tools.tools.protocol_updater.ask_agent")

    # Create original protocol
    original_protocol = ExperimentalProtocol(
        protocol_title="Test Protocol",
        equipment=["Equipment 1"],
        sections=[
            ProtocolSection(
                section_name="Test Section",
                steps=["Step 1"],
                references=["Reference 1"],
            )
        ],
    )

    # Create feedback
    feedback = ProtocolFeedback(
        complete=False,
        feedback_points=["Need more detail", "Missing reagent concentrations"],
        suggestions=["Add step 2", "Include buffer concentrations"],
        previous_feedback="Previous feedback was addressed, but more detail is needed.",
    )

    # Create mock documents
    documents = [create_mock_document() for _ in range(3)]

    # Create expected updated protocol
    expected_protocol = ExperimentalProtocol(
        protocol_title="Updated Test Protocol",
        equipment=["Equipment 1", "Equipment 2"],
        sections=[
            ProtocolSection(
                section_name="Test Section",
                steps=["Step 1", "Step 2: Add 5ml of 1X PBS buffer"],
                references=["Reference 1", "Reference 2"],
            ),
            ProtocolSection(
                section_name="Additional Section",
                steps=["Step 1: Prepare reagents", "Step 2: Analyze results"],
                references=["Reference 3"],
            ),
        ],
    )
    mock_ask_agent.return_value = expected_protocol

    # Create tool instance
    protocol_update_fn = create_protocol_update_function("mock value", None)

    # Call the function with protocol and feedback
    result = await protocol_update_fn(
        protocol=original_protocol,
        feedback=feedback,
        constraints="",
        documents=documents,
    )

    # Verify results
    assert isinstance(result, ExperimentalProtocol)
    assert result.protocol_title == expected_protocol.protocol_title
    assert len(result.equipment) == 2
    assert len(result.sections) == 2
    assert all(isinstance(section, ProtocolSection) for section in result.sections)
    mock_ask_agent.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.slow
@parametrize_model_inputs()
async def test_update_protocol(config, event_bus, model_input_transformer):
    """Test protocol updating based on reviewer feedback with different input formats.

    Verifies that:
    1. The function can process feedback and update a protocol in different formats
    2. The updated protocol maintains correct structure and data types
    3. Additional source documents can be incorporated into the update

    Args:
        config: Test configuration
        event_bus: Event bus for communication
        model_input_transformer: Function that transforms the model into the desired format
    """
    protocol = ExperimentalProtocol(
        protocol_title="Test Protocol",
        equipment=["Equipment 1"],
        sections=[
            ProtocolSection(
                section_name="Test Section",
                steps=["Step 1"],
                references=["Reference 1"],
            )
        ],
    )
    feedback = ProtocolFeedback(
        complete=False,
        feedback_points=["Need more detail"],
        suggestions=["Add step 2"],
        previous_feedback="Missing reagent concentrations",
    )
    documents = [create_mock_document() for _ in range(3)]

    # Transform the protocol using the parametrized transformer function
    transformed_protocol = model_input_transformer(protocol)

    # Also transform the feedback
    transformed_feedback = model_input_transformer(feedback)

    protocol_update_fn = create_protocol_update_function(config["llm_model"], event_bus)
    result = await protocol_update_fn(
        protocol=transformed_protocol,
        feedback=transformed_feedback,
        constraints="",
        documents=documents,
    )

    # Verify protocol content directly
    assert isinstance(result, ExperimentalProtocol)
    assert isinstance(result.protocol_title, str)
    assert isinstance(result.equipment, list)
    assert isinstance(result.sections, list)
    assert all(isinstance(x, ProtocolSection) for x in result.sections)
