from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.db_service import get_db
from models import User
from schemas import UserRequest, UserResponse

router = APIRouter(tags=["user"], prefix="/user")


@router.get("/", response_model=List[UserResponse])
async def get_all_users(db: Session = Depends(get_db)):
    db_users = db.query(User).all()
    return db_users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise
    return db_user


@router.get("/name/{username}", response_model=UserResponse)
async def get_user_by_name(username: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise
    return db_user


@router.post("/create", response_model=UserResponse)
async def create_user(request: UserRequest, db: Session = Depends(get_db)):
    db_new_user = User(**request.model_dump())
    db.add(db_new_user)
    db.commit()
    return db_new_user


@router.patch("/update/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, request: UserRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise

    new_data_for_db_user = request.model_dump(exclude_unset=True)
    for key, value in new_data_for_db_user.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/delete/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise
    db.delete(db_user)
    db.commit()
    return {"message": f"User {user_id} deleted."}
