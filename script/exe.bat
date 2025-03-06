chcp 65001
rmdir /S /Q "D:\Code\打包"
call D:\Code\HsannuTurboEnroll\.venv\Scripts\activate.bat
pyinstaller -F -w "D:\Code\HsannuTurboEnroll\program\main.pyw" -i "D:\Code\HsannuTurboEnroll\program\source\img\program.ico" -n HsannuTurboEnroll --distpath "D:\Code\打包" --workpath "D:\Code\打包\build" --clean --contents-directory source --add-data D:\Code\HsannuTurboEnroll\program\source\img:img -y
call D:\Code\HsannuTurboEnroll\.venv\Scripts\deactivate.bat
pause