@echo off
echo ===================================================
echo Setting up Odoo Hydration Environment (Windows)
echo ===================================================

echo Creating Python Virtual Environment (venv)...
python -m venv venv

echo Activating venv and installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ===================================================
echo Environment setup complete!
echo To use the script, run:
echo    call venv\Scripts\activate.bat
echo    python main.py --help
echo ===================================================
