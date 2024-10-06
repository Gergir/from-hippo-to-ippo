from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.db_service import get_db
from models import Measurement
from schemas import MeasurementRequest, MeasurementResponse
from helpers.exceptions import raise_http_exception_not_found

router = APIRouter(tags=["measurement"], prefix="/measurement")


@router.get("/", response_model=List[MeasurementResponse])
async def get_all_measurements(db: Session = Depends(get_db)):
    db_measurements = db.query(Measurement).all()
    return db_measurements


@router.get("/{measurement_id}", response_model=MeasurementResponse)
async def get_measurement(measurement_id: int, db: Session = Depends(get_db)):
    db_measurement = db.query(Measurement).filter(Measurement.id == measurement_id).first()
    if not db_measurement:
        raise raise_http_exception_not_found(f"Measurement with {measurement_id} not found")

    return db_measurement


@router.post("/create", response_model=MeasurementResponse)
def create_measurement(request: MeasurementRequest, db: Session = Depends(get_db)):
    db_new_measurement = Measurement(**request.model_dump())
    db.add(db_new_measurement)
    db.commit()

    return db_new_measurement


@router.patch("/update/{measurement_id}", response_model=MeasurementResponse)
def update_measurement(measurement_id: int, request: MeasurementRequest, db: Session = Depends(get_db)):
    db_measurement = db.query(Measurement).filter(Measurement.id == measurement_id).first()
    if not db_measurement:
        raise raise_http_exception_not_found(f"Measurement with {measurement_id} not found")

    new_data_for_db_measurement = request.model_dump()
    for key, value in new_data_for_db_measurement.items():
        setattr(db_measurement, key, value)

    db.commit()
    db.refresh(db_measurement)
    return db_measurement


@router.delete("/delete/{measurement_id}")
def delete_measurement(measurement_id: int, db: Session = Depends(get_db)):
    db_measurement = db.query(Measurement).filter(Measurement.id == measurement_id).first()
    if not db_measurement:
        raise raise_http_exception_not_found(f"Measurement with {measurement_id} not found")

    db.delete(db_measurement)
    db.commit()
    return {"message": f"Measurement {measurement_id} deleted."}
