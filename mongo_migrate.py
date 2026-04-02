#!/usr/bin/env python3
"""
MongoDB Database Migration Script

This script copies databases or collections from source MongoDB to destination MongoDB.
Supports dry-run mode and configurable options via config.ini file.
"""

import argparse
import configparser
import sys
import logging
from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from bson import ObjectId
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mongo_migrate.log')
    ]
)
logger = logging.getLogger(__name__)


class MongoMigrator:
    def __init__(self, config_file: str = 'config.ini'):
        """Initialize MongoDB migrator with configuration."""
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(config_file)

        # Get connection details
        self.source_uri = self.config.get('mongodb', 'source_uri')
        self.dest_uri = self.config.get('mongodb', 'dest_uri')

        # Get options
        self.batch_size = self.config.getint('options', 'batch_size', fallback=1000)
        self.timeout = self.config.getint('options', 'timeout', fallback=300)
        self.drop_existing = self.config.getboolean('options', 'drop_existing', fallback=False)
        self.copy_indexes = self.config.getboolean('options', 'copy_indexes', fallback=True)

        self.source_client = None
        self.dest_client = None

    def connect(self) -> bool:
        """Establish connections to source and destination MongoDB instances."""
        try:
            logger.info("Connecting to source MongoDB...")
            self.source_client = MongoClient(
                self.source_uri,
                serverSelectionTimeoutMS=self.timeout * 1000
            )
            # Test connection
            self.source_client.admin.command('ping')
            logger.info("SUCCESS: Connected to source MongoDB")

            logger.info("Connecting to destination MongoDB...")
            self.dest_client = MongoClient(
                self.dest_uri,
                serverSelectionTimeoutMS=self.timeout * 1000
            )
            # Test connection
            self.dest_client.admin.command('ping')
            logger.info("SUCCESS: Connected to destination MongoDB")

            return True

        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            return False

    def disconnect(self):
        """Close MongoDB connections."""
        if self.source_client:
            self.source_client.close()
        if self.dest_client:
            self.dest_client.close()
        logger.info("Disconnected from MongoDB instances")

    def list_databases(self, client: MongoClient) -> List[str]:
        """List all databases in MongoDB instance."""
        try:
            db_list = client.list_database_names()
            # Filter out system databases
            return [db for db in db_list if db not in ['admin', 'local', 'config']]
        except Exception as e:
            logger.error(f"Error listing databases: {e}")
            return []

    def list_collections(self, client: MongoClient, db_name: str) -> List[str]:
        """List all collections in a database."""
        try:
            db = client[db_name]
            return db.list_collection_names()
        except Exception as e:
            logger.error(f"Error listing collections in {db_name}: {e}")
            return []

    def copy_indexes(self, source_collection, dest_collection, dry_run: bool = False):
        """Copy indexes from source to destination collection."""
        if not self.copy_indexes:
            return

        try:
            indexes = list(source_collection.list_indexes())
            for index in indexes:
                if index['name'] == '_id_':
                    continue  # Skip default _id index

                index_spec = {
                    'keys': list(index['key'].items()),
                    'name': index['name']
                }

                # Add other index properties if they exist
                for prop in ['unique', 'sparse', 'background', 'expireAfterSeconds']:
                    if prop in index:
                        index_spec[prop] = index[prop]

                if dry_run:
                    logger.info(f"[DRY RUN] Would create index: {index['name']}")
                else:
                    try:
                        dest_collection.create_index(
                            index_spec['keys'],
                            **{k: v for k, v in index_spec.items() if k != 'keys'}
                        )
                        logger.info(f"SUCCESS: Created index: {index['name']}")
                    except Exception as e:
                        logger.warning(f"Failed to create index {index['name']}: {e}")

        except Exception as e:
            logger.error(f"Error copying indexes: {e}")

    def copy_collection(self, db_name: str, collection_name: str, dry_run: bool = False) -> bool:
        """Copy a single collection from source to destination."""
        try:
            logger.info(f"Accessing database: {db_name}")
            source_db = self.source_client[db_name]
            dest_db = self.dest_client[db_name]

            logger.info(f"Accessing collection: {collection_name}")
            # Use get_collection() to avoid naming conflicts
            source_collection = source_db.get_collection(collection_name)
            dest_collection = dest_db.get_collection(collection_name)

            logger.info(f"Collection objects created successfully")
            logger.info(f"Source collection type: {type(source_collection)}")
            logger.info(f"Destination collection type: {type(dest_collection)}")

            logger.info(f"Getting document count for collection: {collection_name}")
            # Get document count with specific error handling
            try:
                doc_count = source_collection.count_documents({})
                logger.info(f"Collection {collection_name} has {doc_count} documents")
            except Exception as count_error:
                logger.error(f"Error getting document count: {count_error}")
                logger.error(f"Error type: {type(count_error)}")
                raise

            if dry_run:
                logger.info(f"[DRY RUN] Would copy {doc_count} documents from {collection_name}")
                if self.drop_existing:
                    logger.info(f"[DRY RUN] Would drop existing collection: {collection_name}")
                return True

            # Drop existing collection if configured
            if self.drop_existing:
                dest_collection.drop()
                logger.info(f"Dropped existing collection: {collection_name}")

            # Copy documents in batches
            copied_count = 0
            batch_num = 0

            logger.info(f"Creating cursor for collection: {collection_name}")
            try:
                cursor = source_collection.find().batch_size(self.batch_size)
                logger.info(f"Cursor created successfully")
            except Exception as cursor_error:
                logger.error(f"Error creating cursor: {cursor_error}")
                raise

            batch = []
            logger.info(f"Starting document iteration")
            try:
                for doc in cursor:
                    batch.append(doc)

                    if len(batch) >= self.batch_size:
                        try:
                            dest_collection.insert_many(batch)
                            copied_count += len(batch)
                            batch_num += 1
                            logger.info(f"Copied batch {batch_num}: {copied_count}/{doc_count} documents")
                            batch = []
                        except Exception as e:
                            logger.error(f"Error inserting batch: {e}")
                            raise

                # Insert remaining documents
                if batch:
                    try:
                        dest_collection.insert_many(batch)
                        copied_count += len(batch)
                        logger.info(f"Copied final batch: {copied_count}/{doc_count} documents")
                    except Exception as e:
                        logger.error(f"Error inserting final batch: {e}")
                        raise

            except Exception as iteration_error:
                logger.error(f"Error during document iteration: {iteration_error}")
                logger.error(f"Error type: {type(iteration_error)}")
                raise

            # Copy indexes
            self.copy_indexes(source_collection, dest_collection, dry_run)

            logger.info(f"SUCCESS: Successfully copied collection: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error copying collection {collection_name}: {e}")
            return False

    def copy_database(self, db_name: str, specific_collection: Optional[str] = None, dry_run: bool = False) -> bool:
        """Copy entire database or specific collection."""
        try:
            # Check if source database exists
            if db_name not in self.list_databases(self.source_client):
                logger.error(f"Source database '{db_name}' not found")
                return False

            logger.info(f"Starting copy of database: {db_name}")

            if specific_collection:
                # Copy only specific collection
                collections = [specific_collection]
                if specific_collection not in self.list_collections(self.source_client, db_name):
                    logger.error(f"Collection '{specific_collection}' not found in database '{db_name}'")
                    return False
            else:
                # Copy all collections
                collections = self.list_collections(self.source_client, db_name)

            if not collections:
                logger.warning(f"No collections found in database: {db_name}")
                return True

            logger.info(f"Collections to copy: {collections}")

            success_count = 0
            for collection_name in collections:
                logger.info(f"Copying collection: {collection_name}")
                if self.copy_collection(db_name, collection_name, dry_run):
                    success_count += 1
                else:
                    logger.error(f"Failed to copy collection: {collection_name}")

            if success_count == len(collections):
                logger.info(f"SUCCESS: Successfully copied all collections from database: {db_name}")
                return True
            else:
                logger.warning(f"Copied {success_count}/{len(collections)} collections")
                return False

        except Exception as e:
            logger.error(f"Error copying database {db_name}: {e}")
            return False

    def show_info(self):
        """Display information about source and destination."""
        logger.info("=== Migration Information ===")
        logger.info(f"Source URI: {self.source_uri}")
        logger.info(f"Destination URI: {self.dest_uri}")
        logger.info(f"Batch size: {self.batch_size}")
        logger.info(f"Timeout: {self.timeout}s")
        logger.info(f"Drop existing: {self.drop_existing}")
        logger.info(f"Copy indexes: {self.copy_indexes}")

        # List source databases
        source_dbs = self.list_databases(self.source_client)
        logger.info(f"Source databases: {source_dbs}")

        # List destination databases
        dest_dbs = self.list_databases(self.dest_client)
        logger.info(f"Destination databases: {dest_dbs}")


