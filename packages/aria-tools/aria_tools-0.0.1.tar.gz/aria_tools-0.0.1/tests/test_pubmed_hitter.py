"""Test module for PubMed Central query hit counting functionality.

This module tests the ability to check the number of results (hits) that a PubMed Central
query would return, both with mocked responses and against the real PMC database.
"""

import pytest
from faker import Faker
from aria_tools.tools import check_pubmed_hits
from aria_tools.utils.models import PMCQuery

fake = Faker()


def generate_mock_entrez_result(count=3) -> dict:
    """Generate a mock Entrez search result with the specified number of hits.

    Args:
        count: Number of fake PMC IDs to generate

    Returns:
        Dict simulating Entrez esearch response format
    """
    return {
        "Count": str(count),
        "RetMax": str(count),
        "RetStart": "0",
        "IdList": [
            str(fake.random_int(min=1000000, max=9999999)) for _ in range(count)
        ],
    }


@pytest.mark.asyncio
async def test_check_pubmed_hits(mocker):
    """Test hit counting with a successful mock response.

    Verifies that the function correctly processes Entrez search results
    and returns the number of hits found.
    """
    # Mock Entrez.esearch and read
    mock_handle = mocker.Mock()
    mock_result = generate_mock_entrez_result(3)

    esearch_mock = mocker.patch("Bio.Entrez.esearch", return_value=mock_handle)
    read_mock = mocker.patch("Bio.Entrez.read", return_value=mock_result)
    mocker.patch.object(mock_handle, "close")

    # Generate realistic query using Faker
    medical_terms = ["cancer", "diabetes", "alzheimer", "obesity", "inflammation"]
    filters = ["Title/Abstract", "MeSH Terms", "Author"]
    query = PMCQuery(
        query_str=(
            f'"{fake.random_element(medical_terms)}"[{fake.random_element(filters)}]'
            ' AND "open access"[filter]'
        )
    )
    result = await check_pubmed_hits(query, paper_limit=100)

    assert result == 3
    esearch_mock.assert_called_once_with(db="pmc", term=query.query_str, retmax=100)
    read_mock.assert_called_once_with(mock_handle)
    mock_handle.close.assert_called_once()


@pytest.mark.asyncio
async def test_check_pubmed_hits_no_results(mocker):
    """Test hit counting when no results are found.

    Verifies that the function correctly handles and reports zero hits.
    """
    # Mock Entrez with empty results
    mock_handle = mocker.Mock()
    mock_result = generate_mock_entrez_result(0)

    mocker.patch("Bio.Entrez.esearch", return_value=mock_handle)
    mocker.patch("Bio.Entrez.read", return_value=mock_result)
    mocker.patch.object(mock_handle, "close")

    query = PMCQuery(query_str=f'"{fake.uuid4()}"[Title/Abstract]')
    result = await check_pubmed_hits(query, paper_limit=100)

    assert result == 0
    mock_handle.close.assert_called_once()


@pytest.mark.asyncio
async def test_check_pubmed_hits_error(mocker):
    """Test error handling when Entrez search fails.

    Verifies that errors from the Entrez API are properly propagated.
    """
    mocker.patch("Bio.Entrez.esearch", side_effect=RuntimeError("Entrez error"))

    query = PMCQuery(
        query_str=f'"{fake.random_element(["cancer", "diabetes"])}"[Title/Abstract]'
    )
    with pytest.raises(RuntimeError):
        await check_pubmed_hits(query, paper_limit=100)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.slow
async def test_check_pubmed_hits_integration():
    """Integration test using real PMC database."""
    # Use a query that should always return results
    query = PMCQuery(
        query_str='"cancer"[Title/Abstract] AND "open access"[filter] AND "2024"[pdat]'
    )
    result = await check_pubmed_hits(query, paper_limit=100)

    # Verify we get results
    assert result > 0, "Expected to find at least one paper about cancer in 2024"
    assert result <= 100, "Should respect paper_limit parameter"
