from abc import ABCMeta

from ed_domain.core.aggregate_roots.consumer import Consumer
from ed_domain.persistence.async_repositories.abc_async_generic_repository import \
    ABCAsyncGenericRepository


class ABCAsyncConsumerRepository(
    ABCAsyncGenericRepository[Consumer],
    metaclass=ABCMeta,
):
    ...
