@echo off
setlocal

where pyinstaller >nul 2>nul
if errorlevel 1 (
  echo [ERRO] PyInstaller nao encontrado. Execute: pip install -r requirements.txt
  exit /b 1
)

pyinstaller --noconfirm --clean --windowed --name trader_ia --collect-all PySide6 --hidden-import PySide6.QtWebEngineWidgets --hidden-import PySide6.QtWebEngineCore app/main.py
if errorlevel 1 (
  echo [ERRO] Build falhou.
  exit /b 1
)

echo Build finalizado. Arquivo em dist\trader_ia.exe
exit /b 0
