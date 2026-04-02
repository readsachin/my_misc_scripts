#!/bin/bash

# MongoDB Migration Script - Usage Examples
# Make sure Python and dependencies are installed first: pip install -r requirements.txt

echo "MongoDB Migration Script Examples"
echo "=================================="
echo

echo "1. Test connections first:"
echo "python test_connection.py"
echo

echo "2. Show source and destination info:"
echo "python mongo_migrate.py --info"
echo

echo "3. Dry run - copy entire database (preview only):"
echo "python mongo_migrate.py --database myapp --dry-run"
echo

echo "4. Copy entire database:"
echo "python mongo_migrate.py --database myapp"
echo

echo "5. Copy specific collection:"
echo "python mongo_migrate.py --database myapp --collection users"
echo

echo "6. Copy with verbose logging:"
echo "python mongo_migrate.py --database myapp --verbose"
echo

echo "7. Use custom config file:"
echo "python mongo_migrate.py --config production.ini --database analytics"
echo

echo "8. Dry run for specific collection:"
echo "python mongo_migrate.py --database ecommerce --collection products --dry-run"
echo

read -p "Choose an option (1-8) or press Enter to exit: " choice

case $choice in
    1)
        python test_connection.py
        ;;
    2)
        python mongo_migrate.py --info
        ;;
    3)
        read -p "Enter database name: " dbname
        python mongo_migrate.py --database "$dbname" --dry-run
        ;;
    4)
        read -p "Enter database name: " dbname
        python mongo_migrate.py --database "$dbname"
        ;;
    5)
        read -p "Enter database name: " dbname
        read -p "Enter collection name: " collname
        python mongo_migrate.py --database "$dbname" --collection "$collname"
        ;;
    6)
        read -p "Enter database name: " dbname
        python mongo_migrate.py --database "$dbname" --verbose
        ;;
    7)
        read -p "Enter config file path: " configfile
        read -p "Enter database name: " dbname
        python mongo_migrate.py --config "$configfile" --database "$dbname"
        ;;
    8)
        read -p "Enter database name: " dbname
        read -p "Enter collection name: " collname
        python mongo_migrate.py --database "$dbname" --collection "$collname" --dry-run
        ;;
    *)
        echo "Exiting..."
        ;;
esac