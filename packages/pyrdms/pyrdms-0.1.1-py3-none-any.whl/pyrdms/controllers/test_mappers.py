from .mappers import Proto2Py, Py2Proto

from pyrdms.proto import rdm_pb2_grpc as rdm_pb2_grpc
from pyrdms.proto import rdm_pb2 as rdm_pb2

from pyrdms.core.entities import DomainModelMeta, DomainFunctionMeta

def test_map_meta():
    meta = DomainModelMeta(
        name="some_domain_model",
        domain_functions={
            "test1": DomainFunctionMeta(
                name="test1",
                args=[bool,int,str,list],
                ret=bool,
            )
        }
    )

    proto = Py2Proto.map_meta(meta)

    assert proto.name == meta.name
    assert proto.descriptors["test1"].name == "test1"
    assert proto.descriptors["test1"].return_value == rdm_pb2.LOGICAL
    assert len(proto.descriptors["test1"].arguments) == 4
    assert proto.descriptors["test1"].arguments[0] == rdm_pb2.LOGICAL
    assert proto.descriptors["test1"].arguments[1] == rdm_pb2.NUMERICAL
    assert proto.descriptors["test1"].arguments[2] == rdm_pb2.STRING
    assert proto.descriptors["test1"].arguments[3] == rdm_pb2.LIST

def test_map_int():
    val = Py2Proto.map(1)
    assert val.type == rdm_pb2.NUMERICAL
    assert val.value.numerical_value == 1.0

    assert Proto2Py.map(val) == 1.0

def test_map_float():
    val = Py2Proto.map(1.23)
    assert val.type == rdm_pb2.NUMERICAL
    assert abs(val.value.numerical_value - 1.23) < 1e-9

    assert abs(Proto2Py.map(val) - 1.23) < 1e-9

def test_map_str():
    val = Py2Proto.map("123")
    assert val.type == rdm_pb2.STRING
    assert val.value.string_value == "123"

    assert Proto2Py.map(val) == "123"

def test_map_bool():
    val1 = Py2Proto.map(None)
    val2 = Py2Proto.map(True)

    assert val1.type == rdm_pb2.LOGICAL
    assert val1.value.logical_value == rdm_pb2.NONE

    assert val2.type == rdm_pb2.LOGICAL
    assert val2.value.logical_value == rdm_pb2.TRUE

    assert Proto2Py.map(val1) == None
    assert Proto2Py.map(val2) == True

def test_map_list():
    some_list = [1, True, "123"]

    val = Py2Proto.map(some_list)

    assert val.type == rdm_pb2.LIST
    assert len(val.list_of_values.data) == 3

    assert val.list_of_values.data[0].type == rdm_pb2.NUMERICAL
    assert val.list_of_values.data[1].type == rdm_pb2.LOGICAL
    assert val.list_of_values.data[2].type == rdm_pb2.STRING

    assert val.list_of_values.data[0].value.numerical_value == 1.0
    assert val.list_of_values.data[1].value.logical_value == rdm_pb2.TRUE
    assert val.list_of_values.data[2].value.string_value == "123" 

    assert Proto2Py.map(val) == some_list

def test_map_list_of_lists():
    some_list = [1, True, "123", [1, True, "123"]]

    val = Py2Proto.map(some_list)

    assert val.type == rdm_pb2.LIST
    assert len(val.list_of_values.data) == 4

    assert val.list_of_values.data[0].type == rdm_pb2.NUMERICAL
    assert val.list_of_values.data[1].type == rdm_pb2.LOGICAL
    assert val.list_of_values.data[2].type == rdm_pb2.STRING

    assert val.list_of_values.data[0].value.numerical_value == 1.0
    assert val.list_of_values.data[1].value.logical_value == rdm_pb2.TRUE
    assert val.list_of_values.data[2].value.string_value == "123" 

    assert val.list_of_values.data[3].type == rdm_pb2.LIST
    assert len(val.list_of_values.data[3].list_of_values.data) == 3

    assert val.list_of_values.data[3].list_of_values.data[0].type == rdm_pb2.NUMERICAL
    assert val.list_of_values.data[3].list_of_values.data[1].type == rdm_pb2.LOGICAL
    assert val.list_of_values.data[3].list_of_values.data[2].type == rdm_pb2.STRING

    assert val.list_of_values.data[3].list_of_values.data[0].value.numerical_value == 1.0
    assert val.list_of_values.data[3].list_of_values.data[1].value.logical_value == rdm_pb2.TRUE
    assert val.list_of_values.data[3].list_of_values.data[2].value.string_value == "123" 

    assert Proto2Py.map(val) == some_list