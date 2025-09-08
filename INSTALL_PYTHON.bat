@echo off
title AI Chat - Portable Python Installer
color 0A

echo.
echo ========================================
echo   🐍 AI CHAT PYTHON INSTALLER 🐍
echo ========================================
echo.
echo This will install Python 3.11 for AI Chat
echo Location: %~dp0python_portable
echo Size: ~15MB download
echo.
echo ✅ Completely isolated - won't affect your system
echo ✅ Includes all required modules
echo ✅ Ready to use immediately after install
echo.

set /p confirm="Continue? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Installation cancelled.
    pause
    exit /b
)

echo.
echo 📥 Starting installation...
echo.

REM Check if already installed
if exist "%~dp0python_portable\python.exe" (
    echo ✅ Python already installed!
    echo Testing installation...
    "%~dp0python_portable\python.exe" --version
    if %errorlevel% equ 0 (
        echo 🎊 Installation is working correctly!
        echo You can now use AI Chat!
        pause
        exit /b
    ) else (
        echo ⚠️ Reinstalling due to issues...
        rmdir /s /q "%~dp0python_portable" 2>nul
    )
)

REM Create python directory
mkdir "%~dp0python_portable" 2>nul

REM Download Python embeddable
echo 📥 Downloading Python 3.11.9 (embeddable)...
powershell -Command "& {try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile '%~dp0python_portable.zip'; Write-Host '✅ Download complete' } catch { Write-Host '❌ Download failed:' $_.Exception.Message; exit 1 }}"

if %errorlevel% neq 0 (
    echo ❌ Download failed! Check your internet connection.
    pause
    exit /b 1
)

REM Extract Python
echo 📂 Extracting Python...
powershell -Command "& {try { Expand-Archive -Path '%~dp0python_portable.zip' -DestinationPath '%~dp0python_portable' -Force; Write-Host '✅ Extraction complete' } catch { Write-Host '❌ Extraction failed:' $_.Exception.Message; exit 1 }}"

if %errorlevel% neq 0 (
    echo ❌ Extraction failed!
    pause
    exit /b 1
)

REM Clean up zip file
del "%~dp0python_portable.zip" 2>nul

REM Enable pip by uncommenting import site in pth file
echo 🔧 Configuring Python...
powershell -Command "& {$pthFile = Get-ChildItem '%~dp0python_portable' -Filter '*._pth' | Select-Object -First 1; if ($pthFile) { $content = Get-Content $pthFile.FullName; $content = $content -replace '^#import site', 'import site'; Set-Content $pthFile.FullName $content; Write-Host '✅ Python configured' } else { Write-Host '⚠️ Could not find pth file' }}"

REM Download and install pip
echo 📦 Installing pip...
powershell -Command "& {try { Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%~dp0python_portable\get-pip.py'; Write-Host '✅ Downloaded pip installer' } catch { Write-Host '❌ Pip download failed:' $_.Exception.Message }}"

if exist "%~dp0python_portable\get-pip.py" (
    "%~dp0python_portable\python.exe" "%~dp0python_portable\get-pip.py" --quiet --no-warn-script-location
    if %errorlevel% equ 0 (
        echo ✅ Pip installed successfully
        del "%~dp0python_portable\get-pip.py" 2>nul
    ) else (
        echo ⚠️ Pip installation had issues, continuing...
    )
)

REM Install requests module
echo 📚 Installing requests module...
"%~dp0python_portable\python.exe" -m pip install requests --quiet --no-warn-script-location
if %errorlevel% equ 0 (
    echo ✅ Requests module installed
) else (
    echo ⚠️ Requests installation had issues
)

REM Test installation
echo 🧪 Testing installation...
echo.

echo Testing Python:
"%~dp0python_portable\python.exe" --version
if %errorlevel% equ 0 (
    echo ✅ Python test passed
) else (
    echo ❌ Python test failed
)

echo.
echo Testing requests module:
"%~dp0python_portable\python.exe" -c "import requests; print('✅ Requests module working')" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Requests test passed
) else (
    echo ❌ Requests test failed
)

REM Create launcher batch file
echo 📝 Creating launcher script...
(
echo @echo off
echo REM AI Chat Python Launcher
echo set PYTHON_PATH=%~dp0python_portable
echo set PATH=%%PYTHON_PATH%%;%%PYTHON_PATH%%\Scripts;%%PATH%%
echo.
echo REM Run ollama_chat.py with portable Python
echo "%%PYTHON_PATH%%\python.exe" "%%~dp0ollama_chat.py" %%*
) > "%~dp0chat_with_portable_python.bat"

if exist "%~dp0chat_with_portable_python.bat" (
    echo ✅ Launcher created: chat_with_portable_python.bat
) else (
    echo ⚠️ Launcher creation failed
)

echo.
echo ========================================
echo         🎊 INSTALLATION COMPLETE! 🎊
echo ========================================
echo.
echo ✅ Portable Python installed successfully!
echo 📁 Location: %~dp0python_portable
echo 🐍 Python: %~dp0python_portable\python.exe
echo 🚀 Launcher: chat_with_portable_python.bat
echo.
echo You can now use AI Chat in Blender!
echo The system will automatically use this Python.
echo.
echo Press any key to close...
pause > nul
