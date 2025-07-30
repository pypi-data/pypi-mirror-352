from dataclasses import dataclass
from enum import StrEnum

from ed_domain.core.value_objects.base_value_object import BaseValueObject


class Unit(StrEnum):
    KG = "kg"
    G = "g"


@dataclass
class Length(BaseValueObject):
    value: float
    currency: Unit

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "value": self.value,
            "unit": self.currency.value,
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "Length":
        return cls(
            id=dict_value["id"],
            value=dict_value["value"],
            currency=Unit(dict_value["unit"]),
        )
