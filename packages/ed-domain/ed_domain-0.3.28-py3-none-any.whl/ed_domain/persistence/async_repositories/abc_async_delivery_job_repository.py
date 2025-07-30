from abc import ABCMeta

from ed_domain.core.aggregate_roots.delivery_job import DeliveryJob
from ed_domain.persistence.async_repositories.abc_async_generic_repository import \
    ABCAsyncGenericRepository


class ABCAsyncDeliveryJobRepository(
    ABCAsyncGenericRepository[DeliveryJob],
    metaclass=ABCMeta,
):
    ...
