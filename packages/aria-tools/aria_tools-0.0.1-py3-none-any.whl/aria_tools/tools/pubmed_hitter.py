"""A tool to check the number of hits for a query in PubMed Central."""

from typing import Any, Dict
from Bio import Entrez
from pydantic import Field
from schema_agents import schema_tool  # type: ignore
from hypha_rpc.utils.schema import schema_function  # type: ignore
from aria_tools.utils.models import PMCQuery


@schema_tool
@schema_function
async def check_pubmed_hits(
    query_obj: PMCQuery = Field(
        description="The PubMed Central query to check for hits"
    ),
    paper_limit: int = Field(
        default=100,
        description="Maximum number of papers to return",
    ),
) -> int:
    """Check the number of hits for a query in PubMed Central."""

    async def _search() -> Dict[str, Any]:
        handle = Entrez.esearch(  # type: ignore
            db="pmc",
            term=query_obj.query_str,
            retmax=paper_limit,
        )
        result: dict[str, Any] = Entrez.read(handle)  # type: ignore
        handle.close()
        return result

    result = await _search()

    n_hits = len(result["IdList"])

    return n_hits
