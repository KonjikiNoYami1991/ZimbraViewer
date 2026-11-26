@echo off
rem ============================================================
rem  Build di Zimbra Local Viewer con PyInstaller
rem  Uso:   build_zimbra.bat            -> un solo .exe (--onefile)
rem         build_zimbra.bat onedir     -> cartella (avvio piu' veloce)
rem ============================================================
setlocal
cd /d "%~dp0"

set "SCRIPT=ZimbraViewer 3.2.py"
set "NOME=ZimbraViewer"
set "ICONA=zimbra_icon.ico"
set "VERSIONE=version_info.txt"

set "MODO=--onefile"
if /i "%~1"=="onedir" set "MODO=--onedir"

if not exist "%SCRIPT%" (
    echo [ERRORE] Non trovo "%SCRIPT%" in questa cartella.
    pause
    exit /b 1
)

echo.
echo [1/4] Installo/aggiorno le dipendenze...
python -m pip install --upgrade pip pyinstaller PyQt6 PyQt6-WebEngine asn1crypto pyhanko pyhanko-certvalidator cryptography lxml olefile certifi tzdata
if errorlevel 1 goto errore
rem cryptography per Python 3.15 si lega a python3t.dll, che PyInstaller non include da solo
set "DLL_ARG="
for /f "delims=" %%D in ('python -c "import os,sys;p=os.path.join(sys.base_prefix,'abi3t-compat','python3t.dll');print(p if os.path.exists(p) else '')"') do if not "%%D"=="" set "DLL_ARG=--add-binary=%%D;."

echo.
echo [2/4] Controllo icona e informazioni di versione...
set "ICON_ARG="
set "VERSION_ARG="
if exist "%ICONA%" (set "ICON_ARG=--icon=%ICONA%") else (echo [AVVISO] "%ICONA%" non trovata: compilo senza icona. Avvia una volta il .py per generarla.)
if exist "%VERSIONE%" (set "VERSION_ARG=--version-file=%VERSIONE%") else (echo [AVVISO] "%VERSIONE%" non trovato: compilo senza info di versione.)

echo.
echo [3/4] Compilazione in corso (%MODO%)...
python -m PyInstaller ^
  --noconfirm --clean ^
  %MODO% ^
  --noconsole ^
  --name "%NOME%" ^
  %ICON_ARG% ^
  %VERSION_ARG% ^
  %DLL_ARG% ^
  --hidden-import PyQt6.QtWebEngineCore ^
  --hidden-import PyQt6.QtWebEngineWidgets ^
  --exclude-module tkinter ^
  --exclude-module unittest ^
  --exclude-module matplotlib ^
  --exclude-module numpy ^
  --exclude-module scipy ^
  --exclude-module pandas ^
  --exclude-module PIL ^
  --noupx ^
  "%SCRIPT%"
if errorlevel 1 goto errore

echo.
echo [4/4] Pulizia file temporanei di build...
if exist build rmdir /s /q build

echo.
echo ============================================================
echo  FATTO!
if /i "%MODO%"=="--onedir" (
    echo  Programma in: dist\%NOME%\%NOME%.exe
) else (
    echo  Programma in: dist\%NOME%.exe
)
echo ============================================================
explorer dist
pause
exit /b 0

:errore
echo.
echo [ERRORE] La build e' fallita: controlla i messaggi qui sopra.
pause
exit /b 1
