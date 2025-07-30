from dataclasses import dataclass
from uuid import UUID


@dataclass
class BaseDomainObject:
    id: UUID

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "BaseDomainObject":
        return cls(
            id=UUID(dict_value["id"]),
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
