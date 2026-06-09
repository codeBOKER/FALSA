from fastapi import Header, HTTPException, Request, status

from app.services.container import ServiceContainer


def get_container(request: Request) -> ServiceContainer:
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service container is not initialized",
        )
    return container


def verify_admin_api_key(
    request: Request,
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-Api-Key"),
) -> None:
    expected = get_container(request).settings.admin_api_key
    if not x_admin_api_key or x_admin_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key",
        )
