from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from services.db_service import get_db
from models import Role, User
from schemas import RoleRequest, RoleResponse
from auth import get_current_admin_user
from helpers import exceptions, queries

router = APIRouter(tags=["role"], prefix="/roles")


@router.get("/", response_model=list[RoleResponse])
async def get_roles(
        db: Annotated[Session, Depends(get_db)],
        current_admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    db_roles = queries.find_all_roles(db)
    return db_roles


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
        role_id: int,
        db: Annotated[Session, Depends(get_db)],
        current_admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    db_role = queries.find_role(db, role_id)
    if not db_role:
        raise exceptions.http_exception_not_found(f"Role with id {role_id} not found")
    return db_role


@router.get("/name/{role_type}", response_model=RoleResponse)
async def get_role_by_name(
        role_type: str,
        db: Annotated[Session, Depends(get_db)],
        current_admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    db_role = queries.find_role_by_name(db, role_type)
    if not db_role:
        raise exceptions.http_exception_not_found(f"Role with role type {role_type} not found")
    return db_role


@router.post("/", response_model=RoleResponse)
async def create_role(
        request: RoleRequest,
        db: Annotated[Session, Depends(get_db)],
        current_admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    db_role = queries.find_role_by_name(db, request.role_type.value)
    if db_role:
        raise exceptions.http_exception_conflict(f"Role with role type {request.role_type.value} already exists")

    db_new_role = Role(**request.model_dump())
    db.add(db_new_role)
    db.commit()
    return db_new_role


@router.patch("/{role_id}", response_model=RoleResponse)
async def update_role(
        role_id: int,
        request: RoleRequest, db: Annotated[Session, Depends(get_db)],
        current_admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    db_role = queries.find_role(db, role_id)
    if not db_role:
        raise exceptions.http_exception_not_found(f"Role with id {role_id} not found")

    new_data_for_db_role = request.model_dump(exclude_unset=True)
    for key, value in new_data_for_db_role.items():
        setattr(db_role, key, value)

    db.commit()
    db.refresh(db_role)
    return db_role


@router.delete("/{role_id}")
async def delete_role(
        role_id: int,
        db: Annotated[Session, Depends(get_db)],
        current_admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    db_role = queries.find_role(db, role_id)
    if not db_role:
        raise exceptions.http_exception_not_found(f"Role with id {role_id} not found")

    db.delete(db_role)
    db.commit()
    return {"message": f"Role type {db_role.role_type} with id {role_id} deleted"}
