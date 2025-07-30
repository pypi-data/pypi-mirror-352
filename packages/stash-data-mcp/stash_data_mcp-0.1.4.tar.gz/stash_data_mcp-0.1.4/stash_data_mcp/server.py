import os
import inspect
from typing import List, Dict, Optional
import dotenv

from fastastra.fastastra import AstraDatabase
from mcp.server.fastmcp import FastMCP

# Load environment variables
dotenv.load_dotenv("./.env")
dotenv.load_dotenv("../.env")

# AstraDB credentials
TOKEN = os.environ["ASTRA_DB_APPLICATION_TOKEN"]
DBID  = os.environ["DBID"]

# Initialize Astra client and MCP server
db  = AstraDatabase(TOKEN, DBID)
mcp = FastMCP("stash-data-mcp")


def make_index_search(tbl, table_name: str, col: str):
    def search(value):
        return tbl.xtra(**{col: value})
    search.__doc__ = (
        f"Search `{table_name}` by column `{col}` using its secondary index."
    )
    return search


def make_vector_search(tbl, table_name: str, col: str):
    def vs(embedding: List[float]):
        return tbl.xtra(**{col: embedding})
    vs.__doc__ = (
        f"ANN search on `{table_name}`.`{col}` with a raw embedding vector."
    )
    return vs


def make_text_search(tbl, table_name: str, col: str):
    def ts(query: str):
        return tbl.xtra(**{col: query})
    ts.__doc__ = (
        f"Semantic text search on `{table_name}`.`{col}`, auto-embedding the input string."
    )
    return ts


def make_typed_get_by_pk(tbl, table_name: str, pks: List[str]):
    """
    Dynamically build a get_by_pk(table_name) function with explicit, typed PK args.
    """
    # Pull types from the Pydantic model
    model_fields = tbl._model.model_fields
    # Prepare exec namespace (hide tbl via default)
    local_ns = {"tbl": tbl, "Dict": Dict, "Optional": Optional}

    # Build signature source, e.g. "cat_id: UUID, owner: str"
    params_src = ", ".join(
        f"{pk}: {model_fields[pk].annotation.__name__}" for pk in pks
    )
    # Function definition with a hidden _tbl default
    src = (
        f"def get_{table_name}_by_pk({params_src}, _tbl=tbl) -> Dict:\n"
        + (f"    return _tbl[{pks[0]}]\n"
           if len(pks) == 1
           else f"    return _tbl[({', '.join(pks)},)]\n")
    )

    exec(src, globals(), local_ns)
    fn = local_ns[f"get_{table_name}_by_pk"]

    # Override signature so _tbl is hidden
    sig_params = [
        inspect.Parameter(pk,
                          inspect.Parameter.POSITIONAL_OR_KEYWORD,
                          annotation=model_fields[pk].annotation)
        for pk in pks
    ]
    fn.__signature__ = inspect.Signature(sig_params)
    fn.__doc__ = f"Fetch one row from `{table_name}` by its partition key(s)."
    return fn


def make_typed_crud_tool(tbl, table_name: str, kind: str):
    """
    Dynamically build insert/update/delete with explicit, typed columns.
    """
    model_fields = tbl._model.model_fields
    pks = tbl.partition_keys or []

    # Build (name, type, is_optional) list: PKs first (required), then others (optional)
    parts = []
    for pk in pks:
        ann = model_fields[pk].annotation
        parts.append((pk, ann, False))
    if kind in ("insert", "update"):
        for col, fld in model_fields.items():
            if col in pks:
                continue
            ann = fld.annotation
            parts.append((col, ann, True))

    # Prepare exec namespace
    local_ns = {"tbl": tbl, "Dict": Dict}
    # Build signature source: "id: int, owner: str = None, ..."
    params_src = ", ".join(
        f"{name}: {typ.__name__}" + (" = None" if optional else "")
        for name, typ, optional in parts
    )

    # Function header
    ret = "bool" if kind == "delete" else "Dict"
    src_lines = [f"def {kind}_{table_name}({params_src}, _tbl=tbl) -> {ret}:"]
    # Body
    if kind in ("insert", "update"):
        src_lines.append("    data = {}")
        for name, _, _ in parts:
            src_lines.append(f"    if {name} is not None: data['{name}'] = {name}")
        call = "insert" if kind == "insert" else "update"
        src_lines.append(f"    return _tbl.{call}(**data)")
    else:  # delete
        if len(pks) == 1:
            src_lines.append(f"    return _tbl.delete({pks[0]}={pks[0]})")
        else:
            args = ", ".join(f"{pk}={pk}" for pk in pks)
            src_lines.append(f"    return _tbl.delete({args})")

    src = "\n".join(src_lines)
    exec(src, globals(), local_ns)
    fn = local_ns[f"{kind}_{table_name}"]

    # Override signature to expose only the real columns
    sig_params = []
    for name, typ, optional in parts:
        default = inspect._empty if not optional else None
        sig_params.append(
            inspect.Parameter(
                name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=typ,
                default=default
            )
        )
    fn.__signature__ = inspect.Signature(sig_params)
    fn.__doc__ = {
        "insert": f"Insert a new row into `{table_name}`.",
        "update": f"Update an existing row in `{table_name}`.",
        "delete": f"Delete a row from `{table_name}` by its partition key(s)."
    }[kind]

    return fn


