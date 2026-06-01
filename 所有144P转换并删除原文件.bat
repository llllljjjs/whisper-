@echo off
title Convert MP4 to 144p (NVIDIA NVENC GPU)

cd /d "%~dp0"

echo =======================================
echo  Batch Convert MP4 to 144p (GPU)
echo =======================================
echo.

:: 查找 ffmpeg
set "ffmpeg=ffmpeg.exe"
if exist "%~dp0ffmpeg.exe" set "ffmpeg=%~dp0ffmpeg.exe"

:: 检查 ffmpeg
"%ffmpeg%" -version >nul 2>nul
if errorlevel 1 (
    echo [ERROR] ffmpeg not found!
    pause
    exit /b
)

:: 检查是否有 MP4 文件
dir /b "*.mp4" 2>nul | findstr . >nul
if errorlevel 1 (
    echo [ERROR] No MP4 files found in current folder: %cd%
    pause
    exit /b
)

:: 处理每个 MP4 文件
for %%f in ("*.mp4") do (
    echo Processing: %%f
    set "tempfile=%%~nf_temp.mp4"
    setlocal enabledelayedexpansion

    "%ffmpeg%" -i "%%f" -vf "scale=-2:144" -c:v h264_nvenc -rc vbr -cq 28 -preset p1 -c:a copy -y "!tempfile!"

    if errorlevel 1 (
        echo [FAIL] Failed to convert %%f
        if exist "!tempfile!" del /f /q "!tempfile!"
    ) else (
        echo [OK] Conversion successful. Deleting original...
        del /f /q "%%f"
        if not errorlevel 1 (
            rename "!tempfile!" "%%~nxf"
            echo [OK] Replaced original with 144p version.
        ) else (
            echo [WARN] Could not delete original, keeping temp file.
        )
    )
    echo.
    endlocal
)

echo =======================================
echo Done. Press any key to exit...
pause >nul
exit /b