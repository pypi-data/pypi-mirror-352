from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID

from ed_domain.core.aggregate_roots.base_aggregate_root import \
    BaseAggregateRoot
from ed_domain.core.entities.waypoint import WayPoint
from ed_domain.core.value_objects.money import Money


class DeliveryJobStatus(StrEnum):
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class DeliveryJob(BaseAggregateRoot):
    waypoints: list[WayPoint]
    estimated_payment: Money
    estimated_completion_time: datetime
    estimated_distance_in_kms: float
    estimated_time_in_minutes: int
    status: DeliveryJobStatus
    driver_id: Optional[UUID] = None

    def add_waypoint(self, waypoint: WayPoint) -> None:
        self.waypoints.append(waypoint)

    def update_estimated_payment(self, new_payment: Money) -> None:
        self.estimated_payment = new_payment

    def update_estimated_completion_time(self, new_time: datetime) -> None:
        if new_time < datetime.now():
            raise ValueError(
                "Estimated completion time cannot be in the past.")
        self.estimated_completion_time = new_time

    def update_status(self, new_status: DeliveryJobStatus) -> None:
        if new_status not in DeliveryJobStatus:
            raise ValueError(f"Invalid delivery job status: {new_status}")

        self.status = new_status

    def assign_driver(self, driver_id: UUID) -> None:
        if self.status != DeliveryJobStatus.AVAILABLE:
            raise ValueError(
                "Cannot assign driver to a job that is not available.")
        self.driver_id = driver_id
        self.update_status(DeliveryJobStatus.IN_PROGRESS)

    def complete_job(self) -> None:
        if self.status != DeliveryJobStatus.IN_PROGRESS:
            raise ValueError("Cannot complete a job that is not in progress.")
        self.update_status(DeliveryJobStatus.COMPLETED)

    def cancel_job(self) -> None:
        if self.status in {DeliveryJobStatus.COMPLETED, DeliveryJobStatus.CANCELLED}:
            raise ValueError(
                "Cannot cancel a job that is already completed or cancelled."
            )

        self.update_status(DeliveryJobStatus.CANCELLED)

    def fail_job(self) -> None:
        if self.status in {DeliveryJobStatus.COMPLETED, DeliveryJobStatus.CANCELLED}:
            raise ValueError(
                "Cannot fail a job that is already completed or cancelled."
            )

        self.update_status(DeliveryJobStatus.FAILED)

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "waypoints": [waypoint.to_dict() for waypoint in self.waypoints],
            "estimated_payment": self.estimated_payment.to_dict(),
            "estimated_completion_time": self.estimated_completion_time.isoformat(),
            "estimated_distance_in_kms": self.estimated_distance_in_kms,
            "estimated_time_in_minutes": self.estimated_time_in_minutes,
            "status": self.status.value,
            "driver_id": str(self.driver_id) if self.driver_id else None,
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "DeliveryJob":
        base_entity = BaseAggregateRoot.from_dict(dict_value)
        return cls(
            **vars(base_entity),
            waypoints=[WayPoint.from_dict(wp)
                       for wp in dict_value["waypoints"]],
            estimated_payment=Money.from_dict(dict_value["estimated_payment"]),
            estimated_completion_time=datetime.fromisoformat(
                dict_value["estimated_completion_time"]
            ),
            estimated_distance_in_kms=dict_value["estimated_distance_in_kms"],
            estimated_time_in_minutes=dict_value["estimated_time_in_minutes"],
            status=DeliveryJobStatus(dict_value["status"]),
            driver_id=(
                UUID(dict_value["driver_id"]) if dict_value.get(
                    "driver_id") else None
            ),
        )
