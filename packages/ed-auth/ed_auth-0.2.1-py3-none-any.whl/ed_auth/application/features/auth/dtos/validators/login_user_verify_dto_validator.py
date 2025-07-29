from ed_domain.core.validation import (ABCValidator, ValidationError,
                                       ValidationErrorType, ValidationResponse)
from ed_infrastructure.validation.default import OtpValidator

from ed_auth.application.features.auth.dtos.login_user_verify_dto import \
    LoginUserVerifyDto


class LoginUserVerifyDtoValidator(ABCValidator[LoginUserVerifyDto]):
    def __init__(self) -> None:
        super().__init__()
        self._otp_validator = OtpValidator()

    def validate(
        self,
        value: LoginUserVerifyDto,
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
