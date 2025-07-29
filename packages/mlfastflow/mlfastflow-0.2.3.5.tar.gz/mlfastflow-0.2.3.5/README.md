# MLFastFlow

A Python package for fast dataflow and workflow processing.

## Installation

```bash
pip install mlfastflow
```

## Features

- Easy-to-use data sourcing with the Sourcing class
- Flexible vector search capabilities
- Optimized for data processing workflows
- Powerful BigQuery integration with support for:
  - Table operations (create, truncate, delete)
  - Asynchronous query execution for long-running jobs
  - Efficient data transfer between BigQuery and GCS
  - Advanced GCS folder management capabilities

## Quick Start

```python
from mlfastflow import Sourcing

# Create a sourcing instance
sourcing = Sourcing(
    query_df=your_query_dataframe,
    db_df=your_database_dataframe,
    columns_for_sourcing=["column1", "column2"],
    label="your_label"
)

# Process your data
sourced_db_df_without_label, sourced_db_df_with_label = (
    sourcing.sourcing()
)
```

## BigQuery Integration

MLFastFlow provides a powerful `BigQueryClient` class for seamless integration with Google BigQuery and Google Cloud Storage (GCS).

### Initialization

```python
from mlfastflow import BigQueryClient

# Initialize the client with your GCP credentials
bq_client = BigQueryClient(
    project_id="your-gcp-project-id",
    dataset_id="your_dataset",
    key_file="/path/to/your/service-account-key.json"
)
```

### Running SQL Queries

```python
# Execute a SQL query and get results as a pandas DataFrame
df = bq_client.sql2df("SELECT * FROM your_dataset.your_table LIMIT 10")

# Run a query without returning results
bq_client.run_sql("CREATE TABLE your_dataset.new_table AS SELECT * FROM your_dataset.source_table")

# Execute a long-running query asynchronously and get the job_id for status checking
job_id = bq_client.run_sql("CREATE TABLE your_dataset.large_table AS SELECT * FROM your_dataset.huge_table")

# Check the status of an asynchronous query job
job_status = bq_client.check_job_status(job_id)
```

### Table Operations

```python
# Truncate a table (remove all rows while preserving schema)
bq_client.truncate_table("your_table_name")
```

### DataFrame to BigQuery

```python
import pandas as pd

# Create a sample DataFrame
df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'value': [100, 200, 300]
})

# Upload DataFrame to BigQuery
bq_client.df2table(
    df=df,
    table_id="your_table_name",
    if_exists="fail"  # Options: 'fail',  'append'
)
```

### BigQuery to Google Cloud Storage

```python
# Export query results to GCS as Parquet files (default)
bq_client.sql2gcs(
    sql="SELECT * FROM your_dataset.your_table",
    destination_uri="gs://your-bucket/path/to/export/",
    destination_format="PARQUET"  # Options: 'PARQUET', 'CSV', 'JSON', 'AVRO'
)

# Export large query results with control over file sizes using SQL EXPORT DATA
bq_client.sql2gcs_via_query(
    sql="SELECT * FROM your_dataset.large_table",
    destination_uri="gs://your-bucket/path/to/export/data-*.parquet",
    destination_format="PARQUET",
    max_file_size="5GB"  # Control output file size
)

# Save SQL query text to GCS for documentation/audit purposes
bq_client.save_sql_to_gcs(
    sql_content="SELECT * FROM your_dataset.your_table WHERE date = '2025-05-08'",
    bucket_name="your-bucket",
    blob_name="queries/daily_extract.sql",
    metadata={"purpose": "daily_extraction", "author": "data_team"}
)
```

### Google Cloud Storage to BigQuery

```python
# Load data from GCS to BigQuery
bq_client.gcs2table(
    gcs_uri="gs://your-bucket/path/to/data/*.parquet",
    table_id="your_destination_table",
    write_disposition="WRITE_TRUNCATE",  # Options: 'WRITE_TRUNCATE', 'WRITE_APPEND', 'WRITE_EMPTY'
    source_format="PARQUET"  # Options: 'PARQUET', 'CSV', 'JSON', 'AVRO', 'ORC'
)
```

### GCS Folder Management

```python
# Create a proper folder in GCS that appears in the GCS Console
bq_client.create_gcs_folder("gs://your-bucket/new-folder/")

# Delete a folder and all its contents
success, deleted_count = bq_client.delete_gcs_folder(
    gcs_folder_path="gs://your-bucket/folder-to-delete/",
    dry_run=True  # Set to False to actually delete
)
print(f"Would delete {deleted_count} files" if success else "Error occurred")
```

### Resource Management

```python
# Explicitly close the client when done to free resources
bq_client.close()
del bq_client
bq_client = None
```

## Utility Functions

### CSV to Parquet Conversion

Convert CSV files to the more efficient Parquet format using high-performance Polars with LazyFrame processing:

```python
from mlfastflow import csv2parquet

# Convert a single CSV file to Parquet
csv2parquet("path/to/file.csv")

# Convert all CSV files in a directory
csv2parquet("path/to/directory")

# Convert all CSV files in a directory and its subdirectories
csv2parquet("path/to/directory", sub_folders=True)

# Specify a custom output directory
csv2parquet("path/to/source", output_dir="path/to/destination")
```

This function efficiently handles large CSV files and directories with many files, leveraging Polars' LazyFrame for better performance and lower memory usage compared to pandas.

For more detailed examples and advanced usage, refer to the [documentation](https://github.com/Xileven/mlfastflow/docs).

### Timer Decorator

Measure and print the execution time of any function using the `timer_decorator`:

```python
from mlfastflow import timer_decorator

@timer_decorator
def my_function():
    # ... your code ...
    pass

my_function()
```

This decorator prints the elapsed time after the function completes, making it easy to profile code blocks.

## License

MIT

## Author

Xileven
