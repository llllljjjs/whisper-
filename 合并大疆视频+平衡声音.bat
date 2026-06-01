#安装Python  然后运行： pip install ffmpeg-normalize

@echo off
chcp 65001 > nul
echo 正在处理视频，请稍等...

:: 第一步：用 ffmpeg-normalize 对每个视频进行统一的响度标准化，目标是 -16 LUFS
for %%i in (DJI_*.MP4) do (
    echo 正在标准化：%%i
    ffmpeg-normalize "%%i" -nt ebur128 -t -23 -c:a aac -b:a 192k -ext mp4 -of normalised_temp
)

:: 第二步：进入标准化后的文件夹，生成合并列表
cd normalised_temp
(for %%i in (*.mp4) do @echo file '%%i') > list.txt

:: 第三步：用 concat demuxer 快速无损合并
ffmpeg -f concat -safe 0 -i list.txt -c copy "..\output_normalized.mp4"
cd ..

echo 完成！合并好的视频名为 output_normalized.mp4
pause