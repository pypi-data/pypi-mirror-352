import asyncio
import logging
from pathlib import Path

import click

from co_datascientist.workflow_runner import workflow_runner
from . import co_datascientist_api, mcp_local_server
from .settings import settings

logging.basicConfig(level=settings.log_level)
logging.info(f"settings: {settings.model_dump()}")


@click.group()
@click.option('--reset-token', is_flag=True, help='Reset the API token')
def main(reset_token: bool):
    """Welcome to CoDatascientist CLI!"""
    print("Welcome to CoDatascientist CLI!")
    if reset_token:
        settings.delete_api_key()
    settings.get_api_key()

    try:
        print(f"connecting to co-datascientist server...")
        response = asyncio.run(co_datascientist_api.test_connection())
        print(f"server: {response}")
    except Exception as e:
        print(f"error from server: {e}")
        print("make sure that your token is correct, your can remove and reset the token using --reset-token flag.")
        exit(1)


@main.command()
def mcp_server():
    """Start the MCP server which allows agents to use CoDatascientist"""
    print("starting MCP server... Press Ctrl+C to exit.")
    asyncio.run(mcp_local_server.run_mcp_server())


@main.command()
@click.option('--script-path', required=True, type=click.Path(), help='Path to the python code to process, must be absolute path')
@click.option('--python-path', required=True, type=click.Path(), default="python", show_default=True,
              help='Path to the python interpreter to use')
def run(script_path, python_path):
    """Process a file"""
    print(f"Processing file: {script_path} with python interpreter executable: {python_path}")
    if not Path(script_path).exists():
        print("Python code file path doesn't exist.")
        return

    if not Path(script_path).is_absolute():
        print("Python code file path must be absolute.")
        return

    if python_path != "python":
        if not Path(python_path).exists():
            print("Python interpreter executable path doesn't exist.")
            return

        if not Path(python_path).is_absolute():
            print("Python interpreter executable path has to be either absolute or 'python'.")
            return

    code = Path(script_path).read_text()
    project_path = Path(script_path).parent
    asyncio.run(workflow_runner.run_workflow(code, python_path, project_path))


if __name__ == "__main__":
    main()
