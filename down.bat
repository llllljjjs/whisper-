@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 修改标题，避免使用感叹号（因为开启了延迟扩展）
title YouTube 最小体积下载 - 自动封装MP4

:: 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: 设置工具路径
set "ytdlp=%SCRIPT_DIR%\yt-dlp.exe"
set "cookies=%SCRIPT_DIR%\cookies.txt"
set "ffmpeg=%SCRIPT_DIR%\ffmpeg.exe"

:: 检查 yt-dlp
if not exist "%ytdlp%" (
    echo 错误：找不到 %ytdlp%
    pause
    exit /b
)

:: 检查 ffmpeg
if not exist "%ffmpeg%" (
    echo 警告：找不到 ffmpeg.exe，将无法处理 WebM。
    set "ffmpeg="
)

:: 获取视频链接（支持命令行参数）
set "video_url=%~1"
if "%video_url%"=="" (
    set /p "video_url=请输入 YouTube 视频链接："
    if "!video_url!"=="" exit /b
)

:: 设置自动模式标志（判断第二个参数是否为 --auto）
set "AUTO_MODE=0"
if "%~2"=="--auto" set "AUTO_MODE=1"
if "%~1"=="--auto" set "AUTO_MODE=1"   :: 兼容参数可能出现在第一位

echo.
echo 正在分析视频并下载最小体积的文件...
echo.

:: ========== 核心下载命令 ==========
"%ytdlp%" ^
    --cookies "%cookies%" ^
    --no-playlist ^
    -f "worstvideo+worstaudio/worst" ^
    --merge-output-format mp4 ^
    --remux-video mp4 ^
    --extractor-args "youtube:player_client=web" ^
    --js-runtimes "node" ^
    -o "%SCRIPT_DIR%\%%(title)s.%%(ext)s" ^
    "%video_url%"

if errorlevel 1 (
    echo.
    echo 下载失败！请检查链接、网络或 cookies。
    pause
    exit /b
)

echo.
echo ========================================
echo 下载完成，文件已保存。
echo ========================================

:: ========== 根据自动模式决定是否暂停 ==========
if "%AUTO_MODE%"=="1" exit /b

echo 所有操作完成！按任意键退出...
pause >nul
exit /b