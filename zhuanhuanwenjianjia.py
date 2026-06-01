#  python zhuanhuanwenjianjia.py "D:\yt"

import os
import sys
import subprocess
import traceback

# 支持的视频格式
VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".flv",
    ".wmv",
    ".m4v",
    ".ts",
    ".webm"
}


def find_video_files(folder_path):
    """只查找当前文件夹里的视频文件，不递归子文件夹"""

    video_files = []

    for file in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file)

        # 跳过子文件夹
        if not os.path.isfile(full_path):
            continue

        ext = os.path.splitext(file)[1].lower()

        if ext in VIDEO_EXTENSIONS:
            video_files.append(full_path)

    return sorted(video_files)


def main():
    if len(sys.argv) < 2:
        print("用法：")
        print('python zhuanhuanwenjianjia.py "D:\\yt"')
        sys.exit(1)

    folder_path = sys.argv[1]

    if not os.path.exists(folder_path):
        print(f"❌ 文件夹不存在: {folder_path}")
        sys.exit(1)

    if not os.path.isdir(folder_path):
        print(f"❌ 这不是文件夹: {folder_path}")
        sys.exit(1)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    zhuanwenzi_path = os.path.join(current_dir, "zhuanwenzi.py")

    if not os.path.exists(zhuanwenzi_path):
        print(f"❌ 找不到 zhuanwenzi.py : {zhuanwenzi_path}")
        sys.exit(1)

    print(f"📂 正在扫描文件夹: {folder_path}")

    video_files = find_video_files(folder_path)

    if not video_files:
        print("❌ 没找到视频文件")
        sys.exit(1)

    print(f"🎬 共找到 {len(video_files)} 个视频文件")
    print()

    success_count = 0
    fail_count = 0

    for index, video_file in enumerate(video_files, start=1):
        print("=" * 80)
        print(f"🎯 [{index}/{len(video_files)}]")
        print(f"📹 文件: {video_file}")
        print("=" * 80)

        try:
            cmd = [
                sys.executable,
                zhuanwenzi_path,
                video_file
            ]

            result = subprocess.run(cmd)

            if result.returncode == 0:
                success_count += 1
                print("✅ 转写成功")
            else:
                fail_count += 1
                print("❌ 转写失败")

        except Exception:
            fail_count += 1
            print("❌ 运行异常：")
            traceback.print_exc()

        print()

    print("=" * 80)
    print("🎉 全部任务完成")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {fail_count}")
    print("=" * 80)


if __name__ == "__main__":
    main()