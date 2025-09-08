@echo off
echo Checking Python Installation...
echo =====================================

echo Testing 'python' command:
python --version 2>nul
if %errorlevel% neq 0 (
    echo   FAILED: 'python' not found
) else (
    echo   SUCCESS: 'python' found
)

echo.
echo Testing 'py' command:
py --version 2>nul
if %errorlevel% neq 0 (
    echo   FAILED: 'py' not found
) else (
    echo   SUCCESS: 'py' found
)

echo.
echo Testing 'python3' command:
python3 --version 2>nul
if %errorlevel% neq 0 (
    echo   FAILED: 'python3' not found
) else (
    echo   SUCCESS: 'python3' found
)

echo.
echo Testing 'requests' module:
python -c "import requests; print('SUCCESS: requests module found')" 2>nul
if %errorlevel% neq 0 (
    echo   FAILED: 'requests' module not found
    echo   Install with: pip install requests
) else (
    echo   SUCCESS: 'requests' module found
)

echo.
echo Testing Ollama connection:
python -c "import requests; r=requests.get('http://localhost:11434/api/tags', timeout=2); print('SUCCESS: Ollama is running')" 2>nul
if %errorlevel% neq 0 (
    echo   FAILED: Cannot connect to Ollama
    echo   Make sure Ollama is running: ollama serve
) else (
    echo   SUCCESS: Ollama is running
)

echo.
echo =====================================
echo If you see failures above, fix them before using the AI chat.
echo.
pause
