@echo off
chcp 65001 >nul
cd /d C:\
echo 正在生成视频列表 list.txt...
(for %%i in (DJI_*.MP4) do @echo file '%%i') > list.txt
echo 正在合并视频，请稍候...
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4 -y
if exist output.mp4 (
    echo 合并完成！文件已保存为 C:\output.mp4
) else (
    echo 合并失败，请检查视频文件或FFmpeg是否安装。
)
pause