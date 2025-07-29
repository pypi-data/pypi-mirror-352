import logging
import grpc

from pyrdms.core.entities import SymbolType

from .app import serve
from pyrdms.client import RDMClient

import argparse
import os

from re import compile, findall

callstrre = compile(r"^([^.\ ]*)\.([^:\ ]*)\:(([^,\ ]+\,)*([^,\ ]*))$")

class HealthServer:
    def health(self) -> bool:
        logging.warning("Health request!")
        return True

class TestRDM:
    def test(self, a: bool, b: bool) -> bool:
        if a == None or b == None:
            return None
        return a and b

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    argsp = argparse.ArgumentParser()

    argsp.add_argument("-a", "--host", type=str, required=True, help="Hostname")
    argsp.add_argument("-p", "--port", type=int, required=False, default=50051, help="Port")

    argsp.add_argument("-c", "--client", action="store_true", help="Work as client")
    argsp.add_argument("-s", "--serve", action="store_true", help="Work as server")

    argsp.add_argument("--call-function", action="store_true", help="Add this flag if you want to call function with --call")
    argsp.add_argument("--call", type=str, help="Client argument: call string in format <model_name>.<predicate_name>:<arg1>,<arg2>,...")
    argsp.add_argument("--list", action="store_true", help="Client argument: list models")

    args = argsp.parse_args()

    if args.serve:
        hs = HealthServer()
        serve(port=args.port, health=hs, TestRDM=TestRDM())
    elif args.client:
        if args.list:
            with RDMClient(f"{args.host}:{args.port}") as cli:
                logging.info(f"Domain models on remote DM server: {cli.list()}")
            os._exit(0)

        if not args.call:
            print("call must not be nil!")
            os._exit(1)
        
        if not callstrre.match(args.call):
            logging.error(f"Invalid call string: {args.call}")
            os._exit(1)
        
        model, predicate, argsstr = callstrre.findall(args.call)[0][:3]

        callargs = []
        for arg in argsstr.split(','):
            if arg == "":
                continue

            if arg in ["True", "False", "true", "false"]:
                callargs.append(arg in ["True", "true"])
            else:
                try:
                    callargs.append(float(arg))
                except ValueError:
                    callargs.append(arg)

        try:
            with RDMClient(f"{args.host}:{args.port}") as cli:
                res = cli(SymbolType.FUNCTION if args.call_function else SymbolType.PREDICATE, model, predicate, *callargs)
            
            logging.info(f"Call result: {res}")
        except grpc.RpcError as ex:
            logging.warning(f"Got rpc error calling function: {ex}")
    else:
        argsp.print_help()
        os._exit(1)