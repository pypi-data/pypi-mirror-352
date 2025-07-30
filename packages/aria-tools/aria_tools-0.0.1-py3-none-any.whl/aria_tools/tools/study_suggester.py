"""This module contains the function to create a study suggester tool."""

from collections.abc import Callable
from typing import Any, Coroutine
from pydantic import Field
from hypha_rpc.utils.schema import schema_function  # type: ignore
from schema_agents.utils.common import EventBus  # type: ignore
from aria_tools.utils.models import (
    SuggestedStudy,
    Document,
)
from aria_tools.utils.agents import call_agent, AgentConfig


def create_study_suggester_function(
    llm_model: str, event_bus: EventBus | None = None
) -> Callable[..., Coroutine[Any, Any, SuggestedStudy]]:
    """Wrapper function to create a study suggester tool.

    Args:
        llm_model (str): The language model to use for generating the study.
        event_bus (EventBus | None, optional): An optional event bus for communication.
            Defaults to None.

    Returns:
        Callable: A callable that suggests a study based on user input and documents."""

    @schema_function
    async def run_study_suggester(
        user_request: str = Field(
            description="The user's request to create a study around"
        ),
        documents: list[Document] = Field(
            default_factory=list,
            description="The documents that the study suggester will use to generate the study",
        ),
        constraints: str | None = Field(
            default="", description="Optional constraints for the study"
        ),
    ) -> SuggestedStudy:
        """Suggests a study to test a new hypothesis based on the user request."""

        doc_summaries = [str(doc) for doc in documents]
        agent_config = AgentConfig(
            name="Study Suggester",
            instructions="You are the study suggester. You suggest a study to test a new hypothesis"
            " based on the cutting-edge information from the literature review.",
            messages=[
                (
                    "Design a study to address an open question in the field based on the following"
                    f" user request: ```{user_request}```"
                ),
                (
                    "After generating the study, you will make a call to CompleteUserQuery. You"
                    " should call that function with schema {'response': <SuggestedStudy>}."
                ),
                "You have the following documents that you can source your information from:\n\n"
                + "\n\n".join(doc_summaries),
            ],
            tools=[],
            output_schema=SuggestedStudy,
            llm_model=llm_model,
            event_bus=event_bus,
            constraints=constraints,
        )

        return await call_agent(agent_config)

    return run_study_suggester
