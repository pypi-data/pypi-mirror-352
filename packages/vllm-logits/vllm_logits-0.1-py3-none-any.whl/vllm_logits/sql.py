import functools
import logging
import pprint
import re
from typing import *

import pglast
from sqlfluff.core import Linter, SQLBaseError, SQLLexError, SQLParseError
from sqlfluff.core.parser.segments.base import UnparsableSegment

from hkkang_utils.string import multi_space_to_single_space


def double_quotes_to_single_quotes(sql_str):
    return sql_str.replace('"', "'")


def add_subquery_alias(sql_str):
    tokens_before_parenthesis = []
    last_token = ""
    current_token = ""
    alias_cnt = 1
    parenthesis_depth = 0
    sql_str = multi_space_to_single_space(sql_str)
    new_sql_str = ""
    for character in sql_str:
        new_sql_str += character
        # State change
        if character in [" ", "\n", "\t"]:
            last_token = current_token
            current_token = ""
        else:
            current_token += character
        # Set parenthesis depth
        if character == "(":
            parenthesis_depth += 1
            tokens_before_parenthesis.append(last_token)
        elif character == ")":
            parenthesis_depth -= 1
            popped_token = tokens_before_parenthesis.pop(-1)
            if popped_token.lower() == "from":
                # Add alias
                new_alias = f"S{alias_cnt}"
                alias_cnt += 1
                new_sql_str += f" AS {new_alias}"
    return new_sql_str


def replace_table_or_column_names_with_postgresql_keywords(sql_str):
    keywords = ["CAST", "cast"]
    for keyword in keywords:
        sql_str = sql_str.replace(f" FROM {keyword} ", f" FROM {keyword}1 ").replace(
            f" JOIN {keyword} ", f" JOIN {keyword}1 "
        )
    return sql_str


def loosely_parse(sql_str):
    """_summary_: Parse a SQL string and return a parse tree. If the parsing fails, return None.

    Args:
        sql_str (str): SQL string to parse

    Returns:
        pglast.ast.Node: pglast Node object
    """

    def is_nested_query_in_from_clause_without_alias(e_args):
        return e_args[0] == "subquery in FROM must have an alias"

    def has_join_keyword_without_join_condition(sql, e_args):
        sql = sql.lower()
        if "syntax error at" in e_args[0].lower():
            # Cut off the WHERE clause
            where_start_idx = e_args[1]
            sql_substring = sql[:where_start_idx]
            # Cut off before FROM clause
            from_start_idx = sql_substring.index("from")
            sql_substring = sql_substring[from_start_idx:]
            if " join " in sql_substring and " on " not in sql_substring:
                return True
        return False

    def add_natural_keyword(sql, where_start_idx):
        sql_front = sql[:where_start_idx]
        sql_rear = sql[where_start_idx:]
        return (
            sql_front.replace(" join ", " natural join ").replace(
                " JOIN ", " NATURAL JOIN "
            )
            + sql_rear
        )

    sql_str_ = double_quotes_to_single_quotes(sql_str)
    sql_str_ = replace_table_or_column_names_with_postgresql_keywords(sql_str_)
    try:
        parse_tree = pglast.parse_sql(sql_str_)
    except pglast.parser.ParseError as e:
        if is_nested_query_in_from_clause_without_alias(e.args):
            sql_str_ = add_subquery_alias(sql_str_)
            return loosely_parse(sql_str_)
        elif has_join_keyword_without_join_condition(sql_str_, e.args):
            sql_str_ = add_natural_keyword(sql_str_, where_start_idx=e.args[1])
            return loosely_parse(sql_str_)
        else:
            raise e
    return parse_tree[0]


# Recursively set att_name of object to att_value
def set_att_value(object, att_name, att_value):
    def is_pglast_object(obj):
        return str(type(obj)).startswith("<class 'pglast.")

    if hasattr(object, att_name):
        setattr(object, att_name, att_value)
    for att_str in filter(
        lambda att_str: not att_str.startswith("__")
        and (
            type(getattr(object, att_str)) in [list, tuple]
            or is_pglast_object(getattr(object, att_str))
        ),
        dir(object),
    ):
        selected_object = getattr(object, att_str)
        if type(selected_object) in [list, tuple]:
            for item in selected_object:
                set_att_value(item, att_name, att_value)
        else:
            set_att_value(selected_object, att_name, att_value)
    return object


def pprint_parse_tree(parse_tree):
    """_summary_: Print a parse tree in a readable json format.

    Args:
        parse_tree (pglast.ast.Node): pglast Node object
    """

    def handle_null(input_str):
        return input_str.replace("None", "null")

    def handle_boolean(input_str):
        return input_str.replace(" True", " true").replace(" False", " false")

    def handle_tuple(input_str):
        return input_str.replace("(", "[").replace(",)", "]").replace(")", "]")

    def handle_qutoes(input_str):
        return input_str.replace("'", '"')

    string_to_print = pprint.pformat(parse_tree)
    processed_string = functools.reduce(
        lambda x, func: func(x),
        [handle_null, handle_boolean, handle_tuple, handle_qutoes],
        string_to_print,
    )
    print(processed_string)


