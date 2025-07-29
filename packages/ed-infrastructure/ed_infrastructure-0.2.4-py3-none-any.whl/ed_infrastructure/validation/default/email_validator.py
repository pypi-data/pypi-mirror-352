import re

from ed_domain.core.validation import (ABCValidator, ValidationError,
                                       ValidationErrorType, ValidationResponse)


class EmailValidator(ABCValidator[str]):
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
                    "message": "Email is required.",
                    "input": value,
                }
            )

            return ValidationResponse(errors)

        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "Invalid email format.",
                    "input": value,
                }
            )

        return ValidationResponse(errors)
