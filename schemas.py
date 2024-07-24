from pydantic import BaseModel
from pydantic import ConfigDict


class UserCreate(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: str
    username: str
    password: str
    model_config = ConfigDict(coerce_numbers_to_str=True)


class TaskValidator(BaseModel):
    name: str
    description: str


class TaskDeletion(BaseModel):
    id: int


class SubtaskCreate(BaseModel):
    description: str
    base_task_id: int


class SubtaskDelete(BaseModel):
    subtask_id: int
    base_task_id: int
