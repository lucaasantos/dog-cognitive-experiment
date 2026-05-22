@echo off
setlocal

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
    goto :done
)

set "BUNDLED_PYTHON=C:\Users\lucasdoutzen.vita\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if exist "%BUNDLED_PYTHON%" (
    "%BUNDLED_PYTHON%" -B main.py
    goto :done
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -B main.py
    goto :done
)

where python >nul 2>nul
if %errorlevel%==0 (
    python main.py
    goto :done
)

echo Python was not found.
echo Install Python from https://www.python.org/downloads/ and run:
echo pip install -r requirements.txt
echo python main.py

:done
if errorlevel 1 (
    echo.
    echo The app could not start. Check the error above.
    pause
)
