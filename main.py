from fastapi import FastAPI
from routers import user_router, target_router, measurement_router
app = FastAPI()
app.include_router(user_router)
app.include_router(target_router)
app.include_router(measurement_router)


@app.get("/")
async def welcome():
    return "Hello World!"