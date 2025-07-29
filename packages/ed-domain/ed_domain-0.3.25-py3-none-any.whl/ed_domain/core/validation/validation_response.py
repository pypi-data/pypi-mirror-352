from ed_domain.core.validation.validation_error import ValidationError


class ValidationResponse:
    def __init__(
        self,
        errors: list[ValidationError] = [],
    ):
        self.errors = errors

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0
