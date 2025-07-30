from enum import Enum
from dataclasses import dataclass
from typing import Union, List


class FilterOperator(Enum):
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


class FilterGroupType(Enum):
  AND = 'and'
  OR = 'or'


@dataclass
class Filter:
  column: str
  operator: FilterOperator
  value: Union[str, int, float, bool, None, List[Union[str, int, float, bool]]]


@dataclass
class FilterGroup:
  type: FilterGroupType
  filters: List[Union['Filter', 'FilterGroup']]
