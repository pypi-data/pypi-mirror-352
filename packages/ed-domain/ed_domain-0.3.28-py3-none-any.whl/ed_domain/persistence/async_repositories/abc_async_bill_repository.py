from abc import ABCMeta

from ed_domain.core.entities.bill import Bill
from ed_domain.persistence.async_repositories.abc_async_generic_repository import \
    ABCAsyncGenericRepository


class ABCAsyncBillRepository(
    ABCAsyncGenericRepository[Bill],
    metaclass=ABCMeta,
):
    ...
