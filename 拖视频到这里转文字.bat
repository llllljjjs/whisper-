@echo off
chcp 65001 >nul
setlocal

set PYTHON_EXE=C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe
set SCRIPT=C:\whisper\zhuanwenzi.py

if "%~1"=="" (
    echo ❌ 没有拖入文件
    pause
    exit /b
)

:loop
if "%~1"=="" goto end

echo.
echo ==========================================
echo 🎬 正在处理：
echo %~1
echo ==========================================

powershell -NoProfile -Command ^
  "& '%PYTHON_EXE%' '%SCRIPT%' '%~1'"

shift
goto loop

:end
echo.
echo 🎉 全部完成
pause