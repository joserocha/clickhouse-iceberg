## ClickHouse - Apache Iceberg engine implemented by ClickHouse Inc.

### Installation
---

1. Clone the repository:
```
git clone https://github.com/joserocha/clickhouse-iceberg.git
cd clickhouse-iceberg/clickhouse-inc
```

2. Start all containers:
```
docker compose up -d
```

3. Check service status:
```
docker ps
```

### Integration

ClickHouse is improving its integration with Apache Iceberg, providing native interactions with the Iceberg engine. In version 25.7, it became possible to run INSERT INTO directly on the table, and in version 25.8, it became possible to create tables using CREATE TABLE. Despite these improvements, they are still not fully functional, which makes their use not recommended for production. For this reason, we will use PyIceberg. There are implementations for other languages as well, but the number is still limited.

---

1. Create database using DataLakeCatalog engine. It supports Iceberg Rest Catalog
```
CREATE DATABASE IF NOT EXISTS iceberg_catalog
ENGINE = DataLakeCatalog('http://iceberg:8181', 'root', 'securepassword')
SETTINGS 
    catalog_type = 'rest',  
    warehouse = 'data', 
    storage_endpoint = 'http://minio:9000/data';

# http://iceberg:8181   → Iceberg REST catalog endpoint.
# root / securepassword → authentication credentials.
# catalog_type          → use REST API for catalog communication.
# warehouse             → base warehouse path for tables/metadata.
# storage_endpoint      → object storage endpoint (s3 bucket).
```

1. Load catalog, create namespace and create table
```
# connect to the python container and setup the catalog, namespace and table
docker exec -it "$(sudo docker ps | grep -i 'python-exec' | awk '{print $1}')" bash

# python console
bash$ python

from pyiceberg.catalog import load_catalog
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.schema import Schema
from pyiceberg.schema import NestedField
from pyiceberg.types import (TimestampType, StringType, DoubleType, IntegerType)



props = {
    "uri": "http://iceberg:8181",
    "warehouse": "data",
    "s3.endpoint": "http://minio:9000",
    "s3.path-style-access": "true",
    "s3.access-key-id": "root",
    "s3.secret-access-key": "securepassword"
}

# Load catalog. Name is optional
catalog = load_catalog(Name=None, **props)

# Create a namespace
catalog.create_namespace("<name>")

# definition of the table schema
schema = Schema(
    NestedField(1, "event_time", TimestampType(), required=True),
    NestedField(2, "battery_serial", StringType(), required=True)
)

# Create a partition spec
partition_spec = PartitionSpec()

# Add table properties for optimization
table_properties = {
    "write.format.default": "parquet",
    "write.parquet.compression-codec": "snappy",
    "format-version": "2"
}

# It creates the table
table = catalog.create_table(
    identifier="dotzapp.myfirsttable",
    schema=schema,
    partition_spec=partition_spec,
    properties=table_properties
)
```

