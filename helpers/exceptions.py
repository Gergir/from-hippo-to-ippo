from fastapi import HTTPException, status


def raise_http_exception_not_found(message="Entity not found"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
