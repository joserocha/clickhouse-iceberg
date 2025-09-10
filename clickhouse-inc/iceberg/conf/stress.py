import time
import random
from datetime import datetime
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, LongType, DoubleType, TimestampType, StringType
import pyarrow as pa


def generate_row():
    return {
        "event_time": datetime.utcnow(),
        "sensor_id": f"sensor_{random.randint(1, 1000)}",
        "value": random.random() * 100,
    }


# Variables
iceberg_endpoint = "http://iceberg:8181"
bucket_endpoint = "http://minio:9000"
base_warehouse = "data"
key_id = "root"
access_key = "securepassword"
n_table = "dotzapp.stress_test"

# Properties of catalog
props = {
    "uri": iceberg_endpoint,
    "warehouse": base_warehouse,
    "s3.endpoint": bucket_endpoint,
    "s3.path-style-access": "true",
    "s3.access-key-id": key_id,
    "s3.secret-access-key": access_key
}

# Connect to the iceberg rest catalog
catalog = load_catalog(Name=None, **props)

# Create table
schema = Schema(
    NestedField(1, "event_time", TimestampType(), required=True),
    NestedField(2, "sensor_id", StringType(), required=True),
    NestedField(3, "value", DoubleType(), required=True),
)

catalog.create_table(n_table, schema)

# Load table
table = catalog.load_table(n_table)

# ---- Row by row
lines_test_per_row = 10000
print(f"\n[Row by row] Inserting {lines_test_per_row} rows...")
start = time.time()

pa_table = []
for _ in range(lines_test_per_row):
    row = generate_row()
    pa_table = pa.Table.from_pylist([row], schema=table.schema().as_arrow())
    table.append(df=pa_table)

end = time.time()
print(f"Tempo total: {end - start:.2f}s  |  {lines_test_per_row/(end-start):.2f} rows/s")


# ---- batch
batch = 1000
lines_test_per_batch = 10000
print(f"\n[Batch] Inserting {lines_test_per_batch} rows in batches of {batch}...")
start = time.time()

rows = []
pa_table = []
for i in range(lines_test_per_batch):
    rows.append(generate_row())  # acumula dicionários
    if len(rows) >= batch:
        rows.append(generate_row())
        if len(rows) >= batch:
            pa_table = pa.Table.from_pylist(rows, schema=table.schema().as_arrow())
            table.append(df=pa_table)
            rows = []

# Se sobrar linhas
if rows:
    table.append(rows)

end = time.time()
print(f"Tempo total: {end - start:.2f}s  |  {lines_test_per_batch/(end-start):.2f} rows/s")

