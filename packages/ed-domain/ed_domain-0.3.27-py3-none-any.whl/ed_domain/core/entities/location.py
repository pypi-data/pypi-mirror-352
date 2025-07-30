from dataclasses import dataclass
from datetime import datetime

from ed_domain.core.entities.base_entity import BaseEntity


@dataclass
class Location(BaseEntity):
    address: str
    latitude: float
    longitude: float
    postal_code: str
    city: str
    country: str
    last_used: datetime

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "postal_code": self.postal_code,
            "city": self.city,
            "country": self.country,
            "last_used": self.last_used.isoformat(),
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "Location":
        base_entity = BaseEntity.from_dict(dict_value)
        return cls(
            **vars(base_entity),
            address=dict_value["address"],
            latitude=dict_value["latitude"],
            longitude=dict_value["longitude"],
            postal_code=dict_value["postal_code"],
            city=dict_value["city"],
            country=dict_value["country"],
            last_used=datetime.fromisoformat(dict_value["last_used"]),
        )
