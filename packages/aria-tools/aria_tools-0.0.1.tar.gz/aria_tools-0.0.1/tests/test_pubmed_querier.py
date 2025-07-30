"""Test module for PubMed Central querying functionality.

This module tests the ability to query and retrieve full documents from PubMed Central,
including XML parsing, error handling, and integration with the real PMC database.
"""

import pytest
from faker import Faker
from aria_tools.tools import query_pubmed
from aria_tools.utils.models import PMCQuery, PubmedResults
from conftest import parametrize_model_inputs

fake = Faker()


def generate_mock_xml() -> str:
    """Generate a mock PMC article XML with realistic metadata and content structure.

    Creates XML that mimics the structure of real PMC articles, with journal info,
    article metadata, and basic content sections.

    Returns:
        str: A mock PMC article XML string
    """
    # Generate realistic article metadata
    journal = fake.random_element(
        [
            "Nature Methods",
            "Cell",
            "Science",
            "PLOS ONE",
            "BMC Genomics",
            "Nature Communications",
        ]
    )

    keywords = [
        "genomics",
        "proteomics",
        "CRISPR",
        "immunotherapy",
        "bioinformatics",
        "cell signaling",
        "drug discovery",
    ]
    topic = fake.random_element(keywords)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE pmc-articleset PUBLIC "-//NLM//DTD ARTICLE SET 2.0//EN" "https://dtd.nlm.nih.gov/ncbi/pmc/articleset/nlm-articleset-2.0.dtd">
<pmc-articleset>
<article>
<front>
<journal-meta>
<journal-title>{journal}</journal-title>
<issn>{fake.bothify(text='####-####')}</issn>
</journal-meta>
<article-meta>
<title-group>
<article-title>Novel {topic} approaches: {fake.bs()}</article-title>
</title-group>
<contrib-group>
<contrib contrib-type="author">
<name><surname>{fake.last_name()}</surname><given-names>{fake.first_name()}</given-names></name>
<aff>{fake.company()}, {fake.city()}, {fake.country()}</aff>
</contrib>
</contrib-group>
<abstract>Background: {fake.text()} Methods: {fake.text()} Results: {fake.text()}</abstract>
<pub-date>
<year>2024</year>
<month>03</month>
<day>05</day>
</pub-date>
</article-meta>
</front>
<body>
<sec>
<title>Introduction</title>
<p>{". ".join([fake.sentence() for _ in range(3)])}</p>
</sec>
<sec>
<title>Methods</title>
<p>{". ".join([fake.sentence() for _ in range(3)])}</p>
</sec>
<sec>
<title>Results</title>
<p>{". ".join([fake.sentence() for _ in range(3)])}</p>
</sec>
</body>
</article>
</pmc-articleset>"""


@pytest.mark.asyncio
async def test_query_pubmed(mocker):
    """Test PubMed querying with mock responses.

    Verifies that the function can:
    - Execute a PMC search query
    - Parse XML responses into Document objects
    - Extract metadata and content correctly
    """
    # Mock Entrez functions
    mock_efetch = mocker.patch("Bio.Entrez.efetch")
    mock_read = mocker.patch("Bio.Entrez.read")

    # Generate random PMCIDs
    pmcids = [str(fake.random_int(min=1000000, max=9999999)) for _ in range(2)]

    # Setup mock returns
    mock_read.return_value = {"Count": "2", "IdList": pmcids}
    mock_efetch_response = mocker.Mock()
    mock_efetch_response.read.return_value = generate_mock_xml()
    mock_efetch.return_value = mock_efetch_response

    # Generate realistic query using scientific terms
    topic = fake.random_element(["cancer", "diabetes", "alzheimer", "covid"])
    filter_type = fake.random_element(["MeSH Terms", "Title/Abstract", "Author"])
    query = PMCQuery(query_str=f'"{topic}"[{filter_type}] AND "open access"[filter]')

    result = await query_pubmed(pmc_query=query)

    assert isinstance(result, PubmedResults)
    assert result.total_results == 2
    assert len(result.documents) == 2
    assert f"PMC{pmcids[0]}" in result.documents[0].metadata["url"]
    assert result.documents[0].content


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.slow
@parametrize_model_inputs()
async def test_query_pubmed_integration(model_input_transformer):
    """Integration test using real PMC database with different input formats.

    Tests that the query_pubmed function can handle different input formats:
    1. Direct PMCQuery object
    2. Dictionary representation (model_dump)
    3. JSON string representation (model_dump_json)

    Args:
        model_input_transformer: Function that transforms the model into the desired format
    """
    base_query = PMCQuery(
        query_str='"CRISPR"[Title/Abstract] AND "open access"[filter] AND "2024"[pdat]'
    )

    # Transform the query using the parametrized transformer function
    transformed_query = model_input_transformer(base_query)

    # Run the query with the transformed input
    result = await query_pubmed(pmc_query=transformed_query, max_results=5)

    # Verify results
    assert isinstance(result, PubmedResults)
    assert result.total_results > 0
    assert len(result.documents) > 0

    # Check document structure
    doc = result.documents[0]
    assert doc.name  # Should have a title
    assert doc.content  # Should have content
    assert doc.metadata  # Should have metadata
    assert "url" in doc.metadata
    assert "journal" in doc.metadata
    assert "publication_date" in doc.metadata
    assert "type" in doc.metadata and doc.metadata["type"] == "pubmed_article"
