::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAjk
::fBw5plQjdCyDJGyX8VAjFBBbTgHCPnm7CL4Z/NTf6vmMtkINaGfulwoCLzJm6mXoNAW2JcR7myoD1ZtUTEoPK0b4P0E9qmEi
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSDk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+JeA==
::cxY6rQJ7JhzQF1fEqQJQ
::ZQ05rAF9IBncCkqN+0xwdVs0
::ZQ05rAF9IAHYFVzEqQJQ
::eg0/rx1wNQPfEVWB+kM9LVsJDGQ=
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWDk=
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATElA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCyDJGyX8VAjFBBbTgHCPnm7CL4Z/NTf6vmMtkINaPU3cZzL36bFK+8B5VfrO5M10xo=
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off
setlocal

if /i "%~1"=="kokoro" goto :KOKORO
if /i "%~1"=="whisper" goto :WHISPER

if not exist "D:\VerityAI\envs\kokoro\python.exe" (
    echo ERROR: Cannot find Kokoro Python:
    echo D:\VerityAI\envs\kokoro\python.exe
    pause
    exit /b 1
)
if not exist "D:\VerityAI\envs\whisper\python.exe" (
    echo ERROR: Cannot find Whisper Python:
    echo D:\VerityAI\envs\whisper\python.exe
    pause
    exit /b 1
)
if not exist "D:\VerityAI\kokoro\kokoro_api.py" (
    echo ERROR: Cannot find D:\VerityAI\kokoro\kokoro_api.py
    pause
    exit /b 1
)
if not exist "D:\VerityAI\whisper\whisper_api.py" (
    echo ERROR: Cannot find D:\VerityAI\whisper\whisper_api.py
    pause
    exit /b 1
)

start "Kokoro TTS - port 8880" "%ComSpec%" /k ""%~f0" kokoro"
start "Whisper STT - port 9000" "%ComSpec%" /k ""%~f0" whisper"
exit /b 0

:KOKORO
set "HF_HOME=D:\VerityAI\hf_cache"
set "HF_HUB_CACHE=D:\VerityAI\hf_cache\hub"
set "HF_HUB_OFFLINE=1"
"D:\VerityAI\envs\kokoro\python.exe" "D:\VerityAI\kokoro\kokoro_api.py"
echo Kokoro service stopped or failed to start.
pause
exit /b

:WHISPER
set "HF_HUB_OFFLINE=1"
"D:\VerityAI\envs\whisper\python.exe" "D:\VerityAI\whisper\whisper_api.py"
echo Whisper service stopped or failed to start.
pause
exit /b
