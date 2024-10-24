from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user

from auth.auth import is_admin
from services.db_service import get_db
from models import Target, User
from schemas import TargetRequest, TargetResponse
from helpers.exceptions import http_exception_not_found, http_exception_forbidden
from auth import get_current_user

router = APIRouter(tags=["target"], prefix="")


@router.get("/users/targets", response_model=list[TargetResponse])
async def get_all_targets(db: Annotated[Session, Depends(get_db)]):
    db_targets = db.query(Target).all()
    return db_targets


@router.get("/users/me/targets", response_model=list[TargetResponse])
def get_my_targets(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user.targets


@router.get("/users/targets/name/{target_name}", response_model=TargetResponse)
async def get_target_by_name(target_name: str, db: Annotated[Session, Depends(get_db)]):
    db_target = db.query(Target).filter(Target.title == target_name).first()
    if not db_target:
        raise http_exception_not_found(f"Target with name {target_name} not found")

    return db_target


@router.get("/users/{user_id}/targets", response_model=list[TargetResponse])
def get_all_user_targets(user_id: int, db: Annotated[Session, Depends(get_db)]):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise http_exception_not_found(f"User with id {user_id} not found")
    return db_user.targets


@router.get("/users/{user_id}/targets/{target_id}", response_model=TargetResponse)
async def get_user_target(user_id: int, target_id: int, db: Annotated[Session, Depends(get_db)]):
    db_user: User = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise http_exception_not_found(f"User with id {user_id} not found")
    db_target = db.query(Target).filter(Target.id == target_id).first()
    if not db_target:
        raise http_exception_not_found(f"Target with id {target_id} not found")

    return db_target


@router.post("/users/{user_id}/targets/create", response_model=TargetResponse)
async def create_target(
        user_id: int,
        request: TargetRequest,
        db: Annotated[Session,
        Depends(get_db)],
        current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.id != user_id and not is_admin(current_user):
        raise http_exception_forbidden()

    db_new_target = Target(**request.model_dump(), user_id=user_id)
    db.add(db_new_target)
    db.commit()
    return db_new_target




@router.patch("/users/{user_id}/targets/update/{target_id}", response_model=TargetResponse)
async def update_target(
        user_id: int,
        target_id: int, request: TargetRequest,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    db_user: User = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise http_exception_not_found(f"User with id {user_id} not found")
    if current_user.id != user_id and not is_admin(current_user):
        raise http_exception_forbidden()

    db_target: Target = db.query(Target).filter(Target.id == target_id).first()
    if not db_target:
        raise http_exception_not_found(f"Target with id {target_id} not found")
    if db_target.user_id != user_id:
        raise http_exception_forbidden("Forbidden this target doesn't belong to this user")

    new_data_for_db_target = request.model_dump()
    for key, value in new_data_for_db_target.items():
        setattr(db_target, key, value)
    db.commit()
    db.refresh(db_target)
    return db_target


@router.delete("/users/{user_id}/targets/delete/{target_id}")
async def delete_target(user_id: int, target_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    db_user: User = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise http_exception_not_found(f"User with id {user_id} not found")
    if current_user.id != user_id and not is_admin(current_user):
        raise http_exception_forbidden()

    db_target: Target = db.query(Target).filter(Target.id == target_id).first()
    if not db_target:
        raise http_exception_not_found(f"Target with id {target_id} not found")
    if db_target.user_id != user_id:
        raise http_exception_forbidden("Forbidden this target doesn't belong to this user")

    db.delete(db_target)
    db.commit()
    return {"message": f"Target with id {target_id} deleted"}
