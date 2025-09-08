@echo off
setlocal enabledelayedexpansion
title AI Usage Monitor
color 0A
echo.
echo ====================================
echo    Advanced AI Communication Monitor
echo ====================================
echo.
echo This monitor observes AI usage and provides statistics.
echo It does not interfere with the addon or AI operation.
echo.
echo Starting monitoring...
echo.

:MONITOR_LOOP
cls
echo.
echo ====================================
echo    AI USAGE MONITOR - %date% %time%
echo ====================================
echo.

REM Check if niout directory exists
if exist "niout" (
    echo [DIRECTORY] niout folder: FOUND
    
    REM Check for input file
    if exist "niout\input.txt" (
        echo [INPUT] Current message file: EXISTS
        for %%A in ("niout\input.txt") do echo [SIZE] Input file size: %%~zA bytes
        echo.
        echo [CONTENT] Last input message:
        echo ----------------------------------
        type "niout\input.txt" 2>nul | findstr /n "^" | more
        echo ----------------------------------
    ) else (
        echo [INPUT] Current message file: NOT FOUND
    )
    
    echo.
    
    REM Check for model config
    if exist "niout\model_config.txt" (
        echo [MODEL] Model configuration: EXISTS
        set /p current_model=<"niout\model_config.txt"
        echo [MODEL] Current AI model: !current_model!
    ) else (
        echo [MODEL] Model configuration: NOT FOUND
        echo [MODEL] Current AI model: UNKNOWN
    )
    
    echo.
    
    REM Count response files
    set response_count=0
    for %%f in ("niout\response_*.txt") do set /a response_count+=1
    
    if exist "niout\response.txt" (
        echo [RESPONSE] Main response file: EXISTS
        for %%A in ("niout\response.txt") do echo [SIZE] Response size: %%~zA bytes
        echo [RESPONSES] Versioned responses: %response_count% files
        
        REM Show latest response file info
        if %response_count% gtr 0 (
            echo.
            echo [LATEST] Most recent response files:
            dir "niout\response_*.txt" /o-d /b 2>nul | findstr /n "^" | more +0 | head -5 2>nul
        )
        
        echo.
        echo [PREVIEW] Latest response content (first 10 lines):
        echo ----------------------------------
        type "niout\response.txt" 2>nul | findstr /n "^" | more +0 | head -10 2>nul
        echo ----------------------------------
    ) else (
        echo [RESPONSE] Main response file: NOT FOUND
        echo [RESPONSES] Versioned responses: %response_count% files
    )
    
    echo.
    
    REM Memory system monitoring
    if exist "memory" (
        echo [MEMORY] Memory system: ACTIVE
        if exist "memory\conversation_history.txt" (
            for %%A in ("memory\conversation_history.txt") do echo [MEMORY] History size: %%~zA bytes
            
            REM Estimate token count (rough: 1 token per 4 characters)
            for %%A in ("memory\conversation_history.txt") do set /a estimated_tokens=%%~zA/4
            echo [MEMORY] Estimated tokens: !estimated_tokens!
            
            REM Count exchanges in memory
            findstr /c:"User: " "memory\conversation_history.txt" >nul 2>&1 && (
                for /f %%i in ('findstr /c:"User: " "memory\conversation_history.txt" 2^>nul') do echo [MEMORY] Total exchanges: %%i
            ) || (
                echo [MEMORY] Total exchanges: 0
            )
        ) else (
            echo [MEMORY] History file: NOT FOUND
        )
    ) else (
        echo [MEMORY] Memory system: INACTIVE
    )
    
    echo.
    
    REM Ollama process monitoring
    tasklist /fi "imagename eq ollama.exe" 2>nul | findstr /i "ollama.exe" >nul && (
        echo [OLLAMA] Process status: RUNNING
        for /f "tokens=5" %%a in ('tasklist /fi "imagename eq ollama.exe" /fo table ^| findstr /i "ollama.exe"') do echo [OLLAMA] Memory usage: %%a
    ) || (
        echo [OLLAMA] Process status: NOT RUNNING
    )
    
    echo.
    
    REM Timer status
    if exist "niout\ollama_status.txt" (
        echo [TIMER] Ollama status file: EXISTS
        set /p timer_status=<"niout\ollama_status.txt"
        echo [TIMER] Status: !timer_status!
    ) else (
        echo [TIMER] Ollama status file: NOT FOUND
    )
    
) else (
    echo [ERROR] niout directory not found!
    echo [INFO] Make sure you're running this from the a_astitnet directory
    echo [INFO] Current directory: %cd%
)

echo.
echo ====================================
echo Press Ctrl+C to exit monitor
echo Refreshing in 10 seconds...
echo ====================================

REM Wait 10 seconds before refreshing
timeout /t 10 /nobreak >nul

goto MONITOR_LOOP
