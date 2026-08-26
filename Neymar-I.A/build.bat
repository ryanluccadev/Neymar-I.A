@echo off
setlocal

python -m pip install -r requirements.txt
python -m pip install pyinstaller

pyinstaller --noconfirm --clean --windowed --onefile --name "Neymar IA" main.py

echo.
echo Build concluido. O executavel esta em dist\Neymar IA.exe
pause
