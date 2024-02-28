@echo off
SET PYTHON_INSTALLER=python-3.12.0-amd64.exe
SET DOWNLOAD_URL=https://www.python.org/ftp/python/3.12.0/%PYTHON_INSTALLER%

:: ダウンロードURLからPythonインストーラーをダウンロード
powershell -Command "Invoke-WebRequest -Uri %DOWNLOAD_URL% -OutFile %PYTHON_INSTALLER%"

:: インストーラーを起動し、ユーザーにGUIでのインストールを促す
start "" %PYTHON_INSTALLER%

echo Pythonインストーラーを起動しました。GUIに従ってインストールを進めてください。
pause
