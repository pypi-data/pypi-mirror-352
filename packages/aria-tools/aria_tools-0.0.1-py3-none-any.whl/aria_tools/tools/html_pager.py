"""Create a summary HTML page for a research item."""

from collections.abc import Callable
from typing import Any, Coroutine
from pydantic import Field
from hypha_rpc.utils.schema import schema_function  # type: ignore
from schema_agents.utils.common import EventBus  # type: ignore
from aria_tools.utils.models import ModelWithTemplate, HTMLPage
from aria_tools.utils.agents import ask_agent, AgentConfig
from aria_tools.utils.io import load_template


def create_make_html_page(
    llm_model: str, event_bus: EventBus | None = None
) -> Callable[..., Coroutine[Any, Any, HTMLPage]]:
    """Create a summary HTML page for a research item.

    Args:
        llm_model (str): The language model to use for generating the HTML page.
        event_bus (EventBus | None, optional): An optional event bus for communication.
            Defaults to None.

    Returns:
        Callable: A callable that creates a HTML page for a research item.
    """

    @schema_function
    async def make_html_page(
        input_model: ModelWithTemplate = Field(
            description="The research item to create a HTML page for"
        ),
    ) -> HTMLPage:
        """Create a summary HTML page for a research item."""
        template_name = getattr(input_model, "template_name", "suggested_study.html")
        template = load_template(template_name)

        agent_config = AgentConfig(
            name="HTML Page Writer",
            instructions=(
                "You are an HTML page writer. You write a HTML page that neatly presents"
                " suggested studies or experimental protocols."
            ),
            messages=[
                "HTML page template:",
                template,
                "Model contents:",
                str(input_model),
            ],
            output_schema=HTMLPage,
            llm_model=llm_model,
            event_bus=event_bus,
        )

        return await ask_agent(agent_config)

    return make_html_page
