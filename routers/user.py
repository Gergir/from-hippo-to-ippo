from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from auth import Hash, oauth2_scheme, get_current_user
from services.db_service import get_db
from models import User
from schemas import UserRequest, UserResponse
from helpers.exceptions import http_exception_not_found

router = APIRouter(tags=["user"], prefix="/users")


@router.get("/", response_model=list[UserResponse])
async def get_all_users(db: Annotated[Session, Depends(get_db)]):
    db_users = db.query(User).all()
    return db_users


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise http_exception_not_found(f"User with id {user_id} not found")

    return db_user




@router.get("/name/{username}", response_model=UserResponse)
async def get_user_by_name(username: str, db: Annotated[Session, Depends(get_db)]):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise http_exception_not_found(f"User with username {username} not found")

    return db_user


@router.post("/create", response_model=UserResponse)
async def create_user(request: UserRequest, db: Annotated[Session, Depends(get_db)]):
    request.password = Hash.bcrypt(request.password)
    db_new_user = User(**request.model_dump())
    db.add(db_new_user)
    db.commit()
    return db_new_user


@router.patch("/update/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int, request: UserRequest,
        db: Annotated[Session, Depends(get_db)],
        token: Annotated[str, Depends(oauth2_scheme)]
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise http_exception_not_found(f"User with id {user_id} not found")

    request.password = Hash.bcrypt(request.password)
    new_data_for_db_user = request.model_dump(exclude_unset=True)
    for key, value in new_data_for_db_user.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/delete/{user_id}")
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise http_exception_not_found(f"User with id {user_id} not found")

    db.delete(db_user)
    db.commit()
    return {"message": f"User {user_id} deleted."}
