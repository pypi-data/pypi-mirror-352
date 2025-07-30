from dataclasses import dataclass
from typing import Optional

from ed_domain.core.aggregate_roots.base_aggregate_root import \
    BaseAggregateRoot


@dataclass
class AuthUser(BaseAggregateRoot):
    first_name: str
    last_name: str
    password_hash: str
    verified: bool
    logged_in: bool
    email: Optional[str] = None
    phone_number: Optional[str] = None

    def log_out(self) -> None:
        self.logged_in = False

    def log_in(self) -> None:
        self.logged_in = True

    def update_phone_number(self, new_phone_number: str) -> None:
        self.phone_number = new_phone_number

    def update_email(self, new_email: str) -> None:
        self.email = new_email

    def update_password_hash(self, new_password_hash: str) -> None:
        self.password_hash = new_password_hash

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "password_hash": self.password_hash,
            "verified": self.verified,
            "logged_in": self.logged_in,
            "email": self.email,
            "phone_number": self.phone_number,
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "AuthUser":
        base_entity = BaseAggregateRoot.from_dict(dict_value)
        return cls(
            **vars(base_entity),
            first_name=dict_value["first_name"],
            last_name=dict_value["last_name"],
            password_hash=dict_value["password_hash"],
            verified=dict_value["verified"],
            logged_in=dict_value["logged_in"],
            email=dict_value.get("email"),
            phone_number=dict_value.get("phone_number"),
        )
