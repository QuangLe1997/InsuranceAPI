from fastapi import APIRouter

from .car_insurance import router as car_insurance

router = APIRouter()
router.include_router(car_insurance)