def register_table_tools(mcp: FastMCP, tbl):
    name = tbl.table_name
    pks = tbl.partition_keys or []

    # list_all
    def list_all():
        return list(tbl())
    list_all.__doc__ = f"Retrieve all rows from `{name}`."
    mcp.tool(name=f"{name}_list_all")(list_all)

    def drop():
        return tbl.drop()
    drop.__doc__ = f"drop table `{name}`."
    mcp.tool(name=f"drop_table_{name}")(drop)


    # get_by_pk (typed)
    mcp.tool(name=f"{name}_get_by_pk")(make_typed_get_by_pk(tbl, name, pks))

    # indexed-column searches
    for col in tbl._indexed_columns:
        mcp.tool(name=f"{name}_search_by_{col}")(
            make_index_search(tbl, name, col)
        )

    # vector & text searches
    for col in getattr(tbl, "_vector_indexes", []):
        mcp.tool(name=f"{name}_vector_search_by_{col}")(
            make_vector_search(tbl, name, col)
        )
        mcp.tool(name=f"{name}_text_search_by_{col}")(
            make_text_search(tbl, name, col)
        )

    # typed CRUD
    for op in ("insert", "update", "delete"):
        mcp.tool(name=f"{name}_{op}")(
            make_typed_crud_tool(tbl, name, op)
        )


# Register tools for every table in AstraDB
for table in db.t:
    register_table_tools(mcp, table)


# Global schema-evolution tools
TYPE_MAP = {
    "int": int,
    "integer": int,
    "str": str,
    "string": str,
    "text": str,
    "bool": bool,
    "boolean": bool,
    "float": float,
    "double": float
}

def create_table(
    table_name: str,
    columns: Dict[str, str],
    partition_keys: List[str]
):
    """
    Dynamically create a new table.

    Supported type names (case‐insensitive, or pass Python types directly):
      • int, integer
      • str, string, text
      • bool, boolean
      • float, double

    Parameters:
      table_name (str): Name of the new table.
      columns (Dict[str|type, str|type]): Mapping column→type‐name (string) or Python type.
      partition_keys (List[str]): Columns to use as the partition key; each must appear in `schema`.

    Returns:
      Dict: { "status": "created", "table": table_name }
    """
    # 1) Build real_schema: map strings→types, accept real types
    real_schema = {}
    if columns is None:
        raise ValueError("Schema is required to create a table.")
    for col, typ in columns.items():
        # If the user passed a string, map it
        if isinstance(typ, str):
            key = typ.strip().lower()
            if key not in TYPE_MAP:
                raise ValueError(
                    f"Unsupported type name '{typ}' for column '{col}'. "
                    f"Supported: {', '.join(sorted(TYPE_MAP.keys()))}"
                )
            real_schema[col] = TYPE_MAP[key]
        # If they already passed the type object, use it
        elif isinstance(typ, type):
            real_schema[col] = typ
        else:
            raise ValueError(
                f"Schema for column '{col}' must be either a type or a supported type-name string."
            )

    # 2) Validate partition keys
    missing = [pk for pk in partition_keys if pk not in real_schema]
    if missing:
        raise ValueError(
            f"Error creating table '{table_name}': Partition key(s) {missing} not found in parsed columns: {list(real_schema.keys())} columns: {columns}"
        )

    # 3) Create or fetch the Table and apply schema
    tbl = getattr(db.t, table_name, None) or db.t._new_table(table_name)
    tbl.create(**real_schema, partition_keys=partition_keys)

    return {"status": "created", "table": table_name}
mcp.tool(name="create_table")(create_table)


def create_index(table_name: str, column: str):
    """
    Add an index to an existing table column.
    """
    tbl = getattr(db.t, table_name)
    getattr(tbl.c, column).index()
    return {"status": "indexed", "table": table_name, "column": column}
mcp.tool(name="create_index")(create_index)

def run():
    mcp.run()

if __name__ == "__main__":
    mcp.run()

