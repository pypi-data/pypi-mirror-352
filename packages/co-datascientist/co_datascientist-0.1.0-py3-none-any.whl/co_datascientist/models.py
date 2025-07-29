from __future__ import annotations
import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# TODO: import only the models from the engine library

class Workflow(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    finished: bool = False
    status_text: str  # running idea 4 out of 10: add_more_generations. graph in the info
    info: dict = Field(default_factory=dict)  # a free dict which is sent to the agent
    baseline_code: CodeVersion | None = None
    code_versions: list[CodeVersion] = Field(default_factory=list)


class CodeVersion(BaseModel):
    code_version_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # baseline / more_generations / try_blah_blah
    idea: str
    info: dict = Field(
        default_factory=dict)  # a free dict which is sent to the agent, should contain descriptions and other info
    code: str
    result: CodeResult | None = None
    is_final: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


class CodeResult(BaseModel):
    runtime_ms: float = 0
    return_code: int
    stdout: str | None = None
    stderr: str | None = None



class EngineType(str, Enum):
    MOCK = 'MOCK'
    CO_DATASCIENTIST = 'CO_DATASCIENTIST'


class SystemInfo(BaseModel):
    python_libraries: list[str] = Field(default_factory=list)
    python_version: str
    os: str = ""


class Prompt(BaseModel):
    code: str
