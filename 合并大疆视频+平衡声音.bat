@echo off
chcp 65001 > nul
echo 正在处理视频（目标 -12 LUFS，音量接近 PR 导出效果），请稍等...

:: 清理旧的临时文件夹（重新开始）
if exist normalized_temp rmdir /s /q normalized_temp
mkdir normalized_temp

:: 第一步：对每个 DJI 视频进行响度标准化（目标 -12 LUFS，真峰值 -1 dBTP）
for %%i in (DJI_*.MP4) do (
    echo 正在标准化：%%i
    ffmpeg-normalize "%%i" -nt ebu -t -12 -tp -1 -c:a aac -b:a 192k -ext mp4 -of normalized_temp
)

:: 第二步：生成合并列表（指向 normalized_temp 里的文件）
cd normalized_temp
(for %%i in (DJI_*.MP4) do @echo file '%%i') > list.txt

:: 第三步：合并视频
ffmpeg -f concat -safe 0 -i list.txt -c copy "..\output_loud.mp4"
cd ..

:: 将 list.txt 复制到当前目录（保留记录）
copy normalized_temp\list.txt list.txt >nul

:: 删除缓存文件夹（不再保留标准化后的单独视频）
rmdir /s /q normalized_temp

echo 完成！
echo 合并好的视频：output_loud.mp4
echo 处理过的视频列表：list.txt（已保存在当前目录）
pause