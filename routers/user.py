from sys import prefix

from fastapi import APIRouter

router = APIRouter(tags=["user"], prefix="/user")

@router.get("/")
async def get_all_users():
    return {"message": "All found users"}

@router.get("/{user_id}")
async def get_user(user_id: int):
    return {"message": f"User with id {user_id} found"}

@router.get("/name/{username}")
async def get_user_by_name(username: str):
    return {"message": f"User with name {username} found"}

@router.post("/create")
async def create_user():
    return {"message": "User created"}

@router.patch("/update/{user_id}")
async def update_user(user_id: int):
    return {"message": f"User with id {user_id} updated"}

@router.delete("/delete/{user_id}")
async def delete_user(user_id: int):
    return {"message": f"User with id {user_id} deleted"}