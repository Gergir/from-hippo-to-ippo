from fastapi import FastAPI

from routers import user_router, target_router, measurement_router, auth_router, role_router


app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(target_router)
app.include_router(measurement_router)
app.include_router(role_router)


@app.get("/")
async def welcome():
    return "Hello World!"
