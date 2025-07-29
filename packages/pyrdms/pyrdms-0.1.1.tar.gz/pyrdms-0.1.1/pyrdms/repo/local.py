from . import DomainModelRepo
from pyrdms.repo.decorators import predicate
from pyrdms.repo.util import get_decorators

import inspect
from typing import Any, Mapping

from pyrdms.core.entities import DomainFunctionMeta, DomainModelMeta
from pyrdms.exceptions import PredicateNotFoundException

class ClassDomainModelRepo(DomainModelRepo):
    def __init__(self) -> None:
        super().__init__()
        self._dms = {}
        self._signs = {}
        self._models = {}
    
    @staticmethod
    def _get_model_decorated_methods(model: object):
        decorators = get_decorators(model.__class__)
        return [
            method_name
            for method_name, decorators in decorators.items() if 'predicate' in decorators
        ]
    
    @staticmethod
    def _method_search_predicate(object: object):
        """Returns if object is method or if object is method decorated with predicate"""
        return inspect.ismethod(object) or isinstance(object, predicate)
    
    def register_model(self, name: str, model):
        # Проверяем, что нам передали экземпляр класса
        assert not isinstance(model, type)

        # todo: тут надо больше проверок, чтобы не выстрелить в ногу
        self._dms[name] = {}
        self._signs[name] = {}

        decorated_methods = self._get_model_decorated_methods(model)

        for method_name, method in inspect.getmembers(model, self._method_search_predicate):
            print(f"Check {method_name}")
            # Нас не интересуют магические методы и, при наличии декораторов, интересуют только декорированные с помощью 'predicate'
            if not method_name.startswith("__") and (not decorated_methods or method_name in decorated_methods):
                self._dms[name][method_name] = method

                if method_name not in decorated_methods:
                    sign = inspect.signature(method)
                else:
                    # get underlying function of predicate decorator
                    sign = inspect.signature(method.function)

                    # model to use as self parameter to method
                    self._models[name] = model

                print(f"register method with name {method_name} and signature {sign} params: {list(sign.parameters.items())} of {model}")
                
                self._signs[name][method_name] = DomainFunctionMeta(
                    name=method_name,
                    # for some reason self is returned when method is decorated as a parameter here
                    args=[v.annotation for k, v in sign.parameters.items() if k != 'self'],
                    ret=sign.return_annotation,
                )
    
    def __call__(self, model_name: str, predicate_name: str, *args: Any, **kwds: Any) -> Any:
        if model_name not in self._dms:
            raise PredicateNotFoundException(model_name)
        
        if predicate_name not in self._dms[model_name]:
            raise PredicateNotFoundException(model_name)
        
        if model_name not in self._models:
            # no need to pass self parameter, because method is already IS bound method of class
            return self._dms[model_name][predicate_name](*args, **kwds)

        # method is decorated in class, so we need to pass the model itself as first parameter 
        return self._dms[model_name][predicate_name](self._models[model_name], *args, **kwds)

    def has(self, model_name: str, predicate: DomainFunctionMeta) -> bool:
        return model_name in self._dms and \
            predicate.name in self._dms[model_name] and \
            self._signs[model_name][predicate.name] == predicate
    
    def get_models(self) -> Mapping[str, DomainModelMeta]:
        meta = []

        for model_name in self._dms.keys():
            meta.append(
                DomainModelMeta(
                    name=model_name,
                    domain_functions={
                        predicate: descr
                        for predicate, descr in self._signs[model_name].items()
                    },
                )
            )

        return meta
