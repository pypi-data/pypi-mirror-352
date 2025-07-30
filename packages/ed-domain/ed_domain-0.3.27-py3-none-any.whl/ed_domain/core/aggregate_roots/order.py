from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID

from ed_domain.core.aggregate_roots.base_aggregate_root import \
    BaseAggregateRoot
from ed_domain.core.entities.bill import Bill, BillStatus
from ed_domain.core.entities.parcel import Parcel


class OrderStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PICKED_UP = "picked_up"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class Order(BaseAggregateRoot):
    consumer_id: UUID
    business_id: UUID
    latest_time_of_delivery: datetime
    bill: Bill
    parcel: Parcel
    order_status: OrderStatus
    driver_id: Optional[UUID] = None

    def update_status(self, new_status: OrderStatus) -> None:
        if new_status not in OrderStatus:
            raise ValueError(f"Invalid order status: {new_status}")

        self.order_status = new_status

    def update_bill_status(self, new_status: str) -> None:
        if new_status not in BillStatus:
            raise ValueError(f"Invalid bill status: {new_status}")

        self.bill.bill_status = BillStatus(new_status)

    def assign_driver(self, driver_id: UUID) -> None:
        if self.order_status != OrderStatus.PENDING:
            raise ValueError(
                "Cannot assign driver to an order that is not pending.")
        self.driver_id = driver_id
        self.update_status(OrderStatus.IN_PROGRESS)

    def complete_order(self) -> None:
        if self.order_status != OrderStatus.IN_PROGRESS:
            raise ValueError(
                "Cannot complete an order that is not in progress.")
        self.update_status(OrderStatus.COMPLETED)

    def cancel_order(self) -> None:
        if self.order_status in {OrderStatus.COMPLETED, OrderStatus.CANCELLED}:
            raise ValueError(
                "Cannot cancel an order that is already completed or cancelled."
            )
        self.update_status(OrderStatus.CANCELLED)

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "consumer_id": self.consumer_id,
            "business_id": self.business_id,
            "bill_id": self.bill.to_dict(),
            "latest_time_of_delivery": self.latest_time_of_delivery,
            "parcel": self.parcel.to_dict(),
            "order_status": self.order_status.value,
            "driver_id": self.driver_id if self.driver_id else None,
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "Order":
        base_entity = BaseAggregateRoot.from_dict(dict_value)
        return cls(
            **vars(base_entity),
            consumer_id=UUID(dict_value["consumer_id"]),
            business_id=UUID(dict_value["business_id"]),
            bill=dict_value["bill"],
            latest_time_of_delivery=datetime.fromisoformat(
                dict_value["latest_time_of_delivery"]
            ),
            parcel=Parcel.from_dict(dict_value["parcel"]),
            order_status=OrderStatus(dict_value["order_status"]),
            driver_id=(
                UUID(dict_value["driver_id"]) if dict_value.get(
                    "driver_id") else None
            ),
        )
