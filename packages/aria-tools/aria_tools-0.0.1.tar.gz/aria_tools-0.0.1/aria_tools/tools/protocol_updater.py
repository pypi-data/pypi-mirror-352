"""Update a protocol based on feedback."""

from collections.abc import Callable
from typing import Any, Coroutine
from pydantic import Field, BaseModel
from hypha_rpc.utils.schema import schema_function  # type: ignore
from schema_agents.utils.common import EventBus  # type: ignore
from aria_tools.utils.models import (
    ExperimentalProtocol,
    ProtocolFeedback,
    to_pydantic_model,
    Document,
)
from aria_tools.utils.agents import ask_agent, AgentConfig


def create_protocol_update_function(
    llm_model: str, event_bus: EventBus | None = None
) -> Callable[
    ...,
    Coroutine[Any, Any, ExperimentalProtocol],
]:
    """Wrapper function to update a protocol based on feedback.

    Args:
        llm_model (str): The language model to use for updating the protocol.
        event_bus (EventBus | None, optional): An optional event bus for communication.
            Defaults to None.

    Returns:
        Callable: A callable that updates a protocol based on feedback."""

    @schema_function
    async def update_protocol(
        protocol: ExperimentalProtocol = Field(
            description="The protocol to update with feedback"
        ),
        feedback: ProtocolFeedback = Field(
            description=(
                "Feedback to make the protocol clearer for the lab worker who is"
                " executing it"
            )
        ),
        documents: list[Document] | None = Field(
            default_factory=list[Document],
            description="Optional documents related to the protocol",
        ),
        constraints: str | None = Field(
            default="",
            description="Optional constraints to apply for compiling experiments",
        ),
    ) -> ExperimentalProtocol:
        """Update a protocol based on feedback."""
        protocol = to_pydantic_model(ExperimentalProtocol, protocol)
        feedback = to_pydantic_model(ProtocolFeedback, feedback)
        doc_summaries = [str(document) for document in documents] if documents else []
        doc_summary_str = "\n\n".join(doc_summaries)

        prompt = (
            "You are being given a laboratory protocol that you have written and the feedback to"
            " make the protocol clearer for the lab worker who will execute it. First the protocol"
            " will be provided, then the feedback, and lastly the documents that you can use as"
            " sources for the protocol."
        )

        messages: list[str | BaseModel] = [prompt, protocol, feedback, doc_summary_str]

        agent_config = AgentConfig(
            name="Protocol Writer",
            instructions=(
                "You are an extremely detail oriented student who works in a biological laboratory."
                " You read protocols and revise them to be specific enough until you and your"
                " fellow students could execute the protocol yourself in the lab."
                " You do not conduct any data analysis, only data collection"
                " so your protocols only include steps up through the point"
                " of collecting data, not drawing conclusions."
            ),
            constraints=constraints,
            event_bus=event_bus,
            llm_model=llm_model,
            output_schema=ExperimentalProtocol,
            messages=messages,
        )
        return await ask_agent(agent_config)

    return update_protocol