### Prettify SQL

# Regex for CREATE TABLE statements
CREATE_TABLE_RE = re.compile(r"(?is)^(CREATE TABLE\s+\S+\s*)\((.*)\)(;?)$")
# Regex for UPSERT (PostgreSQL) statements
UPSERT_RE = re.compile(
    r"(?is)^(INSERT\s+INTO\s+\S+\s*)\((.*?)\)\s*VALUES\s*\((.*?)\)\s*(ON\s+CONFLICT.*?)(;?)$",
    re.DOTALL,
)


def _split_top_level(text: str) -> List[str]:
    """Split a comma-separated list at top-level parentheses, ignoring commas inside quotes."""
    items: List[str] = []
    buffer: List[str] = []
    depth = 0
    in_sq = False
    in_dq = False
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "'" and not in_dq:
            in_sq = not in_sq
            buffer.append(ch)
        elif ch == '"' and not in_sq:
            in_dq = not in_dq
            buffer.append(ch)
        elif not in_sq and not in_dq:
            if ch == "(":
                depth += 1
                buffer.append(ch)
            elif ch == ")":
                depth -= 1
                buffer.append(ch)
            elif ch == "," and depth == 0:
                items.append("".join(buffer).strip())
                buffer = []
            else:
                buffer.append(ch)
        else:
            buffer.append(ch)
        i += 1
    if buffer:
        items.append("".join(buffer).strip())
    return items


def _format_block(header: str, body: str, closing: str = ")") -> str:
    """Format a SQL block with parentheses and comma-separated elements."""
    body = re.sub(r"\s+", " ", body).strip()
    fields = _split_top_level(body)
    last = len(fields) - 1
    lines = [f"    {field}{',' if i < last else ''}" for i, field in enumerate(fields)]
    return f"{header}(\n" + "\n".join(lines) + f"\n){closing}"


def _format_assignments(conflict_clause: str) -> str:
    """
    Split ON CONFLICT ... DO UPDATE SET assignments and format them.
    Returns a formatted string including the assignments.
    """
    m = re.match(
        r"(?is)^(ON\s+CONFLICT\s*\(.*?\)\s*DO\s+UPDATE\s+SET)\s*(.*)$", conflict_clause
    )
    if not m:
        return conflict_clause
    header, assigns = m.groups()
    assigns = assigns.rstrip()
    parts = _split_top_level(assigns)
    last = len(parts) - 1
    lines = [f"    {part}{',' if i < last else ''}" for i, part in enumerate(parts)]
    return f"{header}\n" + "\n".join(lines)


def prettify_sql(sql: str) -> str:
    """Prettify CREATE TABLE and UPSERT (INSERT ... ON CONFLICT) SQL statements."""
    sql = sql.strip()
    # Normalize whitespace for matching
    compact = re.sub(r"\s+", " ", sql)
    # CREATE TABLE
    m = CREATE_TABLE_RE.match(compact)
    if m:
        header, body, closing = m.groups()
        return _format_block(header, body, closing)
    # UPSERT
    m = UPSERT_RE.match(sql)
    if m:
        insert_header, cols, vals, conflict_clause, closing = m.groups()
        cols_block = _format_block(insert_header, cols, closing="")
        vals_block = _format_block("VALUES", vals, closing="")
        conflict_block = _format_assignments(
            re.sub(r"\s+", " ", conflict_clause).strip()
        )
        return "\n".join([cols_block, vals_block, conflict_block + closing])
    # Fallback: return unchanged
    return sql


### Validate SQL string
def is_valid_sql(sql_string: str, dialect: str = "postgres") -> bool:
    """
    Return True if sqlfluff can parse the given SQL string without any
    'unparsable' segments (i.e., it’s syntactically valid for the chosen dialect).
    Return False if parsing fails or if any UnparsableSegment is present.
    """
    sqlfluff_logger = logging.getLogger("sqlfluff")
    prev_level = sqlfluff_logger.level
    sqlfluff_logger.setLevel(logging.WARNING)

    linter = Linter(dialect=dialect)
    try:
        parsed = linter.parse_string(sql_string)
    except (SQLParseError, SQLLexError, SQLBaseError) as e:
        logging.warning(f"sqlfluff raised a parsing error: {e}")
        return False
    finally:
        sqlfluff_logger.setLevel(prev_level)

    # If parse_string succeeds but yields no parse tree at all, it’s invalid
    if not getattr(parsed, "tree", None):
        return False

    # Walk the entire tree and reject if any UnparsableSegment appears
    for segment in parsed.tree.iter_segments():
        if isinstance(segment, UnparsableSegment):
            logging.warning(f"Found unparsable segment in SQL: {sql_string!r}")
            return False

    return True
