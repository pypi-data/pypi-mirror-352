from ed_domain.core.validation import (ABCValidator, ValidationError,
                                       ValidationErrorType, ValidationResponse)
from ed_infrastructure.validation.default.email_validator import EmailValidator
from ed_infrastructure.validation.default.password_validator import \
    PasswordValidator
from ed_infrastructure.validation.default.phone_number_validator import \
    PhoneNumberValidator

from ed_auth.application.features.auth.dtos.login_user_dto import LoginUserDto


class LoginUserDtoValidator(ABCValidator[LoginUserDto]):
    def __init__(self) -> None:
        super().__init__()
        self._email_validator = EmailValidator()
        self._password_validator = PasswordValidator()
        self._phone_number_validator = PhoneNumberValidator()

    def validate(
        self, value: LoginUserDto, location: str = ABCValidator.DEFAULT_ERROR_LOCATION
    ) -> ValidationResponse:
        errors: list[ValidationError] = []

        if value.get("email") is None and value.get("phone_number") is None:
            errors.append(
                {
                    "location": f"{location}.email or {location}.phone_number",
                    "message": "Either email or phone number must be provided",
                    "input": f'{value.get("email")} or {value.get("phone_number")}',
                    "type": ValidationErrorType.MISSING_FIELD,
                }
            )

        if "email" in value:
            email_validation_response = self._email_validator.validate(
                value["email"], f"{location}.email"
            )
            errors.extend(email_validation_response.errors)

        if "phone_number" in value:
            phone_number_validation_response = self._phone_number_validator.validate(
                value["phone_number"], f"{location}.phone_number"
            )
            errors.extend(phone_number_validation_response.errors)

        if "password" in value:
            password_validation_response = self._password_validator.validate(
                value["password"], f"{location}.password"
            )
            errors.extend(password_validation_response.errors)

        return ValidationResponse(errors)
