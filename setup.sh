#!/usr/bin/env bash
set -e

echo "================================"
echo "Setting up Python Virtual Env"
echo "================================"

# -------------------------------------------------
# Check Python
# -------------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python3 is not installed or not in PATH"
    exit 1
fi

python3 --version

# -------------------------------------------------
# Create virtual environment
# -------------------------------------------------
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists"
fi

# -------------------------------------------------
# Activate virtual environment
# -------------------------------------------------
# shellcheck disable=SC1091
source .venv/bin/activate

# -------------------------------------------------
# Upgrade pip
# -------------------------------------------------
python -m pip install --upgrade pip

# -------------------------------------------------
# Install dependencies
# -------------------------------------------------
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found, skipping dependency installation"
fi

# -------------------------------------------------
# Create .env file if missing
# -------------------------------------------------
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat <<EOF > .env
# -----------------------------------
# Credentials
# -----------------------------------
TEST_USERNAME=
TEST_PASSWORD=
EOF
    echo ".env file created. Please fill in credentials."
else
    echo ".env file already exists"
fi

echo "================================"
echo "Setup completed successfully"
echo "================================"
