from abc import ABCMeta

from ed_domain.core.aggregate_roots import Order
from ed_domain.persistence.async_repositories.abc_async_generic_repository import \
    ABCAsyncGenericRepository


class ABCAsyncOrderRepository(
    ABCAsyncGenericRepository[Order],
    metaclass=ABCMeta,
):
    ...
