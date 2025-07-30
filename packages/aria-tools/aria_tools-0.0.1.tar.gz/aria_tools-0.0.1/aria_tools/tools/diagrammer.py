"""Create a diagram illustrating the workflow for a study."""

from collections.abc import Callable
from typing import Coroutine, Any
from pydantic import Field
from hypha_rpc.utils.schema import schema_function  # type: ignore
from schema_agents.utils.common import EventBus  # type: ignore
from aria_tools.utils.models import SuggestedStudy
from aria_tools.utils.agents import ask_agent, AgentConfig
from aria_tools.utils.models import StudyDiagram, StudyWithDiagram, to_pydantic_model


def create_diagram_function(
    llm_model: str, event_bus: EventBus | None = None
) -> Callable[..., Coroutine[Any, Any, StudyWithDiagram]]:
    """Wrapper function to create a diagram illustrating the workflow for a study.

    Args:
        llm_model (str): The language model to use for generating the diagram.
        event_bus (EventBus | None, optional): An optional event bus for communication.
            Defaults to None.

    Returns:
        Callable: A callable that creates a diagram for a suggested study.
    """

    @schema_function
    async def create_diagram(
        suggested_study: SuggestedStudy = Field(
            description="The suggested study to create a diagram for"
        ),
    ) -> StudyWithDiagram:
        """Create a diagram illustrating the workflow for a study."""
        study_model = to_pydantic_model(SuggestedStudy, suggested_study)
        agent_config = AgentConfig(
            name="Diagrammer",
            instructions=(
                "You are the diagrammer. You create a diagram illustrating the workflow"
                " for the suggested study."
            ),
            messages=[
                "Create a diagram illustrating the workflow for the suggested study:",
                f"`{study_model.experiment_name}`",
                study_model,
            ],
            output_schema=StudyDiagram,
            llm_model=llm_model,
            event_bus=event_bus,
        )
        study_diagram = await ask_agent(agent_config)

        return StudyWithDiagram(
            suggested_study=study_model, study_diagram=study_diagram, template_name=None
        )

    return create_diagram
