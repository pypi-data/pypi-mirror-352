from typing import Literal

from ed_domain.core.validation import (ABCValidator, ValidationError,
                                       ValidationErrorType, ValidationResponse)


class _LatitudeLongitudeValidator(ABCValidator[float]):
    def __init__(self, validator_name: Literal["Latitude", "Longitude"]):
        super().__init__()
        self._validator_name = validator_name

    def validate(
        self, value: float, location: str = ABCValidator.DEFAULT_ERROR_LOCATION
    ) -> ValidationResponse:
        error_location = location or self.DEFAULT_ERROR_LOCATION
        errors: list[ValidationError] = []

        if self._validator_name == "Latitude" and not (8.8 <= value <= 9.1):
            errors.append(
                {
                    "location": error_location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": f"{self._validator_name} must be between 8.8 and 9.1 degrees to be valid for Addis Ababa.",
                    "input": f"{location}",
                }
            )

        if self._validator_name == "Longitude" and not (38.6 <= value <= 39.0):
            errors.append(
                {
                    "location": error_location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": f"{self._validator_name} must be between 38.6 and 39.0 degrees to be valid for Addis Ababa.",
                    "input": f"{location}",
                }
            )

        return ValidationResponse(errors)


class LatitudeValidator(_LatitudeLongitudeValidator):
    def __init__(self):
        super().__init__("Latitude")


class LongitudeValidator(_LatitudeLongitudeValidator):
    def __init__(self):
        super().__init__("Longitude")
