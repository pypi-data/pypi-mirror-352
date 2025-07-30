"""Deno service utilities for aria-tools."""

import os
from typing import Any, Dict
from dotenv import load_dotenv
from hypha_rpc.rpc import RemoteService, RemoteException  # type: ignore


async def get_deno_service(server: RemoteService) -> RemoteService:
    """Action function to get deno-app-engine service."""
    deno_service = await server.get_service(
        "hypha-agents/deno-app-engine",
        config={"mode": "random", "timeout": 10.0},
    )
    print(f"Connected to deno-app-engine service: {deno_service.id}")
    return deno_service


def get_registration_code(server: RemoteService, service_id: str) -> str:
    """Return the code to register the aria tools service."""
    print(
        f"Registering aria tools service with ID: {service_id} on server: {server.config.public_base_url}"
    )
    load_dotenv(override=True)
    token = os.environ.get("HYPHA_TOKEN")

    return f"""
import micropip

await micropip.install([
    "hypha-rpc", 
    "aria-tools",
])

from hypha_rpc import connect_to_server
from aria_tools.register_tools import register_tools

async def register_aria_tools_service():
    server = await connect_to_server({{
        "server_url": "{server.config.public_base_url}",
        "workspace": "{server.config.workspace}",
        "token": "{token}"
    }})

    await register_tools(server, "{service_id}")
    await server.serve()

# Run the registration
await register_aria_tools_service()
"""


async def manage_existing_kernel(deno_service: RemoteService, kernel_id: str) -> bool:
    """Manage existing kernel for the service.

    Args:
        deno_service: The deno-app-engine service
        kernel_id: The kernel ID

    Returns:
        True if a kernel was found and managed, False if no existing kernel
    """
    try:
        await deno_service.interruptKernel({"kernelId": kernel_id})
        print(f"Stopped kernel: {kernel_id}")

        return True

    except RemoteException as e:
        print(f"No existing kernel found or error managing kernel: {e}")
        return False


async def create_deno_kernel(
    deno_service: RemoteService, service_id: str
) -> Dict[str, Any]:
    """Create a Deno kernel for the specified service."""
    kernel_info = await deno_service.createKernel(
        {
            "id": f"kernel-{service_id}",
            "mode": "worker",  # Use worker mode for isolation
            "inactivity_timeout": 3600000,  # 1 hour timeout
            "max_execution_time": 300000,  # 5 minutes max execution time
        }
    )
    print(f"Created kernel: {kernel_info}")
    return kernel_info


async def register_deno_service(
    server: RemoteService, deno_service: RemoteService, service_id: str, kernel_id: str
) -> Dict[str, Any]:
    register_code = get_registration_code(server, service_id)

    register_result = await deno_service.executeCode(
        {"kernelId": kernel_id, "code": register_code}
    )

    print(f"Registration execution: {register_result}")

    return register_result


async def destroy_kernel(server: RemoteService, kernel_id: str) -> None:
    """Destroy and exit the Deno service.

    Args:
        server (RemoteService): The Deno service instance.
        kernel_id (str): The ID of the kernel.
    """
    deno_service = await get_deno_service(server)

    result = await deno_service.destroyKernel({"kernelId": kernel_id})

    print(f"Destroyed kernel: {kernel_id} with result: {result['success']}")


async def run_kernel(
    server: RemoteService, service_id: str, kernel_id: str
) -> Dict[str, Any]:
    """Action function to run aria tools service on deno-app-engine."""
    deno_service = await get_deno_service(server)

    kernel_existed = await manage_existing_kernel(deno_service, kernel_id)

    if not kernel_existed:
        await create_deno_kernel(deno_service, service_id)

    register_result = await register_deno_service(
        server, deno_service, service_id, kernel_id
    )

    action_msg = "restarted and set up" if kernel_existed else "created and set up"
    print(f"Aria tools service has been {action_msg} on kernel {kernel_id}")

    return {
        "deno_service": deno_service,
        "kernel_id": kernel_id,
        "register_result": register_result,
        "service_url": f"{server.config.public_base_url}/{server.config.workspace}/services/{service_id}",
        "action": "setup_complete",
    }
