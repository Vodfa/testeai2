@echo off
pyinstaller --noconfirm --windowed --name trader_ia --collect-all PySide6 app/main.py
echo Build finalizado. Arquivo em dist\trader_ia.exe
