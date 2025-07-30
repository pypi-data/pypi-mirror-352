from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from ed_domain.core.aggregate_roots.base_aggregate_root import \
    BaseAggregateRoot
from ed_domain.core.value_objects.money import Money
from ed_domain.core.entities.base_entity import BaseEntity


class BillStatus(StrEnum):
    PENDING = "pending"
    WITH_DRIVER = "with_driver"
    DONE = "done"
    CANCELLED = "cancelled"


@dataclass
class Bill(BaseEntity):
    amount: Money
    bill_status: BillStatus
    due_date: datetime

    def update_status(self, new_status: BillStatus):
        if new_status not in BillStatus:
            raise ValueError(f"Invalid bill status: {new_status}")

        self.bill_status = new_status

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "amount": self.amount.to_dict(),
            "bill_status": self.bill_status.value,
            "due_date": self.due_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "Bill":
        base_entity = BaseAggregateRoot.from_dict(dict_value)
        return cls(
            **vars(base_entity),
            amount=Money.from_dict(dict_value["amount"]),
            bill_status=BillStatus(dict_value["bill_status"]),
            due_date=datetime.fromisoformat(dict_value["due_date"]),
        )
