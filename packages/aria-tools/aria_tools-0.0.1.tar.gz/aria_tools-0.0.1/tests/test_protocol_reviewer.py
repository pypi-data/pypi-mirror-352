"""Test module for the protocol reviewer functionality.

This module tests the protocol review system, which evaluates experimental protocols
for completeness, clarity, and scientific rigor.
"""

import pytest
from faker import Faker
from aria_tools.tools import create_protocol_feedback_function
from aria_tools.utils.models import (
    ExperimentalProtocol,
    ProtocolSection,
    ProtocolFeedback,
)
from conftest import parametrize_model_inputs

fake = Faker()


def generate_equipment_list(experiment_type: str) -> list[str]:
    """Generate appropriate equipment list for a given experiment type."""
    equipment_lists = {
        "Cell Culture": [
            "Biosafety cabinet",
            "CO2 incubator",
            "Centrifuge",
            "Microscope",
            "Cell culture flasks",
            "Pipettes",
        ],
        "PCR": [
            "Thermal cycler",
            "Microcentrifuge",
            "Pipettes",
            "PCR tubes",
            "Ice bucket",
        ],
        "Western Blot": [
            "Electrophoresis system",
            "Transfer apparatus",
            "Power supply",
            "Imaging system",
            "Orbital shaker",
        ],
        "Flow Cytometry": [
            "Flow cytometer",
            "Centrifuge",
            "Sample tubes",
            "Cell strainer",
            "Pipettes",
        ],
        "ELISA": [
            "Microplate reader",
            "Microplate washer",
            "Multichannel pipette",
            "96-well plates",
            "Incubator",
        ],
    }
    return equipment_lists.get(
        experiment_type, [f"{fake.word()} apparatus" for _ in range(3)]
    )


def generate_cell_culture_sections() -> list[ProtocolSection]:
    """Generate protocol sections specific to cell culture experiments."""
    return [
        ProtocolSection(
            section_name="Culture Preparation",
            steps=[
                f"1. Prepare {fake.random_int(min=10, max=50)}ml of growth medium",
                f"2. Warm media to {fake.random_int(min=35, max=38)}°C",
                "3. Clean the biosafety cabinet with 70% ethanol",
            ],
            references=[fake.url()],
        ),
        ProtocolSection(
            section_name="Cell Passaging",
            steps=[
                "1. Remove media from flask",
                f"2. Wash cells with {fake.random_int(min=5, max=15)}ml PBS",
                f"3. Add {fake.random_int(min=2, max=5)}ml trypsin",
                f"4. Incubate for {fake.random_int(min=3, max=10)} minutes",
            ],
            references=[fake.url()],
        ),
    ]


def generate_generic_sections() -> list[ProtocolSection]:
    """Generate generic protocol sections for other experiment types."""
    return [
        ProtocolSection(
            section_name=f"{fake.word().capitalize()} Phase",
            steps=[f"{i+1}. {fake.sentence()}" for i in range(4)],
            references=[fake.url()],
        ),
        ProtocolSection(
            section_name=f"{fake.word().capitalize()} Phase",
            steps=[f"{i+1}. {fake.sentence()}" for i in range(3)],
            references=[fake.url()],
        ),
    ]


def generate_protocol_queries(experiment_type: str) -> list[str]:
    """Generate relevant PubMed queries for the protocol."""
    experiment_type_lower = experiment_type.lower()
    return [
        f"{experiment_type_lower} protocols",
        f"standard {experiment_type_lower} methods",
    ]


@pytest.fixture(name="mock_protocol")
def fixture_mock_protocol():
    """Generate a realistic lab protocol for testing."""
    experiment_types = [
        "Cell Culture",
        "PCR",
        "Western Blot",
        "Flow Cytometry",
        "ELISA",
    ]
    experiment_type = fake.random_element(experiment_types)

    # Generate sections based on experiment type
    sections = (
        generate_cell_culture_sections()
        if experiment_type == "Cell Culture"
        else generate_generic_sections()
    )

    return ExperimentalProtocol(
        protocol_title=f"{experiment_type} Protocol: {fake.bs()}",
        equipment=generate_equipment_list(experiment_type),
        sections=sections,
        queries=generate_protocol_queries(experiment_type),
    )


@pytest.mark.asyncio
async def test_protocol_feedback_mock(mocker, mock_protocol):
    """Test protocol feedback generation with mocked agent response.

    Verifies that:
    1. The function correctly calls the agent to generate feedback
    2. The result follows the ProtocolFeedback schema
    3. The feedback contains expected components
    """
    # Mock the ask_agent function
    mock_ask_agent = mocker.patch("aria_tools.tools.protocol_reviewer.ask_agent")
    mock_feedback = ProtocolFeedback(
        complete=False,
        feedback_points=[
            "Protocol lacks detailed reagent concentrations",
            "Missing temperature specifications",
            "Insufficient detail on equipment settings",
        ],
        suggestions=[
            "Add reagent concentrations for all solutions",
            "Specify incubation temperatures",
            "Include equipment model numbers and settings",
        ],
        previous_feedback="Previous feedback was addressed, but more detail is needed.",
    )
    mock_ask_agent.return_value = mock_feedback

    # Create tool instance
    protocol_feedback_fn = create_protocol_feedback_function("mock value", None)

    # Call the function with a mock protocol
    result = await protocol_feedback_fn(protocol=mock_protocol, constraints="")

    # Verify results
    assert isinstance(result, ProtocolFeedback)
    assert result.complete is False
    assert len(result.feedback_points) == 3
    assert len(result.suggestions) == 3
    mock_ask_agent.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.slow
@parametrize_model_inputs()
async def test_protocol_feedback(
    config, mock_protocol, event_bus, model_input_transformer
):
    """Test the protocol feedback functionality with different input formats.

    Verifies that the protocol reviewer can analyze a mock protocol in different formats
    and provide structured feedback including completeness assessment, feedback points,
    and suggestions for improvement.

    Args:
        config: Test configuration
        mock_protocol: ExperimentalProtocol fixture
        event_bus: Event bus for communication
        model_input_transformer: Function that transforms the model into the desired format
    """
    protocol_feedback_fn = create_protocol_feedback_function(
        config["llm_model"], event_bus
    )

    # Transform the protocol using the parametrized transformer function
    input_model = model_input_transformer(mock_protocol)

    # Get feedback using the transformed protocol
    result = await protocol_feedback_fn(protocol=input_model, constraints="")

    # Verify protocol feedback content directly
    assert isinstance(result, ProtocolFeedback)
    assert isinstance(result.complete, bool)
    assert isinstance(result.feedback_points, list)
    assert isinstance(result.suggestions, list)
    assert all(isinstance(x, str) for x in result.feedback_points)
    assert all(isinstance(x, str) for x in result.suggestions)
