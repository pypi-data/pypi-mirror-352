from abc import ABCMeta

from ed_domain.core.entities import Parcel
from ed_domain.persistence.async_repositories.abc_async_generic_repository import \
    ABCAsyncGenericRepository


class ABCAsyncParcelRepository(
    ABCAsyncGenericRepository[Parcel],
    metaclass=ABCMeta,
):
    ...
