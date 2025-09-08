@echo off
title AI Chat - System Test
color 0B

echo.
echo ========================================
echo      🧪 AI CHAT SYSTEM TEST 🧪
echo ========================================
echo.

REM Test 1: Check for Python installations
echo 🐍 Testing Python installations...
echo.

echo Testing portable Python:
if exist "%~dp0python_portable\python.exe" (
    echo ✅ Found: %~dp0python_portable\python.exe
    "%~dp0python_portable\python.exe" --version
    "%~dp0python_portable\python.exe" -c "import requests; print('✅ Requests module OK')" 2>nul
    if %errorlevel% equ 0 (
        echo ✅ Portable Python ready to use!
        set PYTHON_FOUND=1
    ) else (
        echo ⚠️ Portable Python has issues
    )
) else (
    echo ❌ Portable Python not found
    echo 💡 Run INSTALL_PYTHON.bat to install it
)

echo.
echo Testing system Python:
python --version 2>nul
if %errorlevel% equ 0 (
    echo ✅ System Python found
    python -c "import requests; print('✅ System Python + Requests OK')" 2>nul
    if %errorlevel% equ 0 (
        echo ✅ System Python ready to use!
        set PYTHON_FOUND=1
    ) else (
        echo ⚠️ System Python missing requests module
        echo 💡 Run: pip install requests
    )
) else (
    echo ❌ System Python not found
)

echo.
echo ========================================

REM Test 2: Check for required files
echo 📁 Testing required files...
echo.

if exist "%~dp0ollama_chat.py" (
    echo ✅ ollama_chat.py found
) else (
    echo ❌ ollama_chat.py missing!
)

if exist "%~dp0niout" (
    echo ✅ niout folder found
    if exist "%~dp0niout\input.txt" (
        echo ✅ input.txt found
    ) else (
        echo ⚠️ input.txt will be created when needed
    )
    if exist "%~dp0niout\response.txt" (
        echo ✅ response.txt found
    ) else (
        echo ⚠️ response.txt will be created when needed
    )
) else (
    echo ❌ niout folder missing!
    mkdir "%~dp0niout" 2>nul
    echo ✅ Created niout folder
)

if exist "%~dp0addon\ai_chat" (
    echo ✅ Blender addon found
) else (
    echo ❌ Blender addon folder missing!
)

echo.
echo ========================================

REM Test 3: Check Ollama connection
echo 🤖 Testing Ollama connection...
echo.

if defined PYTHON_FOUND (
    if exist "%~dp0python_portable\python.exe" (
        set PYTHON_CMD="%~dp0python_portable\python.exe"
    ) else (
        set PYTHON_CMD=python
    )
    
    %PYTHON_CMD% -c "import requests; r=requests.get('http://localhost:11434/api/tags', timeout=3); print('✅ Ollama is running and accessible')" 2>nul
    if %errorlevel% equ 0 (
        echo ✅ Ollama connection successful!
        echo.
        echo 🎯 Testing model list...
        %PYTHON_CMD% -c "import requests; r=requests.get('http://localhost:11434/api/tags', timeout=3); import json; data=r.json(); models=[m['name'] for m in data.get('models', [])]; print('Available models:', ', '.join(models) if models else 'None')" 2>nul
    ) else (
        echo ❌ Cannot connect to Ollama
        echo.
        echo 💡 Make sure Ollama is running:
        echo    - Start Ollama desktop app, or
        echo    - Run: ollama serve
        echo    - Install models: ollama pull qwen3:4b
    )
) else (
    echo ⚠️ No working Python found - cannot test Ollama
    echo 💡 Run INSTALL_PYTHON.bat first
)

echo.
echo ========================================

REM Final summary
echo 📋 SYSTEM STATUS SUMMARY:
echo.

if exist "%~dp0python_portable\python.exe" (
    echo ✅ Portable Python: Ready
) else (
    if defined PYTHON_FOUND (
        echo ✅ System Python: Ready
    ) else (
        echo ❌ Python: MISSING - Run INSTALL_PYTHON.bat
    )
)

if exist "%~dp0addon\ai_chat" (
    echo ✅ Blender Addon: Ready
) else (
    echo ❌ Blender Addon: MISSING
)

if exist "%~dp0ollama_chat.py" (
    echo ✅ Chat Script: Ready
) else (
    echo ❌ Chat Script: MISSING
)

echo.
if defined PYTHON_FOUND (
    echo 🎊 AI Chat system is ready to use!
    echo.
    echo Next steps:
    echo 1. Make sure Ollama is running
    echo 2. Install Blender addon from addon/ai_chat/
    echo 3. Start chatting!
) else (
    echo ⚠️ AI Chat system needs Python
    echo.
    echo Next steps:
    echo 1. Double-click INSTALL_PYTHON.bat
    echo 2. Make sure Ollama is running
    echo 3. Install Blender addon from addon/ai_chat/
    echo 4. Start chatting!
)

echo.
echo Press any key to close...
pause > nul
