from typing import final
from .config import GRAPHQL_URL, GET_OHM_CONFIG
from .filter import OhmFilterGroup, OhmFilterGroupType, OhmFilter

from gql import Client as GQLClient
from gql import gql
from gql.transport.requests import RequestsHTTPTransport
import psycopg2
import pandas as pd
from typing import List, Optional
import json
import re


@final
class OhmClient:
  def __init__(self, api_key: str):
    self.api_key = api_key
    self.__gql_transport = RequestsHTTPTransport(
      url=GRAPHQL_URL,
      headers={'workspace_api_key': api_key},
      verify=True,
      retries=3,
    )
    self.__gql_client = GQLClient(transport=self.__gql_transport)
    self.__ohm_config = self.__fetch_config()

    try:
      self.__db_connection = psycopg2.connect(
        host=self.__ohm_config['db']['host'],
        port=self.__ohm_config['db']['port'],
        user=self.__ohm_config['db']['user'],
        password=self.__ohm_config['db']['password'],
        dbname=self.__ohm_config['db']['database'],
      )
    except psycopg2.Error as e:
      raise ConnectionError(f'Failed to connect to database: {e}')

  def __fetch_config(self) -> None:
    """Fetch the Ohm config from the database."""

    json_response = self.__gql_client.execute(gql(GET_OHM_CONFIG))
    if 'get_ohm_config' not in json_response:
      raise ValueError('Unable to fetch Ohm config')

    config = json_response['get_ohm_config']

    # Define expected structure
    expected_types = {
      'db': {
        'type': dict,
        'fields': {
          'host': str,
          'port': int,
          'user': str,
          'password': str,
          'sslmode': str,
          'database': str,
        },
      },
      'tables': {
        'type': dict,
        'fields': {'metadata': str, 'observation': str, 'dataset_cycle': str},
      },
    }

    # Validate config
    self.__validate_config(config, expected_types)
    return config

  def __validate_config(self, config: dict, expected_types: dict) -> None:
    """Validate config against expected structure and types."""
    for section, section_spec in expected_types.items():
      if section not in config:
        raise ValueError(f"Missing required section '{section}' in Ohm config")

      if not isinstance(config[section], section_spec['type']):
        raise ValueError(
          f"Config section '{section}' must be a {section_spec['type'].__name__}"
        )

      for field, field_type in section_spec.get('fields', {}).items():
        if field not in config[section]:
          raise ValueError(f"Missing required field '{field}' in '{section}' section")

        if not isinstance(config[section][field], field_type):
          raise ValueError(f"Field '{section}.{field}' must be a {field_type.__name__}")

  def __convert_value(
    self, value: str | int | float | bool
  ) -> str | int | float | bool:
    """Convert a string value to a more specific type (boolean, number, or string)."""
    if not isinstance(value, str):
      return value

    trimmed = value.strip()
    if trimmed.lower() == 'true':
      return True
    if trimmed.lower() == 'false':
      return False
    if re.match(r'^-?\d+$', trimmed):
      return int(trimmed)
    if re.match(r'^-?\d+\.\d+$', trimmed):
      return float(trimmed)
    return f"'{trimmed}'"

  def __build_columns_sql(self, columns: List[str]) -> str:
    """Build a SQL column string from a list of column names."""

    if not columns:
      return '*'

    return ', '.join([f'"{col}"' for col in columns])

  def __build_where_clause(self, filters: OhmFilterGroup | List[OhmFilter]) -> str:
    """Build a WHERE clause from a OhmFilterGroup.

    Args:
        filters: Either a OhmFilterGroup object or a List of OhmFilter objects. If a list is provided,
                it will be treated as a OhmFilterGroup with AND logic.

    Returns:
        A SQL WHERE clause string
    """
    # Convert list of filters to FilterGroup if needed
    if isinstance(filters, list):
      filters = OhmFilterGroup(type=OhmFilterGroupType.AND, filters=filters)

    # Handle empty case
    if not filters or not filters.filters:
      return ''

    conditions = []

    # Process all items in filters.filters, which can be OhmFilter or OhmFilterGroup objects
    for item in filters.filters:
      if isinstance(item, OhmFilter):
        # Handle OhmFilter objects
        col = f'"{item.column}"'
        val = self.__convert_value(item.value)

        if item.operator == 'equals':
          conditions.append(f'{col} = {val}')
        elif item.operator == 'contains':
          conditions.append(f"{col} ILIKE '%{item.value}%'")
        elif item.operator == 'startsWith':
          conditions.append(f"{col} ILIKE '{item.value}%'")
        elif item.operator == 'endsWith':
          conditions.append(f"{col} ILIKE '%{item.value}'")
        elif item.operator == 'notContains':
          conditions.append(f"{col} NOT ILIKE '%{item.value}%'")
        elif item.operator == 'lt':
          conditions.append(f'{col} < {val}')
        elif item.operator == 'lte':
          conditions.append(f'{col} <= {val}')
        elif item.operator == 'gt':
          conditions.append(f'{col} > {val}')
        elif item.operator == 'gte':
          conditions.append(f'{col} >= {val}')
        elif item.operator == 'not':
          conditions.append(f'{col} <> {val}')
        elif item.operator == 'in':
          try:
            in_values = json.loads(item.value)
            if not isinstance(in_values, list):
              raise ValueError
          except Exception:
            in_values = [v.strip() for v in item.value.split(',')]
            in_values = [self.__convert_value(v) for v in in_values]
          conditions.append(f'{col} IN ({",".join(in_values)})')
        elif item.operator == 'notIn':
          try:
            not_in_values = json.loads(item.value)
            if not isinstance(not_in_values, list):
              raise ValueError
          except Exception:
            not_in_values = [v.strip() for v in item.value.split(',')]
            not_in_values = [self.__convert_value(v) for v in not_in_values]
          conditions.append(f'{col} NOT IN ({",".join(not_in_values)})')
        elif item.operator == 'isNull':
          conditions.append(f'{col} IS NULL')
        elif item.operator == 'isNotNull':
          conditions.append(f'{col} IS NOT NULL')
        else:
          raise ValueError(f'Unsupported operator: {item.operator}')
      elif isinstance(item, OhmFilterGroup):
        # Recursively process nested OhmFilterGroup
        nested = self.__build_where_clause(item)
        if nested:
          conditions.append(f'({nested})')

    # Join conditions with AND/OR
    if conditions:
      # Normalize the filter type to string for comparison
      # Handle both enum and string inputs
      if hasattr(filters.type, 'value'):
        filter_type_str = filters.type.value
      else:
        filter_type_str = filters.type

      join_str = ' AND ' if filter_type_str == OhmFilterGroupType.AND.value else ' OR '
      return f'{join_str.join(conditions)}'

    return ''

  def __get_data(
    self,
    table_name: str,
    columns: Optional[List[str]] = None,
    filters: Optional[OhmFilterGroup | List[OhmFilter]] = None,
  ) -> pd.DataFrame:
    """Fetch data from the database."""
    columns_sql = self.__build_columns_sql(columns)
    where_clause_sql = self.__build_where_clause(filters)

    final_sql = f'SELECT {columns_sql} FROM "{table_name}" WHERE {where_clause_sql}'

    with self.__db_connection.cursor() as cursor:
      cursor.execute(final_sql)

      # Get column names from cursor.description
      column_names = [desc[0] for desc in cursor.description]
      data = cursor.fetchall()

    # Create DataFrame with explicit column names
    return pd.DataFrame(data, columns=column_names)

  def get_observation_data(
    self,
    columns: Optional[List[str]] = None,
    filters: Optional[OhmFilterGroup | List[OhmFilter]] = None,
  ) -> pd.DataFrame:
    """
    Fetch observation data from the database.
    """

    if columns is None:
      columns = []

    if filters is None:
      filters = []

    table_name = self.__ohm_config['tables']['observation']
    return self.__get_data(table_name, columns, filters)

  def get_dataset_cycle_data(
    self,
    columns: Optional[List[str]] = None,
    filters: Optional[OhmFilterGroup | List[OhmFilter]] = None,
  ) -> pd.DataFrame:
    """
    Fetch dataset cycle data from the database.
    """
    if columns is None:
      columns = []

    if filters is None:
      filters = []

    table_name = self.__ohm_config['tables']['dataset_cycle']
    return self.__get_data(table_name, columns, filters)

  def get_metadata(
    self,
    columns: Optional[List[str]] = None,
    filters: Optional[OhmFilterGroup | List[OhmFilter]] = None,
  ) -> pd.DataFrame:
    """
    Fetch metadata from the database.
    """
    if columns is None:
      columns = []

    if filters is None:
      filters = []

    table_name = self.__ohm_config['tables']['metadata']
    return self.__get_data(table_name, columns, filters)