def main():
    parser = argparse.ArgumentParser(
        description='MongoDB Database Migration Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Copy entire database
  python mongo_migrate.py --database mydb

  # Copy specific collection
  python mongo_migrate.py --database mydb --collection mycollection

  # Dry run (no actual copying)
  python mongo_migrate.py --database mydb --dry-run

  # Use custom config file
  python mongo_migrate.py --config custom_config.ini --database mydb

  # Show info about source and destination
  python mongo_migrate.py --info
        """
    )

    parser.add_argument(
        '--config', '-c',
        default='config.ini',
        help='Configuration file path (default: config.ini)'
    )

    parser.add_argument(
        '--database', '-d',
        help='Database name to copy'
    )

    parser.add_argument(
        '--collection', '-t',
        help='Specific collection/table name to copy (optional)'
    )

    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Perform a dry run without actual copying'
    )

    parser.add_argument(
        '--info', '-i',
        action='store_true',
        help='Show information about source and destination'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize migrator
    try:
        migrator = MongoMigrator(args.config)
    except Exception as e:
        logger.error(f"Failed to initialize migrator: {e}")
        sys.exit(1)

    # Connect to MongoDB instances
    if not migrator.connect():
        sys.exit(1)

    try:
        if args.info:
            migrator.show_info()
        elif args.database:
            if args.dry_run:
                logger.info("=== DRY RUN MODE - No changes will be made ===")

            success = migrator.copy_database(
                args.database,
                args.collection,
                args.dry_run
            )

            if not success:
                logger.error("Migration failed!")
                sys.exit(1)
            else:
                logger.info("Migration completed successfully!")
        else:
            parser.print_help()
            logger.error("Please specify --database or --info")
            sys.exit(1)

    finally:
        migrator.disconnect()


if __name__ == '__main__':
    main()