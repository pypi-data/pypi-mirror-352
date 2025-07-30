from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from ed_domain.core.entities.base_entity import BaseEntity


class NotificationType(StrEnum):
    SMS = "SMS"
    EMAIL = "EMAIL"
    IN_APP = "IN_APP"


@dataclass
class Notification(BaseEntity):
    user_id: UUID
    notification_type: NotificationType
    message: str
    read_status: bool

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "user_id": str(self.user_id),
            "notification_type": self.notification_type.value,
            "message": self.message,
            "read_status": self.read_status,
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "Notification":
        base_entity = BaseEntity.from_dict(dict_value)
        return cls(
            **vars(base_entity),
            user_id=UUID(dict_value["user_id"]),
            notification_type=NotificationType(
                dict_value["notification_type"]),
            message=dict_value["message"],
            read_status=dict_value["read_status"],
        )
