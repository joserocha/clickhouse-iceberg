-- +goose Up
CREATE DATABASE IF NOT EXISTS iceberg_catalog
ENGINE = DataLakeCatalog('http://iceberg:8181', 'root', 'securepassword')
SETTINGS 
    catalog_type = 'rest', 
    warehouse = 'warehouse', 
    storage_endpoint = 'http://minio:9000/warehouse';
