#!/bin/sh

echo "Running database migrations..."
uv run alembic upgrade head

if [ $? -eq 0 ]; then
    echo "Migrations completed successfully"
else
    echo "Migration failed"
    exit 1
fi

if [ -f /run/secrets/private_key.pem ]; then
    export PRIVATE_KEY_PATH="/run/secrets/private_key.pem"
    export PUBLIC_KEY_PATH="/app/secrets/public_key.pem"
    echo "SECRET_KEY has been set from secrets file"
else
    echo "Warning: /run/secrets/private_key.pem file not found, using default config"
fi
echo "Starting the application..."
exec uv run main.py