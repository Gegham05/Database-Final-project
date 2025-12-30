#!/bin/bash

# This script initializes the database for the auto service application.
# It creates a new database and a user with ownership of that database.
# The script reads database connection details from the .env file in the project root.

# Function to read a variable from the .env file
get_env_var() {
    local var_name=$1
    local env_file="${PROJECT_ROOT}/${2:-.env}"
    if [ -f "$env_file" ]; then
        # Use grep and cut to extract the value of the variable
        local var_value=$(grep "^${var_name}=" "$env_file" | cut -d'=' -f2-)
        if [ -n "$var_value" ]; then
            echo "$var_value"
        else
            echo "Error: ${var_name} not found in ${env_file}" >&2
            exit 1
        fi
    else
        echo "Error: .env file not found at ${env_file}" >&2
        exit 1
    fi
}

# Set the project root directory
PROJECT_ROOT=$(dirname "$(dirname "$(realpath "$0")")")

# Read database configuration from .env file
DB_NAME=$(get_env_var "POSTGRES_DB")
DB_USER=$(get_env_var "POSTGRES_USER")
DB_PASS=$(get_env_var "POSTGRES_PASSWORD")

# Check if all variables were read successfully
if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASS" ]; then
    echo "Error: Could not read all required variables from .env file." >&2
    exit 1
fi

echo "--- Database Initialization ---"
echo "Attempting to create user '$DB_USER' and database '$DB_NAME'..."
echo "You may be prompted for the password for the postgres superuser."

# Use psql to execute the commands.
# The script will exit if any command fails.
set -e

# Create the user and database
psql -v ON_ERROR_STOP=1 --username "postgres" <<-EOSQL
    -- Create a new role (user) if it doesn't already exist
    DO
    \$do\$
    BEGIN
       IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
          CREATE ROLE "${DB_USER}" WITH LOGIN PASSWORD '${DB_PASS}';
       END IF;
    END
    \$do\$;

    -- Drop the database if it exists (for a clean slate)
    -- DROP DATABASE IF EXISTS "${DB_NAME}";

    -- Create the database with the new user as the owner
    -- Note: We check if the database exists before creating it.
    -- The owner is set after creation as it's a more reliable command.
    SELECT 'CREATE DATABASE "${DB_NAME}"'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}');
    
    -- Grant ownership of the database to the new user.
    -- This command might need to be run by a superuser if the database already
    -- exists and is owned by someone else.
    GRANT ALL PRIVILEGES ON DATABASE "${DB_NAME}" TO "${DB_USER}";
    ALTER DATABASE "${DB_NAME}" OWNER TO "${DB_USER}";

EOSQL

echo ""
echo "--- Initialization Complete ---"
echo "User '$DB_USER' and database '$DB_NAME' should now be ready."
echo "Owner of '$DB_NAME' is set to '$DB_USER'."
echo "To connect, use: psql -U $DB_USER -d $DB_NAME -h localhost"

exit 0
