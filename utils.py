from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from starlette.responses import JSONResponse


def create_aliased_response(model: BaseModel) -> JSONResponse:
    """create aliased response"""

    return JSONResponse(content=jsonable_encoder(model, by_alias=True))
