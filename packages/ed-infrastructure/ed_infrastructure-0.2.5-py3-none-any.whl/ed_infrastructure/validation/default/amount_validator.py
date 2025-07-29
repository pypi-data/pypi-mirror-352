from ed_domain.core.validation import (ABCValidator, ValidationError,
                                       ValidationErrorType, ValidationResponse)


class AmountValidator(ABCValidator[float]):
    def validate(
        self,
        value: float,
        location: str = ABCValidator.DEFAULT_ERROR_LOCATION,
    ) -> ValidationResponse:
        location = location
        errors: list[ValidationError] = []

        if value <= 0:
            errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "Amount must be greater than zero.",
                    "input": f"{value}",
                }
            )

        if value > 1_000_000:
            errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "Amount must not exceed 1,000,000.",
                    "input": f"{value}",
                }
            )

        return ValidationResponse(errors)
