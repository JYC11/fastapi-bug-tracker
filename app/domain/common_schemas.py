from pydantic import BaseModel


class LoginRequest(BaseModel):
    grant_type: str = "password"
    username: str
    password: str
    scope: str = ""
    client_id: str | None
    client_secret: str | None


class RefreshRequest(BaseModel):
    grant_type: str
    refresh_token: str
