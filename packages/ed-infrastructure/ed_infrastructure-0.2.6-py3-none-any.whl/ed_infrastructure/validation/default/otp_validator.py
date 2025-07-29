from ed_domain.core.validation import (ABCValidator, ValidationError,
                                       ValidationErrorType, ValidationResponse)


class OtpValidator(ABCValidator[str]):
    def validate(
        self,
        value: str,
        location: str = ABCValidator.DEFAULT_ERROR_LOCATION,
    ) -> ValidationResponse:
        errors: list[ValidationError] = []

        if not value.isnumeric():
            errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_TYPE,
                    "message": "OTP must be numeric.",
                    "input": value,
                }
            )
            return ValidationResponse(errors)

        if len(value) != 4:
            errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "OTP must be exactly 4 digits long.",
                    "input": value,
                }
            )

        return ValidationResponse(errors)
