from abc import ABCMeta
from uuid import UUID

from ed_domain.core.entities import WayPoint
from ed_domain.persistence.async_repositories.abc_async_generic_repository import \
    ABCAsyncGenericRepository
from src.ed_domain.core.entities.waypoint import WaypointStatus


class ABCAsyncWayPointRepository(
    ABCAsyncGenericRepository[WayPoint],
    metaclass=ABCMeta,
):
    async def update_waypoint_status(
        self, id: UUID, status: WaypointStatus
    ) -> bool: ...
