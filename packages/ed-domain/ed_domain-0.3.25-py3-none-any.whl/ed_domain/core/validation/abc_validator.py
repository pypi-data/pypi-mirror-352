from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ed_domain.core.validation.validation_response import ValidationResponse

T = TypeVar("T")


class ABCValidator(Generic[T], ABC):
    DEFAULT_ERROR_LOCATION: str = "body"

    def validate_many(
        self,
        values: list[T],
        location: str = DEFAULT_ERROR_LOCATION,
    ) -> ValidationResponse:
        list_validation_response: ValidationResponse = ValidationResponse([])

        for index, value in enumerate(values):
            validation_response = self.validate(
                value, f"{location}[{index + 1}]")

            if validation_response.is_valid:
                continue

            list_validation_response.errors.extend(validation_response.errors)

        return list_validation_response

    @abstractmethod
    def validate(
        self,
        value: T,
        location: str = DEFAULT_ERROR_LOCATION,
    ) -> ValidationResponse: ...
