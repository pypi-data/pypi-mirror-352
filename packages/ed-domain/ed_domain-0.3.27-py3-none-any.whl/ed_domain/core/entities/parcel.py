from dataclasses import dataclass
from enum import StrEnum

from ed_domain.core.entities.base_entity import BaseEntity


class ParcelSize(StrEnum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


@dataclass
class Parcel(BaseEntity):
    size: ParcelSize
    length: int
    width: int
    height: float
    weight: float
    fragile: bool

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "size": self.size.value,
            "length": self.length,
            "width": self.width,
            "height": self.height,
            "weight": self.weight,
            "fragile": self.fragile,
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "Parcel":
        base_entity = BaseEntity.from_dict(dict_value)
        return cls(
            **vars(base_entity),
            size=ParcelSize(dict_value["size"]),
            length=dict_value["length"],
            width=dict_value["width"],
            height=dict_value["height"],
            weight=dict_value["weight"],
            fragile=dict_value["fragile"],
        )
