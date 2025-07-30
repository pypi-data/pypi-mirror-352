"""Test module for HTML page generation functionality.

This module tests the ability to create formatted HTML pages that present suggested studies
or experimental protocols for user review, including proper formatting and inclusion of
diagrams when available.
"""

import pytest
from aria_tools.tools import create_make_html_page
from aria_tools.utils.models import HTMLPage
from conftest import parametrize_model_inputs


@pytest.mark.asyncio
async def test_make_html_page_mock(mocker, suggested_study):
    """Test HTML page generation with mocked agent response.

    Verifies that:
    1. The function correctly calls the agent to generate HTML
    2. The result follows the HTMLPage schema
    3. The HTML code includes the expected structure
    """
    # Mock the ask_agent function
    mock_ask_agent = mocker.patch("aria_tools.tools.html_pager.ask_agent")
    expected_html = HTMLPage(
        html_code="<html><head><title>Test Study</title></head><body><h1>Test Study</h1></body></html>"
    )
    mock_ask_agent.return_value = expected_html

    # Create tool instance
    make_html_page_fn = create_make_html_page("mock value", None)

    # Call the function with a suggested study
    result = await make_html_page_fn(input_model=suggested_study)

    # Verify results
    assert isinstance(result, HTMLPage)
    assert result.html_code == expected_html.html_code
    mock_ask_agent.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.slow
@parametrize_model_inputs()
async def test_make_html_page(
    config, suggested_study, event_bus, model_input_transformer
):
    """Test HTML page generation from a suggested study with different input formats.

    Verifies that:
    1. The function generates valid HTML output with different input formats
    2. The result follows the HTMLPage schema
    3. Basic HTML structure is present in the output

    Args:
        config: Test configuration
        suggested_study: SuggestedStudy fixture
        event_bus: Event bus for communication
        model_input_transformer: Function that transforms the model into the desired format
    """
    make_html_page_fn = create_make_html_page(config["llm_model"], event_bus)

    # Transform the model using the parametrized transformer function
    input_model = model_input_transformer(suggested_study)

    # Call the function with the prepared input
    result = await make_html_page_fn(input_model=input_model)

    # Verify results
    assert isinstance(result, HTMLPage)
    assert isinstance(result.html_code, str)
    assert "html" in result.html_code.lower()  # Basic HTML validation
