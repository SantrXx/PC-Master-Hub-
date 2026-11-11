@echo off
color 0A
echo === Cleaning old broken builds ===
rmdir /s /q build dist 2>nul
del /q *.spec 2>nul

echo === Building fresh PC_Master_Hub_v2.exe (Wait 30-45 sec) ===
py -m PyInstaller --noconfirm --clean --onefile --windowed --collect-all customtkinter --name "PC_Master_Hub_v2" pc_master_hub.py

echo === Launching your new EXE! ===
start "" "dist\PC_Master_Hub_v2.exe"
pause