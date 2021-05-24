@echo off
title NawBot: starting...

:check_perms
net session >nul 2>&1
    if %errorLevel% == 0 (
        echo [FATAL]: Administrator privileges detected!
        pause
        exit /b 1
    )

:check_python
WHERE python3
IF %ERRORLEVEL% NEQ 0 (
    set pyexec="python"
) ELSE (
    set pyexec="python3"
)


:check_ffmpeg
WHERE ffmpeg
IF %ERRORLEVEL% NEQ 0 (
    echo [WARN]: FFMPEG not found on PATH, voice functions will be disabled!
    set voiceargs="--novoice"
) ELSE (
    set voiceargs=""
)

:run_bot
if EXIST "Pipfile.lock" (
    echo [INFO]: Running in pipenv
   %pyexec%  -m pipenv run %pyexec% main.py %voiceargs% %*
) ELSE (
   %pyexec% main.py %*
)
pause
exit /b 0
