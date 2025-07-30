from enum import StrEnum


class ValidationErrorType(StrEnum):
    MISSING_FIELD = "missing_field"
    INVALID_TYPE = "invalid_type"
    INVALID_VALUE = "invalid_value"
    FORMAT_ERROR = "format_error"
    OTHER = "other"
