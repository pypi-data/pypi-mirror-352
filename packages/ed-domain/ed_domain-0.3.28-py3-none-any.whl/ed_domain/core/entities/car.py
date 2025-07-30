from dataclasses import dataclass

from ed_domain.core.entities.base_entity import BaseEntity


@dataclass
class Car(BaseEntity):
    make: str
    model: str
    year: int
    registration_number: str
    license_plate_number: str
    color: str
    seats: int

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "registration_number": self.registration_number,
            "license_plate_number": self.license_plate_number,
            "color": self.color,
            "seats": self.seats,
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "Car":
        base_entity = BaseEntity.from_dict(dict_value)
        return cls(
            **vars(base_entity),
            make=dict_value["make"],
            model=dict_value["model"],
            year=dict_value["year"],
            registration_number=dict_value["registration_number"],
            license_plate_number=dict_value["license_plate_number"],
            color=dict_value["color"],
            seats=dict_value["seats"],
        )
