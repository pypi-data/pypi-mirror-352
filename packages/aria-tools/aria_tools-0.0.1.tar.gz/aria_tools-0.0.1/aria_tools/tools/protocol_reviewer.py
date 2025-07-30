"""Provide feedback on an experimental protocol."""

from collections.abc import Callable
from typing import Coroutine, Any
from pydantic import Field
from schema_agents.utils.common import EventBus  # type: ignore
from hypha_rpc.utils.schema import schema_function  # type: ignore
from aria_tools.utils.models import ProtocolFeedback, ExperimentalProtocol
from aria_tools.utils.agents import ask_agent, AgentConfig


def create_protocol_feedback_function(
    llm_model: str, event_bus: EventBus | None = None
) -> Callable[..., Coroutine[Any, Any, ProtocolFeedback]]:
    """Wrapper function to provide feedback on an experimental protocol.

    Args:
        llm_model (str): The language model to use for generating feedback.
        event_bus (EventBus | None, optional): An optional event bus for communication.
            Defaults to None.

    Returns:
        Callable: A callable that provides feedback on an experimental protocol.
    """

    @schema_function
    async def protocol_feedback(
        protocol: ExperimentalProtocol = Field(
            description="The experimental protocol to provide feedback on"
        ),
        constraints: str | None = Field(
            default="",
            description="Optional constraints to apply for compiling experiments",
        ),
    ) -> ProtocolFeedback:
        """Provide feedback on an experimental protocol."""
        messages = [
            (
                "You are an expert lab scientist reviewing this protocol. Your task is to:"
                "\n1. Verify that the protocol is complete and detailed enough for execution by a"
                " new student"
                "\n2. Check for any missing steps, unclear instructions, or insufficient detail"
                "\n3. Suggest improvements, including whether additional sources should be fetched"
                " for certain techniques"
                "\n4. Make sure all reagent concentrations, temperatures, timings and equipment"
                " settings are specified"
                "\n5. Ensure proper citation of reference protocols for key steps"
                "\n6. Suggest additional queries to PubMed and the like for more relevant"
                " references"
            ),
            f"Protocol to review:\n{protocol}",
        ]

        agent_config = AgentConfig(
            name="Protocol Manager",
            instructions=(
                "You are an expert laboratory scientist. You read protocols and manage"
                " them to ensure that they are clear and detailed enough for a new"
                " student to follow them exactly without any questions or doubts."
            ),
            messages=messages,
            constraints=constraints,
            event_bus=event_bus,
            llm_model=llm_model,
            output_schema=ProtocolFeedback,
        )
        return await ask_agent(agent_config)

    return protocol_feedback
