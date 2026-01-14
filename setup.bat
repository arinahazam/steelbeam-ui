@echo off
echo [1/4] Creating Virtual Environment...
python -m venv venv

echo [2/4] Activating Environment...
call .\venv\Scripts\activate

echo [3/4] Updating Pip...
python.exe -m pip install --upgrade pip

echo [4/4] Installing Requirements...
pip install -r requirements.txt

echo.
echo ==========================================
echo SETUP COMPLETE! To start the app, run:
echo python app.py
echo ==========================================
pause