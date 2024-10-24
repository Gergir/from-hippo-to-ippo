from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.db_service import get_db
from models import Role, User
from schemas import RoleRequest, RoleResponse
from auth import get_current_admin_user
from helpers.exceptions import http_exception_not_found

router = APIRouter(prefix="/roles", tags=["role"])

@router.get("/", response_model=list[RoleResponse])
async def get_roles(
        db: Annotated[Session, Depends(get_db)],
        current_admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    db_roles = db.query(Role).all()
    return db_roles

@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
        role_id: int,
        db: Annotated[Session, Depends(get_db)],
        current_admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role:
        raise http_exception_not_found(f"Role with id {role_id} not found")
    return db_role


@router.get("/name/{role_type}", response_model=RoleResponse)
async def get_role_by_name(
        role_type: str,
        db: Annotated[Session, Depends(get_db)],
        current_admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    db_role = db.query(Role).filter(Role.role_type == role_type).first()
    if not db_role:
        raise http_exception_not_found(f"Role with role type {role_type} not found")
    return db_role

@router.post("/create", response_model=RoleResponse)
async def create_role(
        request: RoleRequest,
        db: Annotated[Session, Depends(get_db)],
        current_admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    db_new_role = Role(**request.model_dump())
    db.add(db_new_role)
    db.commit()
    return db_new_role


@router.patch("/update/{role_id}", response_model=RoleResponse)
async def update_role(
        role_id: int,
        request: RoleRequest, db: Annotated[Session, Depends(get_db)],
        current_admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role:
        raise http_exception_not_found(f"Role with id {role_id} not found")
    new_data_for_db_role = request.model_dump(exclude_unset=True)
    for key, value in new_data_for_db_role.items():
        setattr(db_role, key, value)

    db.commit()
    db.refresh(db_role)
    return db_role

@router.delete("/delete/{role_id}")
async def delete_role(
        role_id: int,
        db: Annotated[Session, Depends(get_db)],
        current_admin_user: Annotated[User, Depends(get_current_admin_user)]
):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role:
        raise http_exception_not_found(f"Role with id {role_id} not found")
    role_type = db_role.role_type

    db.delete(db_role)
    db.commit()
    return {"message": f"Role type {role_type} with id {role_id} deleted"}