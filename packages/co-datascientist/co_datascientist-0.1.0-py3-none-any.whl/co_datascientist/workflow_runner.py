import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from .models import Workflow, SystemInfo, CodeResult
from . import co_datascientist_api

OUTPUT_FOLDER = "co_datascientist_output"


class _WorkflowRunner:
    def __init__(self):
        self.workflow: Workflow | None = None
        self.start_timestamp = 0
        self.should_stop_workflow = False

    async def run_workflow(self, code: str, python_path: str, project_absolute_path: str):
        try:
            print("Starting workflow")
            _create_output_folder(project_absolute_path)
            self.start_timestamp = time.time()
            self.should_stop_workflow = False
            self.workflow = Workflow(status_text="Workflow started", user_id="")

            system_info = get_system_info(python_path)
            logging.info(f"user system info: {system_info}")
            response = await co_datascientist_api.start_workflow(code, system_info)
            self.workflow = response.workflow
            print(f" - workflow status: {self.workflow.status_text}")
            while not self.workflow.finished and response.code_to_run is not None and not self.should_stop_workflow:
                print(
                    f" - evaluating code version '{response.code_to_run.name}' for idea '{response.code_to_run.idea}'...")
                result = _run_python_code(response.code_to_run.code, python_path)

                print(
                    f" - finished evaluating '{response.code_to_run.name}' for idea '{response.code_to_run.idea}', status: {self.workflow.status_text}")
                response = await co_datascientist_api.finished_running_code(self.workflow.workflow_id,
                                                                            response.code_to_run.code_version_id,
                                                                            result)
                self.workflow = response.workflow
                print(f" - workflow status: {self.workflow.status_text}")
                _update_output_folder(response.workflow, project_absolute_path)

            if self.should_stop_workflow:
                await co_datascientist_api.stop_workflow(self.workflow.workflow_id)
                print(f"workflow stopped.")
            else:
                print(f"workflow finished!")
        except Exception as e:
            if self.workflow is not None:
                self.workflow.finished = True
                self.workflow.status_text = f"An error occurred while running workflow: {str(e)}"
            logging.exception("An error occurred while running workflow")


def _make_filesystem_safe(name):
    return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", '_', name)


def _create_output_folder(project_absolute_path: str) -> None:
    output_path = Path(project_absolute_path) / OUTPUT_FOLDER
    output_path.mkdir(parents=True, exist_ok=True)


def _update_output_folder(workflow: Workflow, project_absolute_path: str) -> None:
    for code_version in workflow.code_versions:
        folder_name = _make_filesystem_safe(code_version.idea)
        timestamp = code_version.timestamp.strftime("%Y_%m_%d__%H_%M_%S")
        python_file_name = _make_filesystem_safe(f"{timestamp}_{code_version.name}.py")
        info_file_name = _make_filesystem_safe(f"{timestamp}_{code_version.name}_info.json")
        result_file_name = _make_filesystem_safe(f"{timestamp}_{code_version.name}_result.json")
        folder_path = Path(project_absolute_path) / OUTPUT_FOLDER / folder_name
        python_file_path = folder_path / python_file_name
        info_file_path = folder_path / info_file_name
        result_file_path = folder_path / result_file_name

        folder_path.mkdir(parents=True, exist_ok=True)
        if not python_file_path.exists():
            python_file_path.write_text(code_version.code)
        if not info_file_path.exists():
            info_file_path.write_text(json.dumps(code_version.info, indent=4) + "\n")
        if not result_file_path.exists():
            result_file_path.write_text(json.dumps(code_version.info, indent=4) + "\n")


def _run_python_code(code: str, python_path: str, args: str | None = None) -> CodeResult:
    start_time = time.time()
    # write the code to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(code.encode('utf-8'))
        temp_file_path = temp_file.name

    command = f"{python_path} {temp_file_path}"
    if args:
        command += " " + args

    # run the command
    logging.info("running command: " + command)
    output = subprocess.run(command,
                            capture_output=True,
                            text=True,
                            input="",  # prevents it from blocking on stdin
                            timeout=300)  # TODO: change the timeout!
    return_code = output.returncode
    out = output.stdout
    err = output.stderr
    if isinstance(out, str) and out.strip() == "":
        out = None
    if isinstance(err, str) and err.strip() == "":
        err = None

    logging.info("stdout: " + str(out))
    logging.info("stderr: " + str(err))

    # delete the temporary file
    os.remove(temp_file_path)
    runtime_ms = int((time.time() - start_time) * 1000)
    return CodeResult(stdout=out, stderr=err, return_code=return_code, runtime_ms=runtime_ms)


def get_system_info(python_path: str) -> SystemInfo:
    return SystemInfo(
        python_libraries=_get_python_libraries(python_path),
        python_version=_get_python_version(python_path),
        os=sys.platform
    )


def _get_python_libraries(python_path: str) -> list[str]:
    installed_libraries = subprocess.check_output(
        [python_path, "-m", "pip", "freeze"],
        universal_newlines=True
    ).strip()
    return [lib.strip() for lib in installed_libraries.split("\n")]


def _get_python_version(python_path: str) -> str:
    return subprocess.check_output(
        [python_path, "--version"],
        universal_newlines=True
    ).strip()


workflow_runner = _WorkflowRunner()
