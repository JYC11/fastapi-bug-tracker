from pydantic import BaseModel


class Token(BaseModel):
    email: str | None
    user_type: str | None
    admin: str | None
    exp: str
    sub: str
    iat: str
    jti: str
