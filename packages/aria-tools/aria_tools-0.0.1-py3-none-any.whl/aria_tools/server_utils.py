"""Server connection utilities for aria-tools."""

import os
from hypha_rpc import connect_to_server  # type: ignore
from hypha_rpc.rpc import RemoteService  # type: ignore
from pydantic import BaseModel
from dotenv import load_dotenv


async def connect_to_hypha_server(
    provided_url: str, port: int | None = None
) -> RemoteService:
    """Generic function to connect to server and execute an action.

    Args:
        provided_url (str): The URL of the server to connect to.
        port (int, optional): The port of the server. Defaults to None.
        action_func: The function to execute after connecting to the server.
        **kwargs: Additional arguments to pass to the action function.
    """
    server_url = provided_url if port is None else f"{provided_url}:{port}"
    load_dotenv(override=True)
    token = os.environ.get("HYPHA_TOKEN")
    assert token is not None, "HYPHA_TOKEN environment variable is not set"
    server: RemoteService = await connect_to_server(  # type: ignore
        {"server_url": server_url, "token": token}
    )

    if not isinstance(server, RemoteService):
        raise ValueError("Server is not a RemoteService instance.")

    # Register pydantic codec
    server.register_codec(  # type: ignore
        {
            "name": "pydantic-model",
            "type": BaseModel,
            "encoder": lambda x: x.model_dump(),  # type: ignore
        }
    )

    return server
