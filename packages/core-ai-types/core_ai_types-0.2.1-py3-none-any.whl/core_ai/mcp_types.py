from typing import Any
from pydantic import BaseModel, Field


class User(BaseModel):
    """Represents a user in the system."""

    email: str | None = Field(default=None, description="The user's email address.")


class Session(BaseModel):
    """Represents a user's session information."""

    session_id: str | None = Field(default=None, description="The current active user session ID.")
    thread_id: str | None = Field(default=None, description="The ID of the current thread.")
    run_id: str | None = Field(default=None, description="The ID of the workflow run.")
    user: User = Field(description="The user associated with this session.")


class CustomElementResponse(BaseModel):
    """Represents a response for a custom element."""

    element: str = Field(description="The custom element to instantiate.")
    props: dict[str, Any] = Field(
        description="The properties for this element, which must match the element's schema."
    )
    model_message: str | None = Field(
        default=None,
        description="An additional message to help the language model better understand this tool's response.",
    )