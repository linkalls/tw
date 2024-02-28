@echo off
chcp 65001 > nul
echo Pythonの追加パッケージをインストールしています...

:: Pythonがインストールされているか確認
where python > nul
if %errorlevel% neq 0 (
    echo Pythonがインストールされていません。先にPythonをインストールしてください。
    exit /b
)

:: pipを使用してパッケージをインストール
python -m pip install --upgrade pip
python -m pip install PySimpleGUI requests selenium chromedriver-binary-sync

echo パッケージのインストールが完了しました。
pause
