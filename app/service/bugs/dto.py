from pydantic import BaseModel


class BugIn(BaseModel):
    ...


class BugUpdateIn(BaseModel):
    ...


class BugOut(BaseModel):
    ...


class CommentIn(BaseModel):
    ...


class CommentUpdateIn(BaseModel):
    ...


class CommentOut(BaseModel):
    ...
