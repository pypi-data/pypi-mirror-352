from typing import List, Mapping
from dataclasses import dataclass
from enum import Enum

class SymbolType(Enum):
    FUNCTION = 1
    PREDICATE = 2

@dataclass
class DomainFunctionMeta:
    name: str
    args: List[type]
    ret: type

@dataclass
class DomainModelMeta:
    name: str
    domain_functions: Mapping[str, DomainFunctionMeta]
