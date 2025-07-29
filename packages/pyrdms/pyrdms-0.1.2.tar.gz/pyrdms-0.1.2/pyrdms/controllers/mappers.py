from typing import Union, List

from pyrdms.proto import rdm_pb2_grpc as rdm_pb2_grpc
from pyrdms.proto import rdm_pb2 as rdm_pb2

from pyrdms.core.entities import DomainModelMeta

class Proto2Py:
    @staticmethod
    def _map_string(v: rdm_pb2.SemanticValue) -> str:
        assert v.type == rdm_pb2.STRING

        return v.value.string_value

    @staticmethod
    def _map_num(v: rdm_pb2.SemanticValue) -> float:
        assert v.type == rdm_pb2.NUMERICAL

        return v.value.numerical_value
    
    @staticmethod
    def _map_bool(v: rdm_pb2.SemanticValue) -> bool:
        assert v.type == rdm_pb2.LOGICAL

        return None if v.value.logical_value == rdm_pb2.NONE else v.value.logical_value == rdm_pb2.TRUE
    
    @staticmethod
    def _map_list(l: rdm_pb2.SemanticValue) -> list:
        assert l.type == rdm_pb2.LIST

        return [Proto2Py.map(e) for e in l.list_of_values.data]

    @staticmethod
    def map(value: rdm_pb2.SemanticValue) -> Union[list, int, float, str, bool]:
        match value.type:
            case rdm_pb2.LOGICAL:
                return Proto2Py._map_bool(value)
            case rdm_pb2.NUMERICAL:
                return Proto2Py._map_num(value)
            case rdm_pb2.STRING:
                return Proto2Py._map_string(value)
            case rdm_pb2.LIST:
                return Proto2Py._map_list(value)
            case _:
                raise TypeError(f"wrong value type: {type(value.type)}")


class Py2Proto:
    @staticmethod
    def _map_string(s: str) -> rdm_pb2.SemanticValue:
        assert isinstance(s, str)

        return rdm_pb2.SemanticValue(type=rdm_pb2.STRING, value=rdm_pb2.BaseSemanticValue(string_value=s))

    @staticmethod
    def _map_num(s: Union[int, float]) -> rdm_pb2.SemanticValue:
        assert isinstance(s, int) or isinstance(s, float)

        return rdm_pb2.SemanticValue(type=rdm_pb2.NUMERICAL, value=rdm_pb2.BaseSemanticValue(numerical_value=s))
    
    @staticmethod
    def _map_bool(b: bool) -> rdm_pb2.SemanticValue:
        assert b == None or isinstance(b, bool)

        if b == None:
            return rdm_pb2.SemanticValue(type=rdm_pb2.LOGICAL, value=rdm_pb2.BaseSemanticValue(logical_value=rdm_pb2.NONE))
        
        return rdm_pb2.SemanticValue(type=rdm_pb2.LOGICAL, value=rdm_pb2.BaseSemanticValue(logical_value=rdm_pb2.TRUE if b else rdm_pb2.FALSE))

    @staticmethod
    def _map_list(l: List) -> rdm_pb2.SemanticValue:
        return rdm_pb2.SemanticValue(
                type=rdm_pb2.LIST,
                list_of_values=rdm_pb2.ListOfSemanticValues(
                    data=[
                        Py2Proto.map(v)
                        for v in l
                    ]
                )
            )

    @staticmethod
    def _map_type(t: type) -> rdm_pb2.SemanticValueType:
        if t == bool:
            return rdm_pb2.LOGICAL
        elif t == int or t == float:
            return rdm_pb2.NUMERICAL
        elif t == str:
            return rdm_pb2.STRING
        elif t == list or t == tuple:
            return rdm_pb2.LIST
        else:
            raise TypeError(f"wrong value type: {t}")


    @staticmethod
    def map_meta(value: DomainModelMeta) -> rdm_pb2.Signature:
        return rdm_pb2.Signature(
            fqn=value.name, # TODO: change to real fqn
            name=value.name,
            descriptors={
                k: rdm_pb2.SymbolDescriptor(
                    type=rdm_pb2.FUNCTION,
                    name=v.name,
                    arguments=[Py2Proto._map_type(a) for a in v.args],
                    return_value=Py2Proto._map_type(v.ret),
                )
                for k, v in value.domain_functions.items()
            }
        )

    @staticmethod
    def map(value: Union[List[int], List[bool], List[float], List[str], int, float, str, bool]) -> rdm_pb2.SemanticValue:
        if value == None or isinstance(value, bool):
            return Py2Proto._map_bool(value)
        elif isinstance(value, int) or isinstance(value, float):
            return Py2Proto._map_num(value)
        elif isinstance(value, str):
            return Py2Proto._map_string(value)
        elif isinstance(value, list) or isinstance(value, tuple):
            return Py2Proto._map_list(value)
        else:
            raise TypeError(f"wrong value type: {type(value)}")

