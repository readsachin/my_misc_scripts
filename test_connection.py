#!/usr/bin/env python3
"""
Test script to validate MongoDB connections and configuration.
Run this before using the migration script.
"""

import configparser
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


def test_connection(uri: str, name: str) -> bool:
    """Test MongoDB connection."""
    try:
        print(f"Testing {name} connection...")
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)

        # Test connection
        client.admin.command('ping')

        # Get server info
        server_info = client.server_info()
        print(f"✓ {name} connected successfully")
        print(f"  - MongoDB version: {server_info['version']}")

        # List databases
        db_names = client.list_database_names()
        user_dbs = [db for db in db_names if db not in ['admin', 'local', 'config']]
        print(f"  - Available databases: {user_dbs}")

        client.close()
        return True

    except ConnectionFailure as e:
        print(f"✗ {name} connection failed: {e}")
        return False
    except ServerSelectionTimeoutError:
        print(f"✗ {name} connection timeout - check if server is running")
        return False
    except Exception as e:
        print(f"✗ {name} unexpected error: {e}")
        return False


def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.ini'

    print(f"Testing MongoDB connections using: {config_file}")
    print("=" * 50)

    try:
        config = configparser.ConfigParser()
        config.read(config_file)

        source_uri = config.get('mongodb', 'source_uri')
        dest_uri = config.get('mongodb', 'dest_uri')

        print(f"Source URI: {source_uri}")
        print(f"Destination URI: {dest_uri}")
        print("-" * 50)

        source_ok = test_connection(source_uri, "Source")
        print()
        dest_ok = test_connection(dest_uri, "Destination")

        print("-" * 50)
        if source_ok and dest_ok:
            print("✓ All connections successful! Ready for migration.")
            sys.exit(0)
        else:
            print("✗ Connection tests failed. Please check your configuration.")
            sys.exit(1)

    except Exception as e:
        print(f"Error reading configuration: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()