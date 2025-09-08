@echo off
echo Ollama timer started...
timeout /t 20 /nobreak >nul
echo ready > "%~dp0niout\ollama_status.txt"
echo Ollama is now ready!
