from typing import TypedDict

from ed_domain.core.validation.validation_error_type import ValidationErrorType


class ValidationError(TypedDict):
    type: ValidationErrorType
    location: str
    message: str
    input: str
