from abc import ABCMeta

from ed_domain.core.aggregate_roots.auth_user import AuthUser
from ed_domain.persistence.async_repositories.abc_async_generic_repository import \
    ABCAsyncGenericRepository


class ABCAsyncAuthUserRepository(
    ABCAsyncGenericRepository[AuthUser],
    metaclass=ABCMeta,
):
    ...
