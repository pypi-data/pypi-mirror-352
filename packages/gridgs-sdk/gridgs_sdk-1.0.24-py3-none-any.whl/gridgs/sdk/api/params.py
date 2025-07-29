from abc import abstractmethod, ABC
from dataclasses import dataclass
from enum import Enum

class QueryParams(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        pass

@dataclass(frozen=True)
class PaginatedQueryParams(QueryParams):
    offset: int  = 0
    limit: int | None = None

    def to_dict(self) -> dict:
        return {'offset': self.offset, 'limit': self.limit}


class SortOrder(Enum):
    ASC = 'asc'
    DESC = 'desc'


@dataclass(frozen=True)
class SortQueryParam(QueryParams):
    sort_by: Enum | None = None
    sort_order: SortOrder = SortOrder.ASC

    def to_dict(self) -> dict:
        return {'sort_by': f'{self.sort_by.value}.{self.sort_order.value}' if isinstance(self.sort_by, Enum) else None}
