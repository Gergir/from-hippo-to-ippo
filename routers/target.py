from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.auth import is_admin
from helpers.queries import find_target
from services.db_service import get_db
from models import Target, User
from schemas import TargetRequest, TargetRequestUpdate, TargetResponse
from helpers import exceptions, queries
from auth import get_current_user

router = APIRouter(tags=["target"])


@router.get("/users/targets", response_model=list[TargetResponse])
async def get_all_targets(db: Annotated[Session, Depends(get_db)]):
    db_targets = queries.find_all_targets(db)
    return db_targets


@router.get("/users/me/targets", response_model=list[TargetResponse])
def get_my_targets(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    db_targets = queries.find_all_targets(db, current_user.id)
    return db_targets


@router.get("/users/targets/name/{target_name}", response_model=TargetResponse)
async def get_target_by_name(target_name: str, db: Annotated[Session, Depends(get_db)]):
    db_target = queries.find_target_by_name(db, target_name)
    if not db_target:
        raise exceptions.http_exception_not_found(f"Target with name {target_name} not found")
    return db_target


@router.get("/users/{user_id}/targets", response_model=list[TargetResponse])
def get_all_user_targets(user_id: int, db: Annotated[Session, Depends(get_db)]):
    db_user = queries.find_user(db, user_id)
    if not db_user:
        raise exceptions.http_exception_not_found(f"User with id {user_id} not found")
    return db_user.targets


@router.get("/users/{user_id}/targets/{target_id}", response_model=TargetResponse)
async def get_user_target(user_id: int, target_id: int, db: Annotated[Session, Depends(get_db)]):
    db_target = find_target(db, target_id, user_id)
    if not db_target:
        raise exceptions.http_exception_not_found(f"Target with {target_id} for user {user_id} not found")
    return db_target


@router.post("/users/{user_id}/targets", response_model=TargetResponse)
async def create_target(
        user_id: int,
        request: TargetRequest,
        db: Annotated[Session,
        Depends(get_db)],
        current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.id != user_id and not is_admin(current_user):
        raise exceptions.http_exception_forbidden()

    db_new_target = Target(**request.model_dump(), user_id=user_id)
    db.add(db_new_target)
    db.commit()
    return db_new_target


@router.patch("/users/{user_id}/targets/{target_id}", response_model=TargetResponse)
async def update_target(
        user_id: int,
        target_id: int,
        request: TargetRequestUpdate,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.id != user_id and not is_admin(current_user):
        raise exceptions.http_exception_forbidden()
    db_target = find_target(db, target_id, user_id)
    if not db_target:
        raise exceptions.http_exception_not_found(f"Target with id {target_id} for user {user_id} not found")

    new_data_for_db_target = request.model_dump(exclude_unset=True)
    for key, value in new_data_for_db_target.items():
        setattr(db_target, key, value)
    db.commit()
    db.refresh(db_target)
    return db_target


@router.delete("/users/{user_id}/targets/{target_id}")
async def delete_target(
        user_id: int, target_id: int,
        db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.id != user_id and not is_admin(current_user):
        raise exceptions.http_exception_forbidden()
    db_target = find_target(db, target_id, user_id)
    if not db_target:
        raise exceptions.http_exception_not_found(f"Target with id {target_id} for user {user_id} not found")

    db.delete(db_target)
    db.commit()
    return {"message": f"Target with id {target_id} deleted successfully"}
