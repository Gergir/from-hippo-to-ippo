from fastapi import FastAPI
from routers import user_router, target_router, measurement_router
from services.db_service import Base, engine

app = FastAPI()
app.include_router(user_router)
app.include_router(target_router)
app.include_router(measurement_router)
Base.metadata.create_all(bind=engine)

@app.get("/")
async def welcome():
    return "Hello World!"