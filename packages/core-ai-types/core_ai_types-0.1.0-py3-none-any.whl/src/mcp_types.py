from pydantic import BaseModel


class User(BaseModel):
    email: str | None = None


class Session(BaseModel):
    session_id: str | None = None
    thread_id: str | None = None
    run_id: str | None = None
    user: User
