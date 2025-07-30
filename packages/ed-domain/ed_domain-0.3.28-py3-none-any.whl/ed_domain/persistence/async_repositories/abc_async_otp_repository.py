from abc import ABCMeta

from ed_domain.core.entities import Otp
from ed_domain.persistence.async_repositories.abc_async_generic_repository import \
    ABCAsyncGenericRepository


class ABCAsyncOtpRepository(
    ABCAsyncGenericRepository[Otp],
    metaclass=ABCMeta,
):
    ...
