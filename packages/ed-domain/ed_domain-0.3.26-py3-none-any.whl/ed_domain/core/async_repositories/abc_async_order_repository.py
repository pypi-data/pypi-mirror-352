from abc import ABCMeta

from ed_domain.core.async_repositories.abc_async_generic_repository import \
    ABCAsyncGenericRepository
from ed_domain.core.entities.order import Order


class ABCAsyncOrderRepository(
    ABCAsyncGenericRepository[Order],
    metaclass=ABCMeta,
):
    ...
