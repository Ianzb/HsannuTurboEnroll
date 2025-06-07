chcp 65001
rmdir /S /Q "..\build"
call ..\.venv\Scripts\activate.bat
pyinstaller -F -w "..\program\main.pyw" -i "..\program\source\img\program.ico" -n HsannuTurboEnroll --distpath "..\build" --workpath "..\build\build" --clean --contents-directory source --add-data ..\program\source\img:img -y
call ..\.venv\Scripts\deactivate.bat
pause