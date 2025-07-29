from ed_domain.core.validation import (ABCValidator, ValidationError,
                                       ValidationErrorType, ValidationResponse)
from ed_infrastructure.validation.default.email_validator import EmailValidator
from ed_infrastructure.validation.default.name_validator import NameValidator
from ed_infrastructure.validation.default.password_validator import \
    PasswordValidator
from ed_infrastructure.validation.default.phone_number_validator import \
    PhoneNumberValidator

from ed_auth.application.features.auth.dtos import UpdateUserDto


class UpdateUserDtoValidator(ABCValidator[UpdateUserDto]):
    def __init__(self):
        super().__init__()
        self._email_validator = EmailValidator()
        self._phone_number_validator = PhoneNumberValidator()
        self._password_validator = PasswordValidator()
        self._name_validator = NameValidator()

    def validate(
        self, value: UpdateUserDto, location: str = ABCValidator.DEFAULT_ERROR_LOCATION
    ) -> ValidationResponse:
        errors: list[ValidationError] = []

        if not value.id:
            errors.append(
                {
                    "message": "User ID is required",
                    "location": f"{location}.user_id",
                    "input": value.id,
                    "type": ValidationErrorType.MISSING_FIELD,
                }
            )

        if value.first_name:
            first_name_validation_response = self._name_validator.validate(
                value.first_name, f"{location}.first_name"
            )
            errors.extend(first_name_validation_response.errors)

        if value.last_name:
            last_name_validation_response = self._name_validator.validate(
                value.last_name, f"{location}.last_name"
            )
            errors.extend(last_name_validation_response.errors)

        if value.email is None and value.phone_number is None:
            errors.append(
                {
                    "location": f"{location}.email and {location}.phone_number",
                    "message": "Either email or phone number must be provided",
                    "input": f"{value.email} or {value.phone_number}",
                    "type": ValidationErrorType.MISSING_FIELD,
                }
            )

        if value.email:
            email_validation_response = self._email_validator.validate(
                value.email, f"{location}.email"
            )
            errors.extend(email_validation_response.errors)

        if value.phone_number:
            phone_number_validation_response = self._phone_number_validator.validate(
                value.phone_number, f"{location}.phone_number"
            )
            errors.extend(phone_number_validation_response.errors)

        if value.password:
            password_validation_response = self._password_validator.validate(
                value.password, f"{location}.password"
            )
            errors.extend(password_validation_response.errors)

        return ValidationResponse(errors)
