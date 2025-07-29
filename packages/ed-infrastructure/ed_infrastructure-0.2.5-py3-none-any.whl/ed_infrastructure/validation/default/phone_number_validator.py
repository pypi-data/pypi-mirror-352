import re

from ed_domain.core.validation import (ABCValidator, ValidationError,
                                       ValidationErrorType, ValidationResponse)


class PhoneNumberValidator(ABCValidator[str]):
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
                    "message": "Phone number is required.",
                    "input": value,
                }
            )
            return ValidationResponse(errors)

        if not re.match(r"^(\+251|0|251)?9\d{8}$", value):
            errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "Invalid phone number format. It should be in one of the following formats: +2519XXXXXXXX, 2519XXXXXXXX, or 09XXXXXXXX.",
                    "input": value,
                }
            )
        return ValidationResponse(errors)
