from ed_domain.core.validation import (ABCValidator, ValidationError,
                                       ValidationErrorType, ValidationResponse)
from ed_infrastructure.validation.default.otp_validator import OtpValidator

from ed_auth.application.features.auth.dtos.create_user_verify_dto import \
    CreateUserVerifyDto


class CreateUserVerifyDtoValidator(ABCValidator[CreateUserVerifyDto]):
    def __init__(self) -> None:
        super().__init__()
        self._otp_validator = OtpValidator()

    def validate(
        self,
        value: CreateUserVerifyDto,
        location: str = ABCValidator.DEFAULT_ERROR_LOCATION,
    ) -> ValidationResponse:
        errors: list[ValidationError] = []

        if not value["user_id"]:
            errors.append(
                {
                    "message": "User ID is required",
                    "location": f"{location}.user_id",
                    "input": value["user_id"],
                    "type": ValidationErrorType.MISSING_FIELD,
                }
            )

        otp_validation_response = self._otp_validator.validate(
            value["otp"], f"{location}.otp"
        )
        errors.extend(otp_validation_response.errors)

        return ValidationResponse(errors)
