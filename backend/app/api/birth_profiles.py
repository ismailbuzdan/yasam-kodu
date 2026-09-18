from fastapi import APIRouter, status

from app.schemas.birth_profile import BirthProfile, BirthProfileValidationResponse

router = APIRouter(prefix="/api/v1/birth-profiles", tags=["birth-profiles"])


@router.post("/validate", response_model=BirthProfileValidationResponse, status_code=status.HTTP_200_OK)
def validate_birth_profile(profile: BirthProfile) -> BirthProfileValidationResponse:
    return BirthProfileValidationResponse(profile=profile)
