# Python D0SL RDM server

Python remote domain model server

## Generate stubs

```shell
python3 -m grpc_tools.protoc -I . --python_out=pyrdms/ --pyi_out=pyrdms/ --grpc_python_out=pyrdms/ proto/protos/rdm.proto

# make import absolute
# OSX:
sed -i '' "s/import rdm_pb2/from . import rdm_pb2/g" pyrdms/proto/rmd_pb2_grpc.py

# Linux:
sed -i "s/import rdm_pb2/from . import rdm_pb2/g" pyrdms/proto/rmd_pb2_grpc.py
```

## Build wheel

```bash
touch ~/.pypirc
chmod 0600 ~/.pypirc

cat <<EOF>~/.pypirc
[distutils]
index-servers = gitea

[gitea]
repository = https://<gitea>/api/packages/<project>/pypi
username = <user>
password = <token>
EOF

poetry build
python3 -m twine upload --repository gitea dist/*
```

Install locally:
```bash
python3 -m pip install dist/*.whl
```

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
