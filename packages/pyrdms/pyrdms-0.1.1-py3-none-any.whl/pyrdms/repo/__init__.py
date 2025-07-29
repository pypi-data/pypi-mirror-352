from abc import ABC, ABCMeta, abstractmethod
from typing import Any, List

from pyrdms.core.entities import DomainFunctionMeta, DomainModelMeta

class DomainModelRepo(ABC):
    @abstractmethod
    def register_model(name: str, model: Any):
        raise NotImplementedError()

    @abstractmethod
    def __call__(self, model_name: str, predicate_name: str, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def has(self, model_name: str, predicate: DomainFunctionMeta) -> bool:
        raise NotImplementedError()
    
    @abstractmethod
    def get_models(self) -> List[DomainModelMeta]:
        raise NotImplementedError()


from .local import ClassDomainModelRepo
from .util import get_decorators
from .decorators import predicate
