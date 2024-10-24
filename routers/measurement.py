from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.auth import is_admin
from services.db_service import get_db
from models import Measurement, Target, User
from schemas import MeasurementRequest, MeasurementResponse
from auth import get_current_user
from helpers.exceptions import http_exception_not_found, http_exception_forbidden

router = APIRouter(tags=["measurement"], prefix="")


@router.get("/users/targets/measurements", response_model=list[MeasurementResponse])
async def get_all_measurements(db: Annotated[Session, Depends(get_db)]):
    db_measurements = db.query(Measurement).all()
    return db_measurements

@router.get("/users/{user_id}/targets/{target_id}/measurements", response_model=list[MeasurementResponse])
async def get_measurement(user_id: int, target_id: int, db: Annotated[Session, Depends(get_db)]):
    db_measurements = db.query(Measurement).join(Measurement.target).join(Target.user).filter(User.id == user_id, Target.id == target_id).all()
    if not db_measurements:
        raise http_exception_not_found()
    return db_measurements


@router.get("/users/{user_id}/targets/{target_id}/measurements/{measurement_id}", response_model=MeasurementResponse)
async def get_measurement(user_id: int, target_id: int, measurement_id: int, db: Annotated[Session, Depends(get_db)]):
    db_measurement = db.query(Measurement).join(Measurement.target).join(Target.user).filter(User.id == user_id, Target.id == target_id, Measurement.id == measurement_id).first()
    if not db_measurement:
        raise http_exception_not_found(f"Measurement with {measurement_id} not found")
    return db_measurement


@router.post("/users/{user_id}/targets/{target_id}/measurements/create", response_model=MeasurementResponse)
def create_measurement(user_id: int, target_id: int, request: MeasurementRequest, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.id != user_id and not is_admin(current_user):
        raise http_exception_forbidden()

    db_target = db.query(Target).filter(Target.id == target_id).first()
    if not db_target:
        raise http_exception_not_found(f"Target with id {target_id} not found")

    if db_target.user_id != user_id:
        raise http_exception_forbidden("Target not associated with user")

    db_new_measurement = Measurement(**request.model_dump(), target_id=target_id)
    db.add(db_new_measurement)
    db.commit()

    return db_new_measurement


@router.patch("/users/{user_id}/targets/{target_id}/measurements/update/{measurement_id}", response_model=MeasurementResponse)
def update_measurement(user_id: int, target_id: int, measurement_id: int, request: MeasurementRequest, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.id != user_id and not is_admin(current_user):
        raise http_exception_forbidden()
    db_measurement = db.query(Measurement).join(Measurement.target).join(Target.user).filter(user_id == User.id, Target.id == target_id, Measurement.id == measurement_id).first()
    if not db_measurement:
        raise http_exception_not_found(f"Measurement with id {measurement_id} not found")

    new_data_for_db_measurement = request.model_dump()
    for key, value in new_data_for_db_measurement.items():
        setattr(db_measurement, key, value)

    db.commit()
    db.refresh(db_measurement)
    return db_measurement


@router.delete("/users/{user_id}/targets/{target_id}/measurements/delete/{measurement_id}")
def delete_measurement(user_id: int, target_id: int, measurement_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.id != user_id and not is_admin(current_user):
        raise http_exception_forbidden()

    db_measurement = db.query(Measurement).join(Measurement.target).join(Target.user).filter(user_id == User.id, Target.id == target_id, Measurement.id == measurement_id).first()
    if not db_measurement:
        raise http_exception_not_found(f"Measurement with {measurement_id} not found")

    db.delete(db_measurement)
    db.commit()
    return {"message": f"Measurement {measurement_id} deleted."}
