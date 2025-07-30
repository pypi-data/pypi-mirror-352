from abc import ABCMeta

from ed_domain.core.async_repositories.abc_async_generic_repository import \
    ABCAsyncGenericRepository
from ed_domain.core.entities.location import Location


class ABCAsyncLocationRepository(
    ABCAsyncGenericRepository[Location],
    metaclass=ABCMeta,
):
    ...
