from abc import ABCMeta

from ed_domain.core.entities.car import Car
from ed_domain.persistence.async_repositories.abc_async_generic_repository import \
    ABCAsyncGenericRepository


class ABCAsyncCarRepository(
    ABCAsyncGenericRepository[Car],
    metaclass=ABCMeta,
):
    ...
