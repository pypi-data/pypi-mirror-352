import httpx
from pydantic import BaseModel

from .models import Workflow, CodeVersion, SystemInfo, Prompt, CodeResult
from .settings import settings


class CoDatascientistBackendResponse(BaseModel):
    workflow: Workflow
    code_to_run: CodeVersion | None = None


async def test_connection() -> str:
    return await _call_co_datascientist_client("/test_connection", {})


async def start_workflow(code: str, system_info: SystemInfo) -> CoDatascientistBackendResponse:
    response = await _call_co_datascientist_client("/start_workflow", {
        "prompt": Prompt(code=code).model_dump(),
        "system_info": system_info.model_dump()
    })
    return CoDatascientistBackendResponse.model_validate(response)


async def finished_running_code(workflow_id, code_version_id, result: CodeResult) -> CoDatascientistBackendResponse:
    response = await _call_co_datascientist_client(
        "/finished_running_code",
        {"workflow_id": workflow_id, "code_version_id": code_version_id, "result": result.model_dump()})
    return CoDatascientistBackendResponse.model_validate(response)


async def stop_workflow(workflow_id) -> None:
    await _call_co_datascientist_client("/stop_workflow", {"workflow_id": workflow_id})


async def _call_co_datascientist_client(path, data):
    response = httpx.post(
        settings.co_datascientist_backend_url + path,
        headers={"Authorization": f"Bearer {settings.api_key.get_secret_value()}"},
        json=data,
        timeout=None)
    response.raise_for_status()
    return response.json()

