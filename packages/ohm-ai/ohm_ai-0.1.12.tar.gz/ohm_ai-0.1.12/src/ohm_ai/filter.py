from enum import Enum
from dataclasses import dataclass
from typing import Union, List


class OhmFilterOperator(Enum):
  LT = 'lt'
  LTE = 'lte'
  EQ = 'equals'
  GTE = 'gte'
  GT = 'gt'
  CONTAINS = 'contains'
  NOT = 'not'
  STARTS_WITH = 'startsWith'
  ENDS_WITH = 'endsWith'
  SEARCH = 'search'
  NOT_CONTAINS = 'notContains'
  IN = 'in'
  NOT_IN = 'notIn'
  IS_NULL = 'isNull'
  IS_NOT_NULL = 'isNotNull'
  HAS = 'has'
  HAS_EVERY = 'hasEvery'
  HAS_SOME = 'hasSome'


class OhmFilterGroupType(Enum):
  AND = 'and'
  OR = 'or'


@dataclass
class OhmFilter:
  column: str
  operator: OhmFilterOperator
  value: Union[str, int, float, bool, None, List[Union[str, int, float, bool]]]


@dataclass
class OhmFilterGroup:
  type: OhmFilterGroupType
  filters: List[Union['OhmFilter', 'OhmFilterGroup']]
