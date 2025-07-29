from typing import Any

import grpc
import logging

from pyrdms.core.entities import SymbolType
from pyrdms.proto import rdm_pb2_grpc, rdm_pb2
from pyrdms.controllers.mappers import Py2Proto, Proto2Py

class RDMClient:
    def __init__(self, host: str = "localhost:50051") -> None:
        self.host = host

    def __enter__(self):
        self._chan = grpc.insecure_channel(self.host)
        self._stub = rdm_pb2_grpc.RemoteModelServiceStub(self._chan)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # if exc_val:
        #     logging.info(f"RDMClient exiting with error: {exc_val.debug_error_string()}")
        self._chan.close()

    def list(self) -> list:
        response: rdm_pb2.ListSignaturesResponse = self._stub.ListSignatures(rdm_pb2.ListSignaturesRequest())
        return response.libraries

    def __call__(self, type: SymbolType, model_name: str, function_name: str, *args: Any, **kwds: Any) -> Any:
        _args = [
            Py2Proto.map(arg)
            for arg in args
        ] + [
            Py2Proto.map(arg)
            for _, arg in kwds.items()
        ]
        
        response: rdm_pb2.CallResult = self._stub.Call(rdm_pb2.CallRequest(
            lib=rdm_pb2.Signature(name=model_name),
            type=rdm_pb2.FUNCTION if type != SymbolType.PREDICATE else rdm_pb2.PREDICATE,
            name=function_name,
            args=_args,
        ))

        return Proto2Py.map(response.value)