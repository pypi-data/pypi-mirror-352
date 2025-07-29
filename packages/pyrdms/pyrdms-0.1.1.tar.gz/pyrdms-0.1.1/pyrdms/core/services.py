from typing import Union

from pyrdms.repo import DomainModelRepo

import logging

class RDMServer:
    def __init__(self, repo: DomainModelRepo) -> None:
        self._repo = repo

    def call(self, domain_library: str, symbol_name: str, args: list) -> Union[int, float, str, bool, list]:
        logging.info(f"Calling predicate {domain_library}.{symbol_name}({args})")

        return self._repo(domain_library, symbol_name, *args)
    
    def list_libraries(self) -> map:
        models = self._repo.get_models()

        logging.info(f"Models: {models}")

        return models
