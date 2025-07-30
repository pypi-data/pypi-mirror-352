"""Test module for PubMed query optimization functionality.

This module tests the ability to generate and validate effective PubMed Central queries
that maximize relevant open access results for a given research request.
"""

import pytest
from faker import Faker
from aria_tools.tools.best_pubmed_query import create_best_pubmed_query_tool
from aria_tools.utils.models import PMCQuery
from aria_tools.tools.pubmed_hitter import check_pubmed_hits

fake = Faker()


@pytest.mark.asyncio
async def test_get_best_pubmed_query(mocker):
    """Test query generation with mocked agent response.

    Verifies that:
    1. The function correctly calls the agent to generate queries
    2. The generated query includes the open access filter
    3. The result follows the PMCQuery schema
    """
    # Mock the call_agent function
    mock_call_agent = mocker.patch("aria_tools.tools.best_pubmed_query.call_agent")
    expected_query = PMCQuery(
        query_str='"cancer"[Title/Abstract] AND "open access"[filter]'
    )
    mock_call_agent.return_value = expected_query

    # Create tool instance
    get_best_pubmed_query = create_best_pubmed_query_tool("mock value", None)

    # Generate a realistic research request
    user_request = "What are the effects of chemotherapy on breast cancer patients?"

    result = await get_best_pubmed_query(user_request=user_request)

    assert isinstance(result, PMCQuery)
    assert '"open access"[filter]' in result.query_str
    mock_call_agent.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.slow
async def test_get_best_pubmed_query_integration(config, event_bus):
    """Integration test using real agent to generate and test queries.

    Tests query generation against common medical research topics, verifying that:
    1. Generated queries include the open access filter
    2. Queries return actual results from PMC
    """
    get_best_pubmed_query = create_best_pubmed_query_tool(
        config["llm_model"], event_bus
    )

    # Test cases with topics likely to have many open access papers
    test_cases = [
        "What are the effects of caffeine on cognitive performance?",
        "How does exercise affect cardiovascular health?",
        "What are the mechanisms of antibiotic resistance?",
    ]

    for user_request in test_cases:
        result = await get_best_pubmed_query(user_request=user_request)

        assert isinstance(result, PMCQuery)
        assert '"open access"[filter]' in result.query_str

        # Verify that the query returns some hits
        hits = await check_pubmed_hits(query_obj=result, paper_limit=100)
        assert (
            hits > 0
        ), f"Query '{result.query_str}' returned no hits for request: {user_request}"
