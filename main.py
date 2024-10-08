from typing import Annotated
from fastapi import FastAPI, Depends
from routers import user_router, target_router, measurement_router, auth_router
from fastapi.security import OAuth2PasswordBearer
from services.db_service import Base, engine

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(target_router)
app.include_router(measurement_router)
Base.metadata.create_all(bind=engine)

@app.get("/")
async def welcome():
    return "Hello World!"
