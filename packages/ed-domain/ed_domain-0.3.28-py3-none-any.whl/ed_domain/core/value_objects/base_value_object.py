from abc import ABC
from dataclasses import dataclass

from ed_domain.core.base_domain_object import BaseDomainObject


@dataclass
class BaseValueObject(BaseDomainObject, ABC):
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return vars(self) == vars(other)

    def __hash__(self):
        return hash(tuple(sorted(vars(self).items())))
