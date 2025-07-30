"""A tool for generating detailed experimental protocols from suggested studies."""

from collections.abc import Callable
from typing import Any, Coroutine
from hypha_rpc.utils.schema import schema_function  # type: ignore
from schema_agents.utils.common import EventBus  # type: ignore
from pydantic import Field
from aria_tools.utils.agents import ask_agent, AgentConfig
from aria_tools.utils.models import (
    ExperimentalProtocol,
    SuggestedStudy,
    to_pydantic_model,
)


def create_write_protocol(
    llm_model: str, event_bus: EventBus | None = None
) -> Callable[..., Coroutine[Any, Any, ExperimentalProtocol]]:
    """A tool for generating detailed experimental protocols from suggested studies."""

    @schema_function
    async def write_protocol(
        suggested_study: SuggestedStudy = Field(
            description="The suggested study to generate an experimental protocol from"
        ),
        constraints: str | None = Field(
            default="",
            description="Optional constraints to apply for compiling experiments",
        ),
    ) -> ExperimentalProtocol:
        """Generate a detailed experimental protocol from a suggested study."""
        suggested_study = to_pydantic_model(SuggestedStudy, suggested_study)
        prompt = (
            "Take the following suggested study and use it to produce a detailed"
            " protocol telling a student exactly what steps they should follow in"
            " the lab to collect data. Do not include any data analysis or"
            " conclusion-drawing steps, only data collection."
        )
        agent_config = AgentConfig(
            name="Protocol Manager",
            instructions=(
                "You are an expert laboratory scientist. You read protocols and manage"
                " them to ensure that they are clear and detailed enough for a new"
                " student to follow them exactly without any questions or doubts."
            ),
            messages=[prompt, suggested_study],
            output_schema=ExperimentalProtocol,
            llm_model=llm_model,
            event_bus=event_bus,
            constraints=constraints,
        )

        return await ask_agent(agent_config)

    return write_protocol
