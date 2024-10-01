from fastapi import APIRouter

router = APIRouter(tags=["measurement"], prefix="/measurement")


@router.get("/")
async def get_all_measurements():
    return {"message": "All found measurements"}


@router.get("/{measurement_id}")
async def get_measurement(measurement_id: int):
    return {"message": f"Measurement with id {measurement_id} found"}


@router.post("/create")
def create_measurement():
    return {"message": "Measurement created"}


@router.patch("/update/{measurement_id}")
def update_measurement(measurement_id: int):
    return {"message": f"Measurement with id {measurement_id} updated"}


@router.delete("/delete/{measurement_id}")
def delete_measurement(measurement_id: int):
    return {"message": f"Measurement with id {measurement_id} deleted"}
