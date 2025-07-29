from concurrent import futures
import grpc

from typing import Mapping, Any, Callable
from functools import partial

import logging

from pyrdms.controllers import RemoteDomainModelController
from pyrdms.core.services import RDMServer
from pyrdms.repo import ClassDomainModelRepo

def start_server(port: int, **models) -> grpc.Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    repo = ClassDomainModelRepo()

    for name, model in models.items():
        repo.register_model(name, model)

    svc = RDMServer(repo)

    controller = RemoteDomainModelController(svc)

    controller.register_on_server(server)

    server.add_insecure_port(f'[::]:{port}')
    server.start()

    logging.warning(f"Server started, listening on {port}")

    return server

def serve(port: int, **models):
    server = start_server(port, **models)
    server.wait_for_termination()

def serve_background(port: int, **models) -> Callable[[], None]:
    server = start_server(port, **models)
    return partial(server.stop, grace=3)
