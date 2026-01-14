@echo off
echo ================================
echo Setting up Python Virtual Env
echo ================================

REM Check Python
python --version
IF ERRORLEVEL 1 (
    echo Python is not installed or not in PATH
    exit /b 1
)

REM Create venv
IF NOT EXIST .venv (
    echo Creating virtual environment...
    python -m venv .venv
) ELSE (
    echo Virtual environment already exists
)

REM Activate venv
call .venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt

REM -------------------------------------------------
REM Create .env file if missing
REM -------------------------------------------------
IF NOT EXIST .env (
    echo Creating .env file...
    (
        echo # -----------------------------------
        echo # Credentials
        echo # -----------------------------------
        echo TEST_USERNAME=
        echo TEST_PASSWORD=
    ) > .env
    echo .env file created. Please fill in credentials.
) ELSE (
    echo .env file already exists
)

echo ================================
echo Setup completed successfully
echo ================================