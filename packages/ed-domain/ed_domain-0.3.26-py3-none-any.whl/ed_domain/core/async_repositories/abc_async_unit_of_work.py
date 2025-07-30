from abc import ABCMeta, abstractmethod

from ed_domain.core.async_repositories.abc_async_auth_user_repository import \
    ABCAsyncAuthUserRepository
from ed_domain.core.async_repositories.abc_async_bill_repository import \
    ABCAsyncBillRepository
from ed_domain.core.async_repositories.abc_async_business_repository import \
    ABCAsyncBusinessRepository
from ed_domain.core.async_repositories.abc_async_car_repository import \
    ABCAsyncCarRepository
from ed_domain.core.async_repositories.abc_async_consumer_repository import \
    ABCAsyncConsumerRepository
from ed_domain.core.async_repositories.abc_async_delivery_job_repository import \
    ABCAsyncDeliveryJobRepository
from ed_domain.core.async_repositories.abc_async_driver_repository import \
    ABCAsyncDriverRepository
from ed_domain.core.async_repositories.abc_async_location_repository import \
    ABCAsyncLocationRepository
from ed_domain.core.async_repositories.abc_async_notification_repository import \
    ABCAsyncNotificationRepository
from ed_domain.core.async_repositories.abc_async_order_repository import \
    ABCAsyncOrderRepository
from ed_domain.core.async_repositories.abc_async_otp_repository import \
    ABCAsyncOtpRepository


class ABCAsyncUnitOfWork(metaclass=ABCMeta):
    @property
    @abstractmethod
    def bill_repository(self) -> ABCAsyncBillRepository: ...

    @property
    @abstractmethod
    def business_repository(self) -> ABCAsyncBusinessRepository: ...

    @property
    @abstractmethod
    def car_repository(self) -> ABCAsyncCarRepository: ...

    @property
    @abstractmethod
    def consumer_repository(self) -> ABCAsyncConsumerRepository: ...

    @property
    @abstractmethod
    def delivery_job_repository(self) -> ABCAsyncDeliveryJobRepository: ...

    @property
    @abstractmethod
    def driver_repository(self) -> ABCAsyncDriverRepository: ...

    @property
    @abstractmethod
    def location_repository(self) -> ABCAsyncLocationRepository: ...

    @property
    @abstractmethod
    def notification_repository(self) -> ABCAsyncNotificationRepository: ...

    @property
    @abstractmethod
    def order_repository(self) -> ABCAsyncOrderRepository: ...

    @property
    @abstractmethod
    def otp_repository(self) -> ABCAsyncOtpRepository: ...

    @property
    @abstractmethod
    def auth_user_repository(self) -> ABCAsyncAuthUserRepository: ...
