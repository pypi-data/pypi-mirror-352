# The MIT License (MIT)
#
# Copyright (c) Jerry Liu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# This file contains code inspired by the original implementation by Jerry Liu.

"""A tool to query PubMed Central and return a corpus of papers."""

import asyncio
from typing import Any
import xml.etree.ElementTree as ET
from pydantic import Field
from hypha_rpc.utils.schema import schema_function  # type: ignore
from aria_tools.utils.models import PubmedResults, Document, PMCQuery, to_pydantic_model
from aria_tools.utils.config import Entrez


@schema_function
async def query_pubmed(
    pmc_query: PMCQuery = Field(
        description="The query to search the NCBI PubMed Central Database.",
    ),
    max_results: int = Field(
        default=10,
        description="The maximum number of papers to return.",
    ),
) -> PubmedResults:
    """Fetch PubMed documents based on a search query."""
    pmc_query = to_pydantic_model(PMCQuery, pmc_query)
    documents: list[Document] = []

    # Search PMC for IDs
    search_results = Entrez.esearch(  # type: ignore
        db="pmc", term=pmc_query.query_str, retmax=max_results
    )
    search_data: dict[str, Any] = Entrez.read(search_results)  # type: ignore
    search_results.close()

    for pmcid in search_data.get("IdList", []):
        fetch_results = Entrez.efetch(db="pmc", id=pmcid, retmode="xml")  # type: ignore
        fetch_data = fetch_results.read()
        fetch_results.close()
        root = ET.fromstring(fetch_data)

        title = root.findtext(".//article-title", default="Untitled")
        raw_text = " ".join(elem.text.strip() for elem in root.iter() if elem.text)
        journal = root.findtext(".//journal-title", default="Unknown Journal")
        publication_date = root.findtext(".//pub-date", default="Unknown Date")
        url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/"

        documents.append(
            Document(
                name=title,
                content=raw_text,
                metadata={
                    "journal": journal,
                    "url": url,
                    "publication_date": publication_date,
                    "type": "pubmed_article",
                },
            )
        )

        await asyncio.sleep(1)

    return PubmedResults(documents=documents, total_results=len(documents))
