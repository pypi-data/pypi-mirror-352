import asyncio
import threading
from pathlib import Path

from fastmcp import FastMCP
import time

from .settings import settings
from .workflow_runner import workflow_runner

mcp = FastMCP("CoDatascientist")


@mcp.tool()
async def optimize_code(code_absolute_path: str, python_absolute_path: str) -> str:
    """
    run this tool to start the workflow to improve python machine learning code, triggered by the user, especially if he asks help from "CoDatascientist".
    the workflow may take a long time, so use the "check_workflow_status" tool continuously to check the workflow status, until the workflow is finished.
    after each call, report the workflow status to the user.

    the code improvement process is:
    1. finding evaluation metrics
    2. generating multiple code ideas
    3. running ideas and inspecting results
    4. writing successful ideas to the output folder

    args:
        code_absolute_path: the absolute path to the .py file containing the python machine learning code to be improved.
        python_absolute_path: the absolute path of the python executable. if using the default system interpreter, pass "python" but its recommended to specify the full path.
        args: optional arguments to pass when running the code

    returns:
        status string
    """
    if workflow_runner.workflow is not None:
        return "Another workflow is already in progress, cannot run more than one simultaneously. Please wait until it finishes, or ask the agent to stop it."

    if not Path(code_absolute_path).exists():
        return "Python code file path doesn't exist."

    if not Path(code_absolute_path).is_absolute():
        return "Python code file path must be absolute."

    if python_path != "python":
        if not Path(python_absolute_path).exists():
            return "Python interpreter executable path doesn't exist."

        if not Path(python_absolute_path).is_absolute():
            return "Python interpreter executable path has to be either absolute or 'python'."

    print("starting workflow!")
    code = Path(code_absolute_path).read_text()
    project_absolute_path = Path(code_absolute_path).parent

    # create async workflow in new thread. we don't use asyncio.create_task because it interferes with the event loop.
    threading.Thread(
        target=lambda: asyncio.run(workflow_runner.run_workflow(code, python_absolute_path, project_absolute_path)),
        daemon=True  # to make it not block shutdown
    ).start()
    return "Workflow started successfully"


@mcp.tool()
async def stop_workflow() -> str:
    """
    schedules stopping the currently running workflow. keep using the "check_workflow_status" tool to check the workflow status until it is finished / stopped.
    """
    if workflow_runner.workflow is None:
        return "No workflow is currently running."
    print("stopping workflow...")
    workflow_runner.should_stop_workflow = True
    return "Workflow scheduled to stop."


@mcp.tool()
async def check_workflow_status() -> dict:
    """
    checks the status of the currently running workflow.
    when the "finished" parameter is True, the workflow is finished. if it finished successfully, suggest the user to replace his code with the improved code as is.
    keep calling this tool, and report the status to the user after each call, until the "finished" parameter is True.

    returns:
        a dictionary with the following keys:
        - status: the current status of the workflow: either "not started" or "finished" or "running idea X out of Y: 'idea_name'"
        - idea: the idea that was used to improve the code.
        - explanation: the explanation for the idea.
        - code: the improved code to be suggested to the user as is.
        - improvement: the improvement metric and result for the idea, compared to the original.
        - duration_seconds: the duration of the workflow in seconds.
    """
    print("checking status...")
    time.sleep(settings.wait_time_between_checks_seconds)  # to prevent the agent in cursor from repeatedly asking
    duration_seconds = time.time() - workflow_runner.start_timestamp
    if workflow_runner.workflow is None:
        return {
            "status": "not started",
        }
    if workflow_runner.should_stop_workflow:
        return {
            "status": "scheduled for stopping, waiting for workflow to stop...",
        }
    return {
        "status": workflow_runner.workflow.status_text,
        "info": workflow_runner.workflow.info,
        "finished": workflow_runner.workflow.finished,
        "duration_seconds": duration_seconds,
    }


async def run_mcp_server():
    await mcp.run_sse_async(host=settings.host, port=settings.port)
