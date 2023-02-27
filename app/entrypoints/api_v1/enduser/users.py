from fastapi import APIRouter
from starlette import status

router = APIRouter()


@router.post("/user", status_code=status.HTTP_201_CREATED)
def create_user():
    return


@router.put("/user", status_code=status.HTTP_200_OK)
def update_user():
    return


@router.delete("/user", status_code=status.HTTP_200_OK)
def delete_user():
    return


@router.post("/login", status_code=status.HTTP_200_OK)
def login():
    return


@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh():
    return


@router.get("/user/{id}", status_code=status.HTTP_201_CREATED)
def my_user_page():
    return


@router.get("/user/comments", status_code=status.HTTP_201_CREATED)
def my_comments():
    return


@router.get("/user/bugs", status_code=status.HTTP_201_CREATED)
def my_bugs():
    return


@router.get("/user/bugs", status_code=status.HTTP_201_CREATED)
def my_tags():
    return
