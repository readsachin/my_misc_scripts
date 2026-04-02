@echo off
REM MongoDB Migration Script - Usage Examples
REM Make sure Python and dependencies are installed first: pip install -r requirements.txt

echo MongoDB Migration Script Examples
echo ===================================
echo.

echo 1. Test connections first:
echo python test_connection.py
echo.

echo 2. Show source and destination info:
echo python mongo_migrate.py --info
echo.

echo 3. Dry run - copy entire database (preview only):
echo python mongo_migrate.py --database myapp --dry-run
echo.

echo 4. Copy entire database:
echo python mongo_migrate.py --database myapp
echo.

echo 5. Copy specific collection:
echo python mongo_migrate.py --database myapp --collection users
echo.

echo 6. Copy with verbose logging:
echo python mongo_migrate.py --database myapp --verbose
echo.

echo 7. Use custom config file:
echo python mongo_migrate.py --config production.ini --database analytics
echo.

echo 8. Dry run for specific collection:
echo python mongo_migrate.py --database ecommerce --collection products --dry-run
echo.

echo Choose an option (1-8) or press any key to exit:
set /p choice="Enter your choice: "

if "%choice%"=="1" (
    python test_connection.py
) else if "%choice%"=="2" (
    python mongo_migrate.py --info
) else if "%choice%"=="3" (
    set /p dbname="Enter database name: "
    python mongo_migrate.py --database %dbname% --dry-run
) else if "%choice%"=="4" (
    set /p dbname="Enter database name: "
    python mongo_migrate.py --database %dbname%
) else if "%choice%"=="5" (
    set /p dbname="Enter database name: "
    set /p collname="Enter collection name: "
    python mongo_migrate.py --database %dbname% --collection %collname%
) else if "%choice%"=="6" (
    set /p dbname="Enter database name: "
    python mongo_migrate.py --database %dbname% --verbose
) else if "%choice%"=="7" (
    set /p configfile="Enter config file path: "
    set /p dbname="Enter database name: "
    python mongo_migrate.py --config %configfile% --database %dbname%
) else if "%choice%"=="8" (
    set /p dbname="Enter database name: "
    set /p collname="Enter collection name: "
    python mongo_migrate.py --database %dbname% --collection %collname% --dry-run
) else (
    echo Exiting...
)

pause