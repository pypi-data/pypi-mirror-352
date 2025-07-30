"""Main entry point for the Aria tools package."""

import argparse
from dotenv import load_dotenv
from aria_tools.constants import (
    DEFAULT_SERVICE_ID,
    DEFAULT_LOCAL_HOST,
    DEFAULT_LOCAL_PORT,
    DEFAULT_REMOTE_URL,
)
from aria_tools.actions import connect_to_remote, run_on_deno, run_locally

load_dotenv()


def main():
    """Main entry point for aria-tools commands."""
    parser = argparse.ArgumentParser(description="Aria tools launch commands.")

    subparsers = parser.add_subparsers()

    # Local server parser
    parser_local = subparsers.add_parser("local")
    parser_local.add_argument("--server-url", type=str, default=DEFAULT_LOCAL_HOST)
    parser_local.add_argument("--port", type=int, default=DEFAULT_LOCAL_PORT)
    parser_local.add_argument(
        "--service-id-existing-server",
        type=str,
        default=DEFAULT_SERVICE_ID,
    )
    parser_local.set_defaults(func=run_locally)

    # Remote server parser
    parser_remote = subparsers.add_parser("remote")
    parser_remote.add_argument("--server-url", type=str, default=DEFAULT_REMOTE_URL)
    parser_remote.add_argument(
        "--port", type=int, help="Port number for the server connection"
    )
    parser_remote.add_argument(
        "--service-id",
        type=str,
        default=DEFAULT_SERVICE_ID,
    )
    parser_remote.set_defaults(func=connect_to_remote)

    # Deno server parser
    parser_deno = subparsers.add_parser("deno")
    parser_deno.add_argument("--server-url", type=str, default=DEFAULT_REMOTE_URL)
    parser_deno.add_argument(
        "--port", type=int, help="Port number for the server connection"
    )
    parser_deno.add_argument(
        "--service-id",
        type=str,
        default=DEFAULT_SERVICE_ID,
        help="Service ID for the aria tools service",
    )
    parser_deno.add_argument(
        "--destroy",
        action="store_true",
        help="Destroy existing kernel completely without starting a new server",
    )
    parser_deno.set_defaults(func=run_on_deno)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
