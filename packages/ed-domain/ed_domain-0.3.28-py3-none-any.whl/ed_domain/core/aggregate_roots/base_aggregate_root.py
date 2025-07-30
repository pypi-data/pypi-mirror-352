from dataclasses import dataclass

from ed_domain.core.entities.base_entity import BaseEntity


@dataclass
class BaseAggregateRoot(BaseEntity):
    ...
