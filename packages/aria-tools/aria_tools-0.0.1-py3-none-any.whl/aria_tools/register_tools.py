"""Register Aria tools service to Hypha."""

import importlib.metadata
from typing import Any
from hypha_rpc.rpc import RemoteService, RemoteException  # type: ignore
from aria_tools.utils.io import load_config
from aria_tools.tools import (
    create_study_suggester_function,
    create_make_html_page,
    create_diagram_function,
    create_protocol_feedback_function,
    create_write_protocol,
    create_protocol_update_function,
    check_pubmed_hits,
    query_pubmed,
    create_best_pubmed_query_tool,
    parse_isa_data,
)


async def add_probes(server: RemoteService):
    """Add probes to the Aria tools service.
    Args:
        server (RemoteService): The server instance to register the probes with.
    """

    async def is_available(service_id: str) -> bool:
        try:
            svc = await server.get_service(service_id)  # type: ignore
            return svc is not None
        except RemoteException:
            return False

    async def is_alive() -> dict[str, str]:
        if await is_available("aria-tools"):
            return {"status": "ok", "message": "All services are available"}

        raise RuntimeError("Aria tools service is not available.")

    await server.register_service(  # type: ignore
        {
            "name": "Aria Tools Probes",
            "id": "aria-tools-probes",
            "config": {"visibility": "public"},
            "type": "probes",
            "readiness": is_alive,
            "liveness": is_alive,
        }
    )


def get_tools() -> dict[str, Any]:
    """Get the tools for the Aria study automation service.

    Returns:
        dict: A dictionary of tools for the Aria study automation service.
    """
    config = load_config()
    llm_model = config["llm_model"]

    return {
        "study_suggester": create_study_suggester_function(llm_model),
        "make_html": create_make_html_page(llm_model),
        "create_diagram": create_diagram_function(llm_model),
        "protocol_feedback": create_protocol_feedback_function(llm_model),
        "write_protocol": create_write_protocol(llm_model),
        "update_protocol": create_protocol_update_function(llm_model),
        "check_pubmed_hits": check_pubmed_hits,
        "get_best_pubmed_query": create_best_pubmed_query_tool(llm_model),
        "query_pubmed": query_pubmed,
        "parse_isa": parse_isa_data,
    }


async def register_tools(server: RemoteService, service_id: str):
    """Register Aria tools service to Hypha.

    Args:
        server (RemoteService): The server instance to register the tools with.
    """
    tools = get_tools()
    version = importlib.metadata.version("aria_tools")
    await server.register_service(  # type: ignore
        {
            "name": "Aria study tools",
            "id": service_id,
            "config": {"visibility": "public"},
            "version": version,
            **tools,
        }
    )

    await add_probes(server)

    url_string = (
        f"{server.config.public_base_url}/"  # type: ignore
        f"{server.config.workspace}/"  # type: ignore
        f"services/{service_id}"
    )
    print("Aria study tools available at:", url_string)
