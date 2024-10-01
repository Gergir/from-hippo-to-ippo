from fastapi import APIRouter

router = APIRouter(tags=["target"], prefix="/target")


@router.get("/")
async def get_all_targets():
    return {"message": "All found targets: ..."}


@router.get("/{target_id}")
async def get_target(target_id: int):
    return {"message": f"Target with id {target_id} found"}


@router.get("/name/{target_name}")
async def get_target_by_name(target_name: str):
    return {"message": f"Target with name {target_name} found"}


@router.post("/create")
async def create_target():
    return {"message": "Target has been created"}


@router.patch("/update/{target_id}")
async def update_target(target_id: int):
    return {"message": f"Target with id {target_id} updated"}


@router.delete("/delete/{target_id}")
async def delete_target(target_id: int):
    return {"message": f"Target with id {target_id} deleted"}
