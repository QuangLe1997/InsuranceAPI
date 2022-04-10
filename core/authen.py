from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status

from configs import settings

api_key_header_auth = APIKeyHeader(name="Authorization", auto_error=True)


async def get_api_key(
    api_key_header: str = Security(api_key_header_auth),
):
    """Get api key from header"""

    key = settings.security.SECRET_KEY
    if api_key_header != key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not found",
        )
