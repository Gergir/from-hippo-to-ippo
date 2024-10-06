from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.db_service import get_db
from models import Target
from schemas import TargetRequest, TargetResponse
from helpers.exceptions import raise_http_exception_not_found

router = APIRouter(tags=["target"], prefix="/target")


@router.get("/", response_model=List[TargetResponse])
async def get_all_targets(db: Session = Depends(get_db)):
    db_targets = db.query(Target).all()
    return db_targets


@router.get("/{target_id}", response_model=TargetResponse)
async def get_target(target_id: int, db: Session = Depends(get_db)):
    db_target = db.query(Target).filter(Target.id == target_id).first()
    if not db_target:
        raise raise_http_exception_not_found(f"Target with id {target_id} not found")

    return db_target


@router.get("/name/{target_name}", response_model=TargetResponse)
async def get_target_by_name(target_name: str, db: Session = Depends(get_db)):
    db_target = db.query(Target).filter(Target.title == target_name).first()
    if not db_target:
        raise raise_http_exception_not_found(f"Target with name {target_name} not found")

    return db_target


@router.post("/create", response_model=TargetResponse)
async def create_target(request: TargetRequest, db: Session = Depends(get_db)):
    db_new_target = Target(**request.model_dump())
    db.add(db_new_target)
    db.commit()
    return db_new_target


@router.patch("/update/{target_id}", response_model=TargetResponse)
async def update_target(target_id: int, request: TargetRequest, db: Session = Depends(get_db)):
    db_target = db.query(Target).filter(Target.id == target_id).first()
    if not db_target:
        raise raise_http_exception_not_found(f"Target with id {target_id} not found")

    new_data_for_db_target = request.model_dump()
    for key, value in new_data_for_db_target.items():
        setattr(db_target, key, value)

    db.commit()
    db.refresh(db_target)
    return db_target


@router.delete("/delete/{target_id}")
async def delete_target(target_id: int, db: Session = Depends(get_db)):
    db_target = db.query(Target).filter(Target.id == target_id).first()
    if not db_target:
        raise raise_http_exception_not_found(f"Target with id {target_id} not found")

    db.delete(db_target)
    db.commit()
    return {"message": f"Target with id {target_id} deleted"}
