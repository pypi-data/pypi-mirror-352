from abc import ABCMeta

from ed_domain.core.entities import Notification
from ed_domain.persistence.async_repositories.abc_async_generic_repository import \
    ABCAsyncGenericRepository


class ABCAsyncNotificationRepository(
    ABCAsyncGenericRepository[Notification],
    metaclass=ABCMeta,
):
    ...
