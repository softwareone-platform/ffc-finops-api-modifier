from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr


class CreateUserData(BaseModel):
    email: EmailStr
    display_name: str
    password: str


class CreateUserResponse(BaseModel):
    id: str
    display_name: str
    is_active: bool
    type_id: int
    email: EmailStr
    scope_id: str | None
    slack_connected: bool
    is_password_autogenerated: bool
    jira_connected: bool
    token: str
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "created_at": 1730126521,
                    "deleted_at": 0,
                    "id": "f0bd0c4a-7c55-45b7-8b58-27740e38789a",
                    "display_name": "Spider Man",
                    "is_active": True,
                    "type_id": 1,
                    "email": "peter.parker@iamspiderman.com",
                    "scope_id": None,
                    "slack_connected": False,
                    "is_password_autogenerated": False,
                    "jira_connected": False,
                    "token": "JTW_TOKEN",
                }
            ]
        }
    )
