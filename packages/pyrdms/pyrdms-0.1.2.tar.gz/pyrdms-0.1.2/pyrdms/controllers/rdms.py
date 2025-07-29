import grpc
from pyrdms.proto import rdm_pb2_grpc as rdm_pb2_grpc
from pyrdms.proto import rdm_pb2 as rdm_pb2

from pyrdms.controllers.mappers import Proto2Py, Py2Proto

from pyrdms.core.services import RDMServer

import logging

class RemoteDomainModelController(rdm_pb2_grpc.RemoteModelService):
    def __init__(self, service: RDMServer) -> None:
        super().__init__()
        self.service = service

    def register_on_server(self, server):
        rdm_pb2_grpc.add_RemoteModelServiceServicer_to_server(self, server)

    def Call(self, request: rdm_pb2.CallRequest, context):
        logging.debug(f"CallPredicate: {request}")
        
        context.set_code(grpc.StatusCode.OK)
        context.set_details('ok')

        try:
            py_result = self.service.call(
                domain_library=request.lib.name,
                symbol_name=request.name,
                args=[
                    Proto2Py.map(e)
                    for e in request.args
                ],
            )

            result = Py2Proto.map(py_result)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Error: {e}')

            logging.error(f"Error occured while processing request: {request}", e)
            return rdm_pb2.CallResult(
                value=rdm_pb2.SemanticValue(
                    type=rdm_pb2.LOGICAL,
                    value=rdm_pb2.BaseSemanticValue(
                        logical_value=rdm_pb2.NONE,
                    )
                ))
        
        logging.info(f"Return result: {result}")
        
        return rdm_pb2.CallResult(value=result)
        
    
    def ListSignatures(self, request: rdm_pb2.ListSignaturesRequest, context):
        logging.debug(f"ListLibraries: {request}")
        context.set_code(grpc.StatusCode.OK)
        context.set_details('ok')

        try:
            py_result = self.service.list_libraries()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'error: {e}')

            logging.error(f"Error occured while processing request: {request}", e)
            return rdm_pb2.ListSignaturesResponse(libraries=[])
        
        return rdm_pb2.ListSignaturesResponse(libraries=[
            Py2Proto.map_meta(lib)
            for lib in py_result
        ])
