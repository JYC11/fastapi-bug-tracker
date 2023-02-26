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


@router.get("/users", status_code=status.HTTP_200_OK)
def get_users():
    return


@router.get("/user/{id}", status_code=status.HTTP_200_OK)
def get_user():
    return
