import re

from ed_domain.core.validation import ABCValidator, ValidationErrorType
from ed_domain.core.validation.validation_error import ValidationError
from ed_domain.core.validation.validation_response import ValidationResponse


class NameValidator(ABCValidator[str]):
    def validate(
        self,
        value: str,
        location: str = ABCValidator.DEFAULT_ERROR_LOCATION,
    ) -> ValidationResponse:
        errors: list[ValidationError] = []

        if not value:
            errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.MISSING_FIELD,
                    "message": "Name is required.",
                    "input": value,
                }
            )
            return ValidationResponse(errors)

        if not re.match(r"^[a-zA-Z]+$", value):
            errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "Name must contain only alphabetic characters.",
                    "input": value,
                }
            )

        if len(value) < 2 or len(value) > 20:
            errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "Name must be between 2 and 15 characters long.",
                    "input": value,
                }
            )

        return ValidationResponse(errors)
