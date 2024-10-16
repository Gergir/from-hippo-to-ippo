from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import Hash, get_current_user
from auth.auth import is_admin
from services.db_service import get_db
from models import User
from schemas import UserRequest, UserResponse
from helpers.exceptions import http_exception_not_found, http_exception_conflict, http_exception_forbidden

router = APIRouter(tags=["user"], prefix="/users")


@router.get("/", response_model=list[UserResponse])
async def get_all_users(db: Annotated[Session, Depends(get_db)]):
    db_users = db.query(User).all()
    return db_users


@router.get("/me", response_model=UserResponse)
async def get_my_user(current_user: Annotated[User, Depends(get_current_user)]):
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
    db_user = db.query(User).filter(User.username == request.username).first()
    if db_user:
        raise http_exception_conflict("User with this username already exists")
    db_user = db.query(User).filter(User.email == request.email).first()
    if db_user:
        raise http_exception_conflict("User with this email already exists")

    request.password = Hash.bcrypt(request.password)
    db_new_user = User(**request.model_dump())
    db.add(db_new_user)
    db.commit()
    return db_new_user


@router.patch("/update/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int, request: UserRequest,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    db_user: User = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise http_exception_not_found(f"User with id {user_id} not found")
    if db_user.id != current_user.id and not is_admin(current_user):
        raise http_exception_forbidden()

    if db.query(User).filter(User.username == request.username).first() and db_user.username != request.username:
        raise http_exception_conflict("User with this username already exists")
    if db.query(User).filter(User.email == request.email).first() and db_user.email != request.email:
        raise http_exception_conflict("User with this email already exists")

    request.password = Hash.bcrypt(request.password)
    new_data_for_db_user = request.model_dump(exclude_unset=True)
    for key, value in new_data_for_db_user.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/delete/{user_id}")
async def delete_user(
        user_id: int,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User,
        Depends(get_current_user)]
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise http_exception_not_found(f"User with id {user_id} not found")
    if db_user.id != current_user.id and not is_admin(current_user):
        raise http_exception_forbidden()

    db.delete(db_user)
    db.commit()
    return {"message": f"User {user_id} deleted."}
