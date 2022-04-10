"""Model response"""
# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods

from typing import Any, Optional

from models.base_model import MyModel


class BaseResponseData(MyModel):
    """Model response success"""

    code: int = 0
    message: Optional[str] = "Success"
    result: Optional[Any] = {}


class BaseErrorResponse(MyModel):
    """mode response error"""

    code: int = 1
    errors: dict
    request_id: Optional[str]
