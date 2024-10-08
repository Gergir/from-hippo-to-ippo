from typing import Annotated
from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import jwt
from fastapi.security import OAuth2PasswordBearer
from helpers.exceptions import http_exception_unauthorized
from services.db_service import get_db
from models import User
from auth import Hash
import os


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"



SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

router = APIRouter(tags=["Auth"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(db: Session, request_email: str, request_password: str) -> User:
    db_user = db.query(User).filter(User.email == request_email).first()
    if not db_user:
        raise http_exception_unauthorized("Invalid username or password")
    if not Hash.verify(plain_password=request_password, hashed_password=db_user.password):
        raise http_exception_unauthorized("Invalid username or password")
    return db_user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[Session, Depends(get_db)]
):
    # form_data.username - variable username is fixed, we will use it to check our user's email
    db_user = authenticate_user(db, request_email=form_data.username, request_password=form_data.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': db_user.email}, expires_delta=access_token_expires)

    return Token(access_token=access_token, token_type="bearer")
