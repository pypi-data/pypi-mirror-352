import re

from urllib.parse import quote
from typing import Dict, Optional, Any, List, TypeVar, Tuple

import sqlalchemy
from pydantic import AnyUrl, UrlConstraints
from sqlalchemy import BinaryExpression, Column, String, create_engine, make_url
from sqlmodel import AutoString
from tidb_vector.sqlalchemy import VectorType
from sqlalchemy.engine import Row
from sqlalchemy import Table
from typing import Union

from pytidb.schema import TableModel
from pytidb.constants import (
    AND,
    OR,
    EQ,
    IN,
    NIN,
    GT,
    GTE,
    LT,
    LTE,
    NE,
)

JSON_FIELD_PATTERN = re.compile(
    r"^(?P<column>[a-zA-Z_][a-zA-Z0-9_]*)\.(?P<json_field>[a-zA-Z_][a-zA-Z0-9_]*)$"
)


TIDB_SERVERLESS_HOST_PATTERN = re.compile(
    r"gateway\d{2}\.(.+)\.(prod|dev|staging)\.(shared\.)?(aws|alicloud)\.tidbcloud\.com"
)


def create_engine_without_db(url, echo=False, **kwargs):
    temp_db_url = make_url(url)
    temp_db_url = temp_db_url._replace(database=None)
    return create_engine(temp_db_url, echo=echo, **kwargs)


class TiDBDsn(AnyUrl):
    """A type that will accept any TiDB DSN.

    * User info required
    * TLD not required
    * Host not required
    """

    _constraints = UrlConstraints(
        allowed_schemes=[
            "mysql",
            "mysql+mysqlconnector",
            "mysql+aiomysql",
            "mysql+asyncmy",
            "mysql+mysqldb",
            "mysql+pymysql",
            "mysql+cymysql",
            "mysql+pyodbc",
        ],
        default_port=4000,
        host_required=True,
    )


def build_tidb_dsn(
    schema: str = "mysql+pymysql",
    host: str = "localhost",
    port: int = 4000,
    username: str = "root",
    password: str = "",
    database: str = "test",
    enable_ssl: Optional[bool] = None,
) -> TiDBDsn:
    if enable_ssl is None:
        if host and TIDB_SERVERLESS_HOST_PATTERN.match(host):
            enable_ssl = True
        else:
            enable_ssl = None

    return TiDBDsn.build(
        scheme=schema,
        host=host,
        port=port,
        username=username,
        # TODO: remove quote after following issue is fixed:
        # https://github.com/pydantic/pydantic/issues/8061
        password=quote(password) if password else None,
        path=database,
        query="ssl_verify_cert=true&ssl_verify_identity=true" if enable_ssl else None,
    )


def filter_vector_columns(columns: Dict) -> List[Column]:
    vector_columns = []
    for column in columns:
        if isinstance(column.type, VectorType):
            vector_columns.append(column)
    return vector_columns


def check_vector_column(columns: Dict, column_name: str) -> Optional[str]:
    if column_name not in columns:
        raise ValueError(f"Non-exists vector column: {column_name}")

    vector_column = columns[column_name]
    if vector_column.type != VectorType:
        raise ValueError(f"Invalid vector column: {vector_column}")

    return vector_column


def filter_text_columns(columns: Dict) -> List[Column]:
    text_columns = []
    for column in columns:
        if isinstance(column.type, AutoString) or isinstance(column.type, String):
            text_columns.append(column)
    return text_columns


def check_text_column(columns: Dict, column_name: str) -> Optional[str]:
    if column_name not in columns:
        raise ValueError(f"Non-exists text column: {column_name}")

    text_column = columns[column_name]
    if not isinstance(text_column.type, String) and not isinstance(
        text_column.type, AutoString
    ):
        raise ValueError(f"Invalid text column: {text_column}")

    return text_column


