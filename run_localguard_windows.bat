@echo off
REM Script de lancement Windows pour LocalGuard SLM

echo ============================================
echo   LocalGuard SLM - demo (10 messages)
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERREUR] Python n'est pas disponible dans le PATH.
    echo Installer Python 3.10 ou superieur depuis https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Verification de l'environnement virtuel...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo Environnement virtuel active.
) else (
    echo Aucun environnement virtuel detecte. Utilisation du Python systeme.
)

echo.
echo Lancement de la demo...
echo.

python src\run_demo.py --model gemma3:1b --limit 10

echo.
echo ============================================
echo   Termine. Les resultats sont dans results\
echo ============================================
echo.
pause
