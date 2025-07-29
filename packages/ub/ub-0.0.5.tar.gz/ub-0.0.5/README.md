# ub
Accessing data in a consistent manner

To install:	```pip install ub```

## Overview
The `ub` package provides a unified interface for accessing and manipulating data stored in various locations, specifically local filesystems and AWS S3 buckets. The main component of the package is the `DataAccessor` class, which abstracts the complexity of handling data across different storage systems. This allows users to switch between local and S3 storage seamlessly without changing their code for data access and manipulation.

## Features
- **Unified Data Access**: Interact with data without worrying about the underlying storage system.
- **Flexible Data Handling**: Easily switch between local and S3 storage.
- **Extension and Encoding Support**: Customize file extensions and encoding types as needed.

## Classes and Methods

### `DataAccessor`
A flexible class designed to facilitate the access and manipulation of data files stored either locally or on S3.

#### Constructor
```python
DataAccessor(relative_root=None, mother_root=None, extension=None, force_extension=False, encoding='UTF-8', location='LOCAL', **kwargs)
```
- `relative_root`: The base path relative to the mother root where files are stored.
- `mother_root`: The root directory or bucket name.
- `extension`: Default file extension to use.
- `force_extension`: If `True`, overrides the file's existing extension with the specified one.
- `encoding`: Character encoding for files.
- `location`: Storage location, either `'LOCAL'` or `'S3'`.

#### Methods
- `use_local(**kwargs)`: Configure the accessor to use local file storage.
- `use_s3(**kwargs)`: Configure the accessor to use S3 storage.
- `load_excel(filename)`: Load an Excel file (method implementation needs to be completed by the user).

### Dynamic Attribute Access
If an attribute or method is not directly found in the `DataAccessor` instance, it will attempt to delegate the call to the current storage handler (`local` or `s3`), allowing direct access to methods defined in these handlers.

## Usage Examples

### Initializing DataAccessor
```python
from ub import DataAccessor

# Access data from local filesystem
local_data_accessor = DataAccessor(relative_root='data/', mother_root='/path/to/data', location='LOCAL')

# Access data from S3
s3_data_accessor = DataAccessor(relative_root='data/', mother_root='my-bucket', location='S3')
```

### Switching Storage Locations
```python
data_accessor = DataAccessor(relative_root='data/', mother_root='/path/to/data')

# Initially use local storage
data_accessor.use_local()

# Switch to S3 storage
data_accessor.use_s3(mother_root='my-bucket')
```

### Loading Data
```python
# Assuming the load_excel method is properly implemented
data = data_accessor.load_excel('example.xlsx')
```

## Notes
- Ensure that AWS credentials are configured properly when using S3 storage.
- The `load_excel` method in the `DataAccessor` class is a placeholder and needs to be fully implemented based on specific requirements.

By providing a high-level abstraction over different storage systems, `ub` aims to simplify data handling tasks in Python applications, making code cleaner and more maintainable.