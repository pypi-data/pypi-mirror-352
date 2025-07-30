from dataclasses import dataclass
from uuid import UUID

from ed_domain.core.aggregate_roots.base_aggregate_root import \
    BaseAggregateRoot


@dataclass
class Admin(BaseAggregateRoot):
    user_id: UUID
    first_name: str
    last_name: str
    phone_number: str
    email: str

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "user_id": str(self.user_id),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "email": self.email,
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "Admin":
        base_entity = BaseAggregateRoot.from_dict(dict_value)
        return cls(
            **vars(base_entity),
            user_id=UUID(dict_value["user_id"]),
            first_name=dict_value["first_name"],
            last_name=dict_value["last_name"],
            phone_number=dict_value["phone_number"],
            email=dict_value["email"],
        )
