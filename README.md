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
