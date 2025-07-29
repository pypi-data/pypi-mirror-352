from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Logical(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FALSE: _ClassVar[Logical]
    TRUE: _ClassVar[Logical]
    NONE: _ClassVar[Logical]

class SemanticValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STRING: _ClassVar[SemanticValueType]
    NUMERICAL: _ClassVar[SemanticValueType]
    LOGICAL: _ClassVar[SemanticValueType]
    LIST: _ClassVar[SemanticValueType]
    OBJECT: _ClassVar[SemanticValueType]

class SymbolType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PREDICATE: _ClassVar[SymbolType]
    FUNCTION: _ClassVar[SymbolType]
FALSE: Logical
TRUE: Logical
NONE: Logical
STRING: SemanticValueType
NUMERICAL: SemanticValueType
LOGICAL: SemanticValueType
LIST: SemanticValueType
OBJECT: SemanticValueType
PREDICATE: SymbolType
FUNCTION: SymbolType

class BaseSemanticValue(_message.Message):
    __slots__ = ("string_value", "numerical_value", "logical_value")
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    NUMERICAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    LOGICAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    string_value: str
    numerical_value: float
    logical_value: Logical
    def __init__(self, string_value: _Optional[str] = ..., numerical_value: _Optional[float] = ..., logical_value: _Optional[_Union[Logical, str]] = ...) -> None: ...

class ListOfSemanticValues(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[SemanticValue]
    def __init__(self, data: _Optional[_Iterable[_Union[SemanticValue, _Mapping]]] = ...) -> None: ...

class SemanticObject(_message.Message):
    __slots__ = ("iri", "data")
    IRI_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    iri: str
    data: _struct_pb2.Struct
    def __init__(self, iri: _Optional[str] = ..., data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class SemanticValue(_message.Message):
    __slots__ = ("type", "value", "list_of_values", "object_value")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    LIST_OF_VALUES_FIELD_NUMBER: _ClassVar[int]
    OBJECT_VALUE_FIELD_NUMBER: _ClassVar[int]
    type: SemanticValueType
    value: BaseSemanticValue
    list_of_values: ListOfSemanticValues
    object_value: SemanticObject
    def __init__(self, type: _Optional[_Union[SemanticValueType, str]] = ..., value: _Optional[_Union[BaseSemanticValue, _Mapping]] = ..., list_of_values: _Optional[_Union[ListOfSemanticValues, _Mapping]] = ..., object_value: _Optional[_Union[SemanticObject, _Mapping]] = ...) -> None: ...

class SymbolDescriptor(_message.Message):
    __slots__ = ("type", "name", "arguments", "return_value")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    RETURN_VALUE_FIELD_NUMBER: _ClassVar[int]
    type: SymbolType
    name: str
    arguments: _containers.RepeatedScalarFieldContainer[SemanticValueType]
    return_value: SemanticValueType
    def __init__(self, type: _Optional[_Union[SymbolType, str]] = ..., name: _Optional[str] = ..., arguments: _Optional[_Iterable[_Union[SemanticValueType, str]]] = ..., return_value: _Optional[_Union[SemanticValueType, str]] = ...) -> None: ...

class Signature(_message.Message):
    __slots__ = ("fqn", "name", "descriptors")
    class DescriptorsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: SymbolDescriptor
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[SymbolDescriptor, _Mapping]] = ...) -> None: ...
    FQN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTORS_FIELD_NUMBER: _ClassVar[int]
    fqn: str
    name: str
    descriptors: _containers.MessageMap[str, SymbolDescriptor]
    def __init__(self, fqn: _Optional[str] = ..., name: _Optional[str] = ..., descriptors: _Optional[_Mapping[str, SymbolDescriptor]] = ...) -> None: ...

class Caller(_message.Message):
    __slots__ = ("modelName", "name")
    MODELNAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    modelName: str
    name: str
    def __init__(self, modelName: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class CalculationContext(_message.Message):
    __slots__ = ("caller",)
    CALLER_FIELD_NUMBER: _ClassVar[int]
    caller: Caller
    def __init__(self, caller: _Optional[_Union[Caller, _Mapping]] = ...) -> None: ...

class ListSignaturesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListSignaturesResponse(_message.Message):
    __slots__ = ("libraries",)
    LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    libraries: _containers.RepeatedCompositeFieldContainer[Signature]
    def __init__(self, libraries: _Optional[_Iterable[_Union[Signature, _Mapping]]] = ...) -> None: ...

class CallRequest(_message.Message):
    __slots__ = ("lib", "type", "name", "args", "ctx")
    LIB_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    CTX_FIELD_NUMBER: _ClassVar[int]
    lib: Signature
    type: SymbolType
    name: str
    args: _containers.RepeatedCompositeFieldContainer[SemanticValue]
    ctx: CalculationContext
    def __init__(self, lib: _Optional[_Union[Signature, _Mapping]] = ..., type: _Optional[_Union[SymbolType, str]] = ..., name: _Optional[str] = ..., args: _Optional[_Iterable[_Union[SemanticValue, _Mapping]]] = ..., ctx: _Optional[_Union[CalculationContext, _Mapping]] = ...) -> None: ...

class CallResult(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: SemanticValue
    def __init__(self, value: _Optional[_Union[SemanticValue, _Mapping]] = ...) -> None: ...
