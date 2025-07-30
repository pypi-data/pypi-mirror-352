from dataclasses import dataclass
from uuid import UUID

from ed_domain.core.aggregate_roots.base_aggregate_root import \
    BaseAggregateRoot


@dataclass
class Consumer(BaseAggregateRoot):
    user_id: UUID
    first_name: str
    last_name: str
    phone_number: str
    profile_image_url: str
    email: str
    location_id: UUID

    def update_profile_image(self, new_image: str) -> None:
        self.profile_image_url = new_image

    def update_phone_number(self, new_phone_number: str) -> None:
        self.phone_number = new_phone_number

    def update_email(self, new_email: str) -> None:
        self.email = new_email

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "profile_image_url": self.profile_image_url,
            "email": self.email,
            "location_id": str(self.location_id),
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "Consumer":
        base_entity = BaseAggregateRoot.from_dict(dict_value)
        return cls(
            **vars(base_entity),
            user_id=dict_value["user_id"],
            first_name=dict_value["first_name"],
            last_name=dict_value["last_name"],
            phone_number=dict_value["phone_number"],
            profile_image_url=dict_value["profile_image_url"],
            email=dict_value["email"],
            location_id=UUID(dict_value["location_id"]),
        )
