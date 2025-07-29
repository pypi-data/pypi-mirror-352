# Python D0SL RDM server

Python remote domain model server


## Example usage

Without decorating: (`some_method` will be exposed as method of "domain model" `NonDecoratedClass`)
```python
from pyrdms import predicate, serve

class NonDecoratedDSL:
    def __init__(self):
        pass

    def a_plus_b_plus_c_plus_d(self, a: int, b: int, c: int, d: int) -> int:
        return a + b + c + d

serve(50051, NonDecoratedDSL=NonDecoratedDSL())
```

With decorators: (`some_method` will be exposed as method of "domain model" `NonDecoratedClass`, `some_other_method` - will NOT be exposed)
```python
from pyrdms import predicate, serve

class DecoratedClass:
    def __init__(self):
        pass
    
    @predicate
    def some_method(self, a: int, b: bool, c: str, d: list) -> bool:
        return True
    
    def some_other_method(self, a: int, b: bool, c: str, d: list) -> bool:
        return True

serve(50051, DecoratedClass=DecoratedClass())
```

### Use as client

Call predicate `start` in model `SomeModel`:
```bash
python3 -m pyrdms -a localhost -c --call SomeModel.start:
```

Call function `start` in model `SomeModel`:
```bash
python3 -m pyrdms -a localhost -c --call SomeModel.start:
```