def build_filter_clauses(
    filters: Dict[str, Any], columns: Dict, table_model: TableModel
) -> List[BinaryExpression]:
    if filters is None:
        return []

    filter_clauses = []
    for key, value in filters.items():
        if key.lower() == AND:
            if not isinstance(value, list):
                raise TypeError(
                    f"Expect a list value for $and operator, but got {type(value)}"
                )
            and_clauses = []
            for item in value:
                and_clauses.extend(build_filter_clauses(item, columns, table_model))
            if len(and_clauses) == 0:
                continue
            filter_clauses.append(sqlalchemy.and_(*and_clauses))
        elif key.lower() == OR:
            if not isinstance(value, list):
                raise TypeError(
                    f"Expect a list value for $or operator, but got {type(value)}"
                )
            or_clauses = []
            for item in value:
                or_clauses.extend(build_filter_clauses(item, columns, table_model))
            if len(or_clauses) == 0:
                continue
            filter_clauses.append(sqlalchemy.or_(*or_clauses))
        elif key in columns:
            column = getattr(columns, key)
            if isinstance(value, dict):
                filter_clause = build_column_filter(column, value)
            else:
                # implicit $eq operator: value maybe int / float / string
                filter_clause = build_column_filter(column, {EQ: value})
            if filter_clause is not None:
                filter_clauses.append(filter_clause)
        elif "." in key:
            match = JSON_FIELD_PATTERN.match(key)
            if not match:
                raise ValueError(
                    f"Got unexpected filter key: {key}, please use valid column name instead"
                )
            column_name = match.group("column")
            json_field = match.group("json_field")
            column = sqlalchemy.func.json_extract(
                getattr(table_model, column_name), f"$.{json_field}"
            )
            if isinstance(value, dict):
                filter_clause = build_column_filter(column, value)
            else:
                # implicit $eq operator: value maybe int / float / string
                filter_clause = build_column_filter(column, {EQ: value})
            if filter_clause is not None:
                filter_clauses.append(filter_clause)
        else:
            raise ValueError(
                f"Got unexpected filter key: {key}, please use valid column name instead"
            )

    return filter_clauses


def build_column_filter(
    column: Any, conditions: Dict[str, Any]
) -> Optional[BinaryExpression]:
    column_filters = []
    for operator, val in conditions.items():
        op = operator.lower()
        if op == IN:
            column_filters.append(column.in_(val))
        elif op == NIN:
            column_filters.append(~column.in_(val))
        elif op == GT:
            column_filters.append(column > val)
        elif op == GTE:
            column_filters.append(column >= val)
        elif op == LT:
            column_filters.append(column < val)
        elif op == LTE:
            column_filters.append(column <= val)
        elif op == NE:
            column_filters.append(column != val)
        elif op == EQ:
            column_filters.append(column == val)
        else:
            raise ValueError(
                f"Unknown filter operator {operator}. Consider using "
                "one of $in, $nin, $gt, $gte, $lt, $lte, $eq, $ne."
            )
    if len(column_filters) == 0:
        return None
    elif len(column_filters) == 1:
        return column_filters[0]
    else:
        return sqlalchemy.and_(*column_filters)


RowKeyType = TypeVar("RowKeyType", bound=Union[Any, Tuple[Any, ...]])


def get_row_id_from_row(row: Row, table: Table) -> Optional[RowKeyType]:
    pk_constraint = table.primary_key
    if not pk_constraint.columns:
        # Try to get _tidb_rowid if no primary key exists
        try:
            return row._mapping["_tidb_rowid"]
        except KeyError:
            return row.__hash__()

    pk_column_names = [col.name for col in pk_constraint.columns]
    try:
        if len(pk_column_names) == 1:
            return row._mapping[pk_column_names[0]]
        return tuple(row._mapping[name] for name in pk_column_names)
    except KeyError as e:
        raise KeyError(
            f"Primary key column '{e.args[0]}' not found in Row. "
            f"Available: {list(row._mapping.keys())}"
        )
