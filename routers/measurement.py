from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user

from auth.auth import is_admin
from helpers.queries import find_all_measurements, find_measurement, find_target
from services.db_service import get_db
from models import Measurement, Target, User
from schemas import MeasurementRequest, MeasurementResponse
from auth import get_current_user
from helpers import exceptions, queries

router = APIRouter(tags=["measurement"], prefix="")


@router.get("/users/targets/measurements", response_model=list[MeasurementResponse])
async def get_all_measurements(db: Annotated[Session, Depends(get_db)]):
    db_measurements = queries.find_all_measurements(db)
    return db_measurements


@router.get("/users/me/targets/measurements", response_model=list[MeasurementResponse])
async def get_my_measurements(
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_current_user)],
):
    db_measurements = queries.find_all_measurements(db, user_id=current_user.id)
    return db_measurements


@router.get("/users/me/targets/{target_id}/measurements", response_model=list[MeasurementResponse])
async def get_my_target_measurements(
        target_id: int,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_current_user)],
):
    db_measurements = find_all_measurements(db, target_id, current_user.id)
    return db_measurements


@router.get("/users/me/targets/{target_id}/measurements/{measurement_id}", response_model=list[MeasurementResponse])
async def get_my_target_measurement(
        target_id: int,
        measurement_id: int,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_current_user)],
):
    db_measurement = find_measurement(db, measurement_id, target_id, current_user.id)
    return db_measurement


@router.get("/users/{user_id}/targets/{target_id}/measurements", response_model=list[MeasurementResponse])
async def get_target_measurements(user_id: int, target_id: int, db: Annotated[Session, Depends(get_db)]):
    db_measurements = find_all_measurements(db, target_id, user_id)
    return db_measurements


@router.get("/users/{user_id}/targets/{target_id}/measurements/{measurement_id}", response_model=MeasurementResponse)
async def get_measurement(user_id: int, target_id: int, measurement_id: int, db: Annotated[Session, Depends(get_db)]):
    db_measurement = queries.find_measurement(db, measurement_id, target_id, user_id)
    if not db_measurement:
        raise exceptions.http_exception_not_found(f"Measurement with {measurement_id} not found")
    return db_measurement


@router.post("/users/{user_id}/targets/{target_id}/measurements/", response_model=MeasurementResponse)
def create_measurement(
        user_id: int,
        target_id: int,
        request: MeasurementRequest,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.id != user_id and not is_admin(current_user):
        raise exceptions.http_exception_forbidden()

    db_target = find_target(db, target_id, user_id)
    if not db_target:
        raise exceptions.http_exception_not_found(f"Target with {target_id} for user {user_id} not found")

    db_new_measurement = Measurement(**request.model_dump(), target_id=target_id)
    db.add(db_new_measurement)
    db.commit()

    return db_new_measurement


@router.patch("/users/{user_id}/targets/{target_id}/measurements/{measurement_id}",
              response_model=MeasurementResponse)
def update_measurement(
        user_id: int,
        target_id: int,
        measurement_id: int,
        request: MeasurementRequest,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.id != user_id and not is_admin(current_user):
        raise exceptions.http_exception_forbidden()
    db_measurement = find_measurement(db, measurement_id, target_id, user_id)
    if not db_measurement:
        raise exceptions.http_exception_not_found(f"Measurement with id {measurement_id} not found")

    new_data_for_db_measurement = request.model_dump()
    for key, value in new_data_for_db_measurement.items():
        setattr(db_measurement, key, value)

    db.commit()
    db.refresh(db_measurement)
    return db_measurement


@router.delete("/users/{user_id}/targets/{target_id}/measurements/{measurement_id}")
def delete_measurement(
        user_id: int,
        target_id: int,
        measurement_id: int,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.id != user_id and not is_admin(current_user):
        raise exceptions.http_exception_forbidden()

    db_measurement = find_measurement(db, measurement_id, target_id, user_id)
    if not db_measurement:
        raise exceptions.http_exception_not_found(f"Measurement with id {measurement_id} not found")

    db.delete(db_measurement)
    db.commit()
    return {"message": f"Measurement {measurement_id} deleted."}
