"""Action functions for aria-tools."""

import sys
import subprocess
import asyncio
from argparse import Namespace
from websockets.exceptions import InvalidURI
from hypha_rpc.rpc import RemoteException, RemoteService  # type: ignore

from aria_tools.register_tools import register_tools
from aria_tools.server_utils import connect_to_hypha_server
from aria_tools.deno_utils import run_kernel, destroy_kernel


async def register_to_existing_server(
    provided_url: str, port: int | None, service_id: str
) -> RemoteService:
    """Register to an existing server with aria tools service."""
    server = await connect_to_hypha_server(provided_url, port)

    await register_tools(server, service_id)

    return server


async def run_local_server(
    server_url: str, port: int, service_id_existing_server: str
) -> None:
    """Run the local server with the provided arguments.

    Args:
        server_url (str): The URL of the server to connect to.
        port (int): The port of the server.
        service_id_existing_server (str): The ID of the service.
    """
    try:
        await register_to_existing_server(
            server_url, port=port, service_id=service_id_existing_server
        )
    except (ConnectionRefusedError, InvalidURI, RemoteException):
        command = [
            sys.executable,
            "-m",
            "hypha.server",
            f"--host={server_url}",
            f"--port={port}",
            "--startup-functions=aria_tools.register_tools:register_tools",
        ]
        subprocess.run(command, check=True)


async def execute_deno_action(
    server_url: str, port: int, service_id: str, destroy: bool = False
) -> None:
    """Execute the Deno action based on the provided arguments.

    Args:
        server_url (str): The URL of the server.
        port (int): The port of the server.
        service_id (str): The ID of the service.
        destroy (bool): Whether to destroy the kernel or not.
    """
    server = await connect_to_hypha_server(server_url, port)
    kernel_id = f"kernel-{service_id}"

    if destroy:
        await destroy_kernel(server, kernel_id)
    else:
        result = await run_kernel(
            server=server,
            service_id=service_id,
            kernel_id=kernel_id,
        )
        print(result["register_result"])


def run_on_deno(args: Namespace) -> None:
    """Connect to the deno-app-engine service and run aria tools service on it."""

    asyncio.run(
        execute_deno_action(
            server_url=args.server_url,
            port=args.port,
            service_id=args.service_id,
            destroy=args.destroy,
        )
    )


def connect_to_remote(args: Namespace) -> None:
    """Connect to remote server and register aria tools service."""
    asyncio.run(
        register_to_existing_server(args.server_url, args.port, args.service_id)
    )


def run_locally(args: Namespace) -> None:
    """Run the local server with the provided arguments.

    Args:
        args (Namespace): The arguments parsed from the command line.
    """
    asyncio.run(
        run_local_server(args.server_url, args.port, args.service_id_existing_server)
    )
