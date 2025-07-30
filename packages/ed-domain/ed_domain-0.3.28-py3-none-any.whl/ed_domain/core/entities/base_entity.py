from dataclasses import dataclass
from datetime import datetime

from ed_domain.core.base_domain_object import BaseDomainObject


@dataclass
class BaseEntity(BaseDomainObject):
    create_datetime: datetime
    update_datetime: datetime
    deleted: bool

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "create_datetime": self.create_datetime.isoformat(),
            "update_datetime": self.update_datetime.isoformat(),
            "deleted": self.deleted,
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "BaseDomainObject":
        base_domain_object = BaseDomainObject.from_dict(dict_value)
        return cls(
            **vars(base_domain_object),
            create_datetime=datetime.fromisoformat(
                dict_value["create_datetime"]),
            update_datetime=datetime.fromisoformat(
                dict_value["update_datetime"]),
            deleted=dict_value["deleted"],
        )
