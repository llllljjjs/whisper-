使用说明
down.bat  #打开后，输入YouTube网址，下载视频



拖视频到这里转文字.bat  #把视频文件拖在这个上面自动转，两个就是一个完事继续下一个。
duandianzhuanhuan.py  #文件夹里面的视频全部转文字，ctrl+c暂停，再按一次继续
duorenzhuanhuan.py  #这个暂时不好用
zhuan_en.py  #转换单个英文视频
zhuanhuanwenjianjia.py  #转换整个文件夹的视频
zhuanwenjianjia_en.py  #转换整个文件夹的英文视频
zhuanwenzi.py  #转换单个视频
  这里面先要安装ffmepg
  安装Python
  安装cuda
  


视频合并命令.txt  #cmd命令，记录一下
一键合并所有大疆的视频.bat  #一键合并当前文件夹的所有视频，以前用的老版本，没有调声音，现在不用了。
  合并大疆视频+平衡声音.bat  #现在用的合并视频+平衡声音，音量-23，比PR快很多很多
    重装系统后不能直接运行
    pip install ffmpeg-normalize
    python -m pip install ffmpeg-normalize
    ffmpeg-normalize --help



所有144P转换并删除原文件.bat  #把当前文件夹里面所有的视频都转成144p，同时覆盖掉之前视频，为了省地方



yt下载命令.txt  #cmd命令，记录一下
连续下载.py  #这个是下载YouTube视频，输入网址排队，一个下完接着下一个，很好用的。需要yt-dlp.exe，FFmpeg，deno。火狐的cookies下一次一直能用。
  重装系统之后，存在网址贴上去不下载的问题
  打开powershell  到目录下安装    irm https://deno.land/install.ps1 | iex
  安装node.js
  用火狐下载cookies
  之后就可以用了

  py代码不可用继续
  在powershell运行    irm https://deno.land/install.ps1 | iex
  🔍 问题原因总结
你遇到的 错误码1 和 “Sign in to confirm you’re not a bot” 的根本原因，是 yt-dlp 无法通过你提供的 cookies.txt 文件完成身份验证。即使你手动导出了 cookies，但可能因为：

导出格式不是标准的 Netscape 格式（yt-dlp 要求特定格式）。

cookies 文件中的某些关键字段（如 SAPISID、__Secure-3PSID 等）已过期或不完整。

YouTube 对基于文件的 cookies 验证越来越严格，直接读取浏览器实时 cookie 更可靠。

改为 --cookies-from-browser chrome 后，yt-dlp 直接与你的 Chrome 浏览器通信，读取当前登录且实时有效的 cookies，绕过了手动导出可能存在的格式、过期、权限问题，因此下载成功。

补充： 你之前还遇到过 --js-runtimes node 找不到 Node.js 的问题，后来你安装了 Node.js 解决了。但最终能工作主要还是依赖正确的 cookie 认证方式。

🧰 重装系统后快速恢复环境清单
下次重装系统，按以下步骤操作，保证你的 连续下载.py 能直接运行：

1️⃣ 安装 Python（必须）
从 python.org 下载 Python 3.10+（推荐 3.11 或 3.12）。

安装时务必勾选 Add Python to PATH。

安装完成后，打开 命令提示符，运行：

bash
python --version
确认版本正常。

2️⃣ 检查 tkinter（Python GUI 库）
默认安装通常自带。测试：

bash
python -m tkinter
应弹出一个简单窗口。若提示缺少，则重新运行 Python 安装程序，勾选 tcl/tk and IDLE。

3️⃣ 安装 yt-dlp.exe
从 yt-dlp GitHub Releases 下载 yt-dlp.exe。

放到你的工作目录（例如 D:\yt），与脚本同级。

4️⃣ 安装 FFmpeg（必须，用于处理视频格式）
从 gyan.dev 下载 ffmpeg-release-full.7z 或直接下载 ffmpeg.exe。

解压或单独将 ffmpeg.exe 放到工作目录（与 yt-dlp.exe 同目录）。

5️⃣ 安装 JavaScript 运行时（推荐，解决 YouTube 反爬）
安装 Node.js：从 nodejs.org 下载 LTS 版本，安装后验证 node --version。

或安装 Deno（更轻量，兼容性好）：从 deno.com 安装，验证 deno --version。

yt-dlp 会自动检测并使用已安装的运行时。

6️⃣ 浏览器与 Cookie 认证（核心）
使用 Chrome 或 Firefox 浏览器，登录你的 Google 账号，确保能在浏览器中正常观看 YouTube。

不需要导出 cookies.txt，只需在脚本中使用参数 --cookies-from-browser chrome（或 firefox）。

重要：如果使用 Chrome，下载前需要 完全关闭所有 Chrome 窗口（包括后台进程），否则 yt-dlp 无法读取 cookie 数据库。

7️⃣ 确认工作目录结构
你的 D:\yt 目录下应至少包含：

text
D:\yt\
  连续下载.py       （你的主程序）
  yt-dlp.exe
  ffmpeg.exe
  cookies.txt       （可选，如果改用浏览器直读则不需要）
可选：deno.exe 或 Node.js（已系统级安装，无需放在目录）。

8️⃣ 修改脚本中的认证方式
在你的 连续下载.py 中，将下载命令部分的 --cookies cookies.txt 改为 --cookies-from-browser chrome（建议永久使用此方式）。

示例：

python
cmd = [
    YTDLP,
    "--cookies-from-browser", "chrome",   # 直接读浏览器
    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    ...
]
9️⃣ 测试环境
重装后，先手动在命令行测试 yt-dlp：

bash
cd /d D:\yt
yt-dlp.exe --cookies-from-browser chrome -f bestvideo+bestaudio/best "https://www.youtube.com/watch?v=测试视频ID"
成功后再运行 Python 脚本。

📦 可选的便携方案（一劳永逸）
你可以把所有依赖（Python 解释器、yt-dlp、ffmpeg）打包成一个便携文件夹，下次重装系统后直接使用，无需再单独安装 Python。

使用 嵌入式 Python（从 python.org 下载 Windows embeddable package），解压到目录。

将 yt-dlp.exe、ffmpeg.exe 放进去。

编写一个 run.bat 批处理，设置 PATH 并启动脚本：

batch
@echo off
set PATH=%~dp0python;%~dp0;%PATH%
python 连续下载.py
这样即使新系统没有安装 Python，也能运行。
