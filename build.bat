@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt

set MODE=%1
if "%MODE%"=="" set MODE=onedir

python build.py --clean --mode %MODE%
if errorlevel 1 exit /b %errorlevel%

echo.
echo Build artifacts:
dir /b /s dist
endlocal
