from typing import TypedDict


class Task(TypedDict):
    id: int


class TaskWithToken(Task):
    token: str
