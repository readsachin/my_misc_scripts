# MongoDB Migration Script

A Python script to copy MongoDB databases or collections from source to destination with support for dry-run mode and configurable options.

## Features

- Copy entire databases or specific collections
- Dry-run mode to preview operations
- Configurable batch processing
- Index copying support
- Detailed logging
- Error handling and recovery
- Drop existing collections option

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your MongoDB connections in `config.ini`:
```ini
[mongodb]
source_uri = mongodb://source-host:27017
dest_uri = mongodb://dest-host:27017

[options]
batch_size = 1000
timeout = 300
drop_existing = false
copy_indexes = true
```

## Usage

### Basic Commands

```bash
# Copy entire database
python mongo_migrate.py --database mydb

# Copy specific collection
python mongo_migrate.py --database mydb --collection mycollection

# Dry run (preview without copying)
python mongo_migrate.py --database mydb --dry-run

# Show source/destination info
python mongo_migrate.py --info

# Use custom config file
python mongo_migrate.py --config custom.ini --database mydb

# Verbose logging
python mongo_migrate.py --database mydb --verbose
```

### Configuration Options

The `config.ini` file supports the following options:

#### MongoDB Section
- `source_uri`: Source MongoDB connection URI
- `dest_uri`: Destination MongoDB connection URI

#### Options Section
- `batch_size`: Number of documents to process in each batch (default: 1000)
- `timeout`: Connection timeout in seconds (default: 300)
- `drop_existing`: Whether to drop existing collections before copying (default: false)
- `copy_indexes`: Whether to copy indexes along with data (default: true)

## Examples

### Example 1: Copy entire database
```bash
python mongo_migrate.py --database ecommerce
```

### Example 2: Copy specific collection with dry-run
```bash
python mongo_migrate.py --database ecommerce --collection products --dry-run
```

### Example 3: Copy with custom configuration
```bash
python mongo_migrate.py --config production.ini --database analytics --verbose
```

## Logging

The script creates detailed logs in:
- Console output (real-time)
- `mongo_migrate.log` file

Log levels can be controlled with the `--verbose` flag.

## Safety Features

- **Dry-run mode**: Preview operations without making changes
- **Batch processing**: Handles large collections efficiently
- **Error recovery**: Continues processing other collections if one fails
- **Connection validation**: Verifies connections before starting
- **Detailed logging**: Tracks all operations for debugging

## Troubleshooting

### Common Issues

1. **Connection timeout**: Increase `timeout` in config.ini
2. **Memory issues**: Reduce `batch_size` in config.ini
3. **Permission errors**: Check MongoDB user permissions
4. **Index creation fails**: Set `copy_indexes = false` in config.ini

### Log Files

Check `mongo_migrate.log` for detailed error information and operation history.

## Security Notes

- Store sensitive connection strings securely
- Use MongoDB authentication when possible
- Test with dry-run mode first
- Backup destination data before migration