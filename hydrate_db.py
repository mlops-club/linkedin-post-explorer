import json
import sqlite3
import time
from pathlib import Path
from shutil import rmtree
from typing import Dict
from uuid import uuid4

from relationalize import (
    Relationalize,
    Schema,
)
from relationalize.utils import create_local_file

THIS_DIR = Path(__file__).parent

### CONSTANTS ###
OBJECT_NAME = "posts"

# Paths using pathlib
BASE_PATH = Path("output")
BASE_PATH.mkdir(parents=True, exist_ok=True)
EXPORT_PATH = THIS_DIR / "./linkedin-post-explorer-infra/assets/posts.json"  # Your local JSON file
LOCAL_TEMP_LOCATION = BASE_PATH / "temp"
LOCAL_FINAL_LOCATION = BASE_PATH / "final"
DB_PATH = BASE_PATH / f"{OBJECT_NAME}.db"

rmtree(BASE_PATH)

# Create directories
BASE_PATH.mkdir(parents=True, exist_ok=True)
LOCAL_TEMP_LOCATION.mkdir(parents=True, exist_ok=True)
LOCAL_FINAL_LOCATION.mkdir(parents=True, exist_ok=True)

schemas: Dict[str, Schema] = {}

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


def on_object_write(schema: str, object: dict):
    if schema not in schemas:
        schemas[schema] = Schema()
    schemas[schema].read_object(object)


def create_iterator(fpath: Path):
    """Yield JSON objects from a file"""
    try:
        posts = json.load(fpath.open())
        for post in posts:
            yield post
    except json.JSONDecodeError:
        for line in fpath.open():
            yield json.loads(line)


print("-" * 20)
print(f"Relationalizing {OBJECT_NAME} from local file: {EXPORT_PATH}")
with Relationalize(
    name=OBJECT_NAME,
    create_output=create_local_file(LOCAL_TEMP_LOCATION),
    on_object_write=on_object_write,
) as r:
    r.relationalize(create_iterator(fpath=EXPORT_PATH))


for schema_name, schema in schemas.items():
    print(f"Processing schema {schema_name}.")

    # Create table schema for SQLite

    short_schema_name = schema_name.replace("posts_", "")

    create_table_statement = schema.generate_ddl(table=short_schema_name, schema="brub").replace('"brub".', "")
    create_table_statement = create_table_statement.replace(f"{short_schema_name}_", "")
    print(create_table_statement)

    cursor.execute(f"DROP TABLE IF EXISTS {schema_name};")
    cursor.execute(create_table_statement)

    import pandas as pd

    json_fpath = LOCAL_TEMP_LOCATION / f"{schema_name}.json"
    df = pd.DataFrame(create_iterator(fpath=json_fpath))
    df.columns = df.columns.str.replace(f"{short_schema_name}_", "")

    df.to_sql(short_schema_name, conn, if_exists="append", index=False)


conn.commit()  # Commit all the inserts
conn.close()
