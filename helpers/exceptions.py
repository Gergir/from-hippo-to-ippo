from fastapi import HTTPException, status


def http_exception_not_found(message="Entity not found"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


def http_exception_unauthorized(message="Could not valid credentials"):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={'WWW-Authenticate': 'Bearer'}
    )
