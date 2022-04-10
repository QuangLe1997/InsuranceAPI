import datetime
import logging

import pygsheets
from fastapi import APIRouter, Depends, Body, Security

from configs import settings
from core.authen import get_api_key
from models.base_model import CarInsuranceModel
from models.base_response import BaseResponseData, BaseErrorResponse
from utils import create_aliased_response

router = APIRouter()
GC_SHEET_SRV = None
CURRENT_ROW = 2
telegram_logger = logging.getLogger("critical")


def get_gg_sheet_inst():
    global GC_SHEET_SRV
    global CURRENT_ROW
    if GC_SHEET_SRV:
        CURRENT_ROW += 1
        return GC_SHEET_SRV
    else:
        gc = pygsheets.authorize(service_file="insurance.json")
        sh = gc.open(settings.SHEET_NAME)
        GC_SHEET_SRV = sh[0]
        GC_SHEET_SRV.insert_rows(
            CURRENT_ROW,
            number=1,
            values=[
                "Họ Tên",
                "SĐT",
                "Email",
                "Hãng xe",
                "Dòng xe",
                "Năm sản xuất xe",
                "Tỉnh thành",
                "Ngày đăng ký đầu tiên",
                "Ngày hiệu lực Bảo hiểm",
                "Xe kinh doanh",
                "Gói bảo hiểm",
                "Thời gian Submit",
            ],
            inherit=True,
        )
        CURRENT_ROW += 1
        return GC_SHEET_SRV


@router.get(
    "/healthcheck",
    response_model=BaseResponseData,
    tags=["Wrapper API"],
)
async def health_check():
    """Add multiple task to task-pipeline"""
    return create_aliased_response(
        BaseResponseData(
            code=0,
            message="success",
            result={"health_check": "Oke"},
        )
    )


@router.post(
    "/car-insurance/new-insurance",
    response_model=BaseResponseData,
    tags=["Wrapper API"],
    dependencies=[Security(get_api_key)],
)
async def new_car_insurance(
    *,
    body: CarInsuranceModel = Body(
        ...,
    ),
    gg_sh=Depends(get_gg_sheet_inst)
):
    """Add multiple task to task-pipeline"""

    try:
        gg_sh.insert_rows(
            CURRENT_ROW,
            number=1,
            values=[
                body.name,
                body.phone,
                body.email,
                body.car_brand,
                body.car_model,
                body.car_year,
                body.province,
                body.date_registry,
                body.date_insurance_atv,
                body.is_ecom,
                body.fee_package,
                datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            ],
            inherit=True,
        )
        telegram_logger.info("New data insert", body.dict())
        return create_aliased_response(
            BaseResponseData(
                code=0,
                message="success",
                result={},
            )
        )
    except Exception as ex:
        telegram_logger.error("New data update error", body.dict())
        return (
            create_aliased_response(
                BaseErrorResponse(code=1, message="servce  error", detail=str(ex)),
            ),
            400,
        )
