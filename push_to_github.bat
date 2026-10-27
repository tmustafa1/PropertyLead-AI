@echo off
title Push PropertyLead AI to GitHub
echo ========================================================
echo   PropertyLead AI - Pushing to GitHub
echo   Repository: https://github.com/tmustafa1/PropertyLead-AI.git
echo ========================================================
echo.

set GIT_EXE="C:\Users\Admin\anaconda3\Library\bin\git.exe"

IF NOT EXIST %GIT_EXE% (
    set GIT_EXE=git
)

cd /d "%~dp0"

echo Project directory: %CD%
echo.

%GIT_EXE% remote remove origin >nul 2>&1
%GIT_EXE% remote add origin https://github.com/tmustafa1/PropertyLead-AI.git

echo Pushing branch 'main' to GitHub...
echo (If a GitHub sign-in window or browser tab pops up, click "Sign in with your browser" / "Authorize")
echo.

%GIT_EXE% push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo   SUCCESS! Your project is now live on GitHub:
    echo   https://github.com/tmustafa1/PropertyLead-AI
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo   Push did not complete. If you saw a login prompt,
    echo   please approve it and run this script again.
    echo ========================================================
)

pause
