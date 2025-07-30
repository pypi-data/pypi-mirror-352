from dataclasses import dataclass
from uuid import UUID

from ed_domain.core.aggregate_roots.base_aggregate_root import \
    BaseAggregateRoot


@dataclass
class Business(BaseAggregateRoot):
    user_id: UUID
    business_name: str
    owner_first_name: str
    owner_last_name: str
    phone_number: str
    email: str
    location_id: UUID

    def update_business_name(self, new_name: str) -> None:
        self.business_name = new_name

    def update_phone_number(self, new_phone_number: str) -> None:
        self.phone_number = new_phone_number

    def update_email(self, new_email: str) -> None:
        self.email = new_email

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "user_id": self.business_name,
            "business_name": self.business_name,
            "owner_first_name": self.owner_first_name,
            "owner_last_name": self.owner_last_name,
            "phone_number": self.phone_number,
            "email": self.email,
            "location_id": str(self.location_id),
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "Business":
        base_entity = BaseAggregateRoot.from_dict(dict_value)
        return cls(
            **vars(base_entity),
            user_id=dict_value["user_id"],
            business_name=dict_value["business_name"],
            owner_first_name=dict_value["owner_first_name"],
            owner_last_name=dict_value["owner_last_name"],
            phone_number=dict_value["phone_number"],
            email=dict_value["email"],
            location_id=UUID(dict_value["location_id"]),
        )
