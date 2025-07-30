from abc import ABC
from typing import Type, TypeVar

ModelType = TypeVar("ModelType")
FilterType = TypeVar("FilterType")


class AbstractSQLAlchemyService(ABC):
    model_cls: Type[ModelType]


class AbstractORMSQLAlchemyService(AbstractSQLAlchemyService):
    filter_cls: Type[FilterType]
