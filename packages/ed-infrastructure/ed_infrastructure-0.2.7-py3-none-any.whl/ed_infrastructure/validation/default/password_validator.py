import re

from ed_domain.core.validation import (ABCValidator, ValidationError,
                                       ValidationErrorType, ValidationResponse)


class PasswordValidator(ABCValidator[str]):
    def validate(
        self,
        value: str,
        location: str = ABCValidator.DEFAULT_ERROR_LOCATION,
    ) -> ValidationResponse:
        errors: list[ValidationError] = []

        if not value:
            errors.append(
                {
                    "message": "Password is required.",
                    "location": location,
                    "type": ValidationErrorType.MISSING_FIELD,
                    "input": value,
                }
            )
            return ValidationResponse(errors)

        if len(value) < 8:
            errors.append(
                {
                    "message": "Password must be at least 8 characters long.",
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "input": value,
                }
            )

        if not re.search(r"\d", value):
            errors.append(
                {
                    "message": "Password must include at least one digit.",
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "input": value,
                }
            )

        if not re.search(r"[A-Z]", value):
            errors.append(
                {
                    "message": "Password must include at least one uppercase letter.",
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "input": value,
                }
            )

        if not re.search(r"[a-z]", value):
            errors.append(
                {
                    "message": "Password must include at least one lowercase letter.",
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "input": value,
                }
            )

        if not re.search(r"[@#$%^&*()_+=!-]", value):
            errors.append(
                {
                    "message": "Password must include at least one special character.",
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "input": value,
                }
            )

        return ValidationResponse(errors)
