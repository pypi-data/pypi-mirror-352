from dataclasses import dataclass
from enum import StrEnum

from ed_domain.core.value_objects.base_value_object import BaseValueObject


class Currency(StrEnum):
    ETB = "etb"
    USD = "usd"


@dataclass
class Money(BaseValueObject):
    value: float
    currency: Currency

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "value": self.value,
            "currency": self.currency.value,
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "Money":
        base_value_object = BaseValueObject.from_dict(dict_value)

        return cls(
            **vars(base_value_object),
            value=dict_value["value"],
            currency=Currency(dict_value["currency"]),
        )
