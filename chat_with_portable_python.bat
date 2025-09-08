@echo off
REM AI Chat Python Launcher
set PYTHON_PATH=F:\odin_grab\a_astitnet\python_portable
set PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PATH%

REM Run ollama_chat.py with portable Python
"%PYTHON_PATH%\python.exe" "%~dp0ollama_chat.py" %*
