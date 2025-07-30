"""This module provides a set of utility functions to interact with agents"""

from typing import Any
import uuid
from contextvars import ContextVar
from schema_agents.utils.common import current_session  # type: ignore
from schema_agents.role import create_session_context, Role  # type: ignore
from aria_tools.utils.models import AgentConfig


def get_session_id(session: ContextVar[None]) -> str:
    """Get the session ID from the provided ContextVar.

    Args:
        session (ContextVar): The current session context variable.

    Returns:
        str: The session ID.
    """
    pre_session = session.get()
    session_id = pre_session.id if pre_session else str(uuid.uuid4())
    return session_id


async def call_agent(config: AgentConfig) -> Any:
    """Call an agent and wait for its response"""
    if config.tools is None:
        config.tools = []
    agent = Role(
        name=config.name,
        instructions=config.instructions,
        icon="🤖",
        constraints=config.constraints,
        event_bus=config.event_bus,  # type: ignore
        register_default_events=True,
        model=config.llm_model,
    )

    session_id = get_session_id(current_session)
    async with create_session_context(id=session_id, role_setting=agent.role_setting):
        return await agent.acall(  # type: ignore
            req=config.messages, tools=config.tools, output_schema=config.output_schema
        )


async def ask_agent(config: AgentConfig) -> Any:
    """Ask an agent a question and wait for its response"""
    agent = Role(
        name=config.name,
        instructions=config.instructions,
        icon="🤖",
        constraints=config.constraints,
        event_bus=config.event_bus,  # type: ignore
        register_default_events=True,
        model=config.llm_model,
    )
    session_id = get_session_id(current_session)
    async with create_session_context(id=session_id, role_setting=agent.role_setting):
        return await agent.aask(  # type: ignore
            req=config.messages,
            output_schema=config.output_schema,
        )
