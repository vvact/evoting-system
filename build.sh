#!/usr/bin/env bash

set -o errexit  # Exit immediately if a command exits with a non-zero status
set -o pipefail # Exit if any command in a pipeline fails

# ----------------------------
# 1️⃣ Force Python 3.12
# ----------------------------
# Use system Python 3.12 if available
PYTHON_BIN=$(which python3.12 || true)

if [ -z "$PYTHON_BIN" ]; then
    echo "Python 3.12 not found. Make sure runtime.txt exists and is correct."
    exit 1
fi

echo "Using Python: $($PYTHON_BIN --version)"

# ----------------------------
# 2️⃣ Install dependencies
# ----------------------------
echo "Installing dependencies from requirements.txt..."
$PYTHON_BIN -m pip install --upgrade pip setuptools wheel
$PYTHON_BIN -m pip install -r requirements.txt

# ----------------------------
# 3️⃣ Run migrations
# ----------------------------
echo "Running Django migrations..."
$PYTHON_BIN manage.py migrate --noinput

# ----------------------------
# 4️⃣ Collect static files
# ----------------------------
echo "Collecting static files..."
$PYTHON_BIN manage.py collectstatic --noinput

echo "✅ Build completed successfully!"