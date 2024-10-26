from fastapi import FastAPI

from routers import user_router, target_router, measurement_router, auth_router, role_router
from services.db_service import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router)
app.include_router(measurement_router)
app.include_router(target_router)
app.include_router(user_router)
app.include_router(role_router)
