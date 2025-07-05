@echo off
echo Kích hoạt môi trường ảo...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo Lỗi: Không thể kích hoạt môi trường ảo. Vui lòng kiểm tra thư mục venv.
    pause
    exit /b %ERRORLEVEL%
)

echo Cài đặt thư viện...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Lỗi: Không thể cài đặt thư viện. Vui lòng kiểm tra requirements.txt.
    pause
    exit /b %ERRORLEVEL%
)

echo Khởi chạy ứng dụng Flask...
python app.py
if %ERRORLEVEL% NEQ 0 (
    echo Lỗi: Không thể khởi chạy ứng dụng. Vui lòng kiểm tra app.py và log.
    pause
    exit /b %ERRORLEVEL%
)

pause