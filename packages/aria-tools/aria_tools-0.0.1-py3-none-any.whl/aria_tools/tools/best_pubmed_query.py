"""Generate multiple PubMed queries and return the one with the most hits."""

from collections.abc import Callable
from typing import Coroutine, Any
from pydantic import Field
from hypha_rpc.utils.schema import schema_function  # type: ignore
from schema_agents.utils.common import EventBus  # type: ignore
from aria_tools.utils.models import PMCQuery
from aria_tools.tools.pubmed_hitter import check_pubmed_hits
from aria_tools.utils.agents import call_agent, AgentConfig


def create_best_pubmed_query_tool(
    llm_model: str, event_bus: EventBus | None = None
) -> Callable[..., Coroutine[Any, Any, PMCQuery]]:
    """Wrapper function to create the get_best_pubmed_query tool.

    Args:
        llm_model (str): The language model to be used for generating queries.
        event_bus (EventBus | None, optional): An optional event bus for message handling.
            Defaults to None.

    Returns:
        Callable: A callable that generates the best PubMed query.
    """

    @schema_function
    async def get_best_pubmed_query(
        user_request: str = Field(
            description=(
                "The user's request to create a study around, framed in terms of a scientific"
                " question"
            )
        ),
    ) -> PMCQuery:
        """Generate multiple PubMed queries and return the one with the most hits."""
        agent_config = AgentConfig(
            name="NCBI Query Creator",
            instructions=(
                "You are the PubMed query creator. You take the user's input and generate"
                " queries that will return relevant papers."
            ),
            messages=[
                (
                    "Take the following user request and generate at least 5 different queries in"
                    " the schema of 'PMCQuery' to search PubMed Central for relevant papers."
                    " Ensure that all queries include the filter for open access papers."
                    " Test each query using the check_pubmed_hits tool to determine which query"
                    " returns the most hits. If no queries return hits, adjust the queries to be"
                    " more general (for example, by removing the [Title/Abstract] field"
                    " specifications from search terms), and try again."
                    " Once you have identified the query with the highest number of hits,"
                    " return that query."
                ),
                user_request,
                (
                    "After generating the study, you will make a call to CompleteUserQuery. You"
                    " should call that function with schema {'response': <PMCQuery>}."
                ),
            ],
            tools=[check_pubmed_hits],
            output_schema=PMCQuery,
            llm_model=llm_model,
            event_bus=event_bus,
        )

        return await call_agent(agent_config)

    return get_best_pubmed_query
