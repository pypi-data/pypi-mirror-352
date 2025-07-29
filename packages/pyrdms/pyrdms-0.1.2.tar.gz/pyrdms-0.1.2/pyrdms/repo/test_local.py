from . import ClassDomainModelRepo
from pyrdms.repo.decorators import predicate

from pyrdms.core.entities import DomainFunctionMeta, DomainModelMeta

class SomeClass:
    def __init__(self, a, b, c):
        pass

    def some_method(self, a: int, b: str, c: float, d: list, e: bool) -> int:
        return 123

class SomeClassDecorated:
    def __init__(self, a, b, c):
        pass

    def some_not_decorated_method(self, a: int, b: str, c: float, d: list, e: bool) -> int:
        return 123

    @predicate
    def some_method(self, a: int, b: str, c: float, d: list, e: bool) -> int:
        return 321

def test_local_domain_model():
    repo = ClassDomainModelRepo()
    cl = SomeClass(1,2,3)

    repo.register_model("test", cl)

    assert repo("test", "some_method", 1, "2", 3.0, [], True) == 123
    assert repo.has("test", predicate=DomainFunctionMeta(
        name="some_method",
        args=[int, str, float, list, bool],
        ret=int,
    ))

    assert repo.get_models() == [DomainModelMeta(
        name="test",
        domain_functions={"some_method": DomainFunctionMeta(
            name="some_method",
            args=[int, str, float, list, bool],
            ret=int,
        )}
    )]

    # assert print(repo._dms) != None

def test_local_domain_model_decorated():
    repo = ClassDomainModelRepo()
    cl = SomeClassDecorated(1,2,3)

    repo.register_model("test", cl)

    assert repo("test", "some_method", 1, "2", 3.0, [], True) == 321
    assert repo.has("test", predicate=DomainFunctionMeta(
        name="some_method",
        args=[int, str, float, list, bool],
        ret=int,
    ))

    assert not repo.has("test", predicate=DomainFunctionMeta(
        name="some_not_decorated_method",
        args=[int, str, float, list, bool],
        ret=int,
    ))

    assert repo.get_models() == [DomainModelMeta(
        name="test",
        domain_functions={"some_method": DomainFunctionMeta(
            name="some_method",
            args=[int, str, float, list, bool],
            ret=int,
        )}
    )]

    # assert print(repo._dms) != None
