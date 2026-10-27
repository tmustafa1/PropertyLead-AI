@echo off
title Push PropertyLead AI to GitHub
echo ========================================================
echo   PropertyLead AI - Push to GitHub Repository
echo ========================================================
echo.

set GIT_EXE="C:\Users\Admin\anaconda3\Library\bin\git.exe"

IF NOT EXIST %GIT_EXE% (
    set GIT_EXE=git
)

cd /d "%~dp0"

echo Current project directory: %CD%
echo.

%GIT_EXE% remote -v

echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/username/propertylead-ai.git): "

if "%REPO_URL%"=="" (
    echo.
    echo [ERROR] No URL provided. Exiting.
    pause
    exit /b
)

echo.
echo Setting remote 'origin' to: %REPO_URL%
%GIT_EXE% remote remove origin >nul 2>&1
%GIT_EXE% remote add origin %REPO_URL%

echo.
echo Pushing branch 'main' to GitHub...
%GIT_EXE% push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo   SUCCESS! Your project is now live on GitHub!
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo   Push failed. Please check your URL and credentials.
    echo   If GitHub requests login, authenticate via browser.
    echo ========================================================
)

pause
