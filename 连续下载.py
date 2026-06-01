# cd D:\yt
# python 连续下载.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import threading
import subprocess
import queue
import time
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
YTDLP = os.path.join(BASE_DIR, "yt-dlp.exe")
COOKIES = os.path.join(BASE_DIR, "cookies.txt")
FFMPEG = os.path.join(BASE_DIR, "ffmpeg.exe") if os.path.exists(os.path.join(BASE_DIR, "ffmpeg.exe")) else None

download_queue = []
current_task = None
current_process = None
stop_current = False
completed_tasks = []
lock = threading.Lock()
stop_event = threading.Event()
gui_queue = queue.Queue()

def log_to_gui(msg):
    gui_queue.put(("log", msg))

def update_queue_display():
    gui_queue.put(("refresh", None))

def fetch_video_info(url):
    try:
        cmd = [YTDLP, "--skip-download", "--print", "%(title)s|%(uploader)s", url]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=15)
        if proc.returncode == 0:
            parts = proc.stdout.strip().split("|", 1)
            title = parts[0] if parts else "未知标题"
            uploader = parts[1] if len(parts) > 1 else "未知作者"
            return title, uploader
    except Exception:
        pass
    return url, "YouTube"

def add_video(url):
    url = url.strip()
    if not url:
        return
    threading.Thread(target=_add_with_info, args=(url,), daemon=True).start()

def _add_with_info(url):
    title, uploader = fetch_video_info(url)
    with lock:
        for task in download_queue + ([current_task] if current_task else []) + completed_tasks:
            if task["url"] == url:
                log_to_gui(f"链接已存在: {title}")
                update_queue_display()
                return
        download_queue.append({
            "url": url,
            "title": title,
            "uploader": uploader,
            "progress": 0,
            "status": "等待中"
        })
    log_to_gui(f"已添加: {title}")
    update_queue_display()
    start_if_idle()

def start_if_idle():
    global current_task
    with lock:
        if current_task is None and download_queue:
            first = download_queue.pop(0)
            first["status"] = "下载中"
            current_task = first
            threading.Thread(target=download_worker_thread, daemon=True).start()

def download_worker_thread():
    global current_process, stop_current, current_task
    task = current_task
    if not task:
        return
    log_to_gui(f"开始下载: {task['title']}")
    cmd = [
        YTDLP,
        "--cookies", COOKIES,
        "--no-playlist",
        "-f", "worstvideo+worstaudio/worst",
        "--merge-output-format", "mp4",
        "--remux-video", "mp4",
        "--extractor-args", "youtube:player_client=web",
        "--js-runtimes", "node",
        "-o", os.path.join(BASE_DIR, "%(title)s.%(ext)s"),
        task["url"]
    ]
    try:
        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        for line in iter(current_process.stdout.readline, ''):
            if stop_current:
                current_process.terminate()
                log_to_gui(f"已取消下载: {task['title']}")
                with lock:
                    task["status"] = "等待中"
                    task["progress"] = 0
                    download_queue.insert(0, task)
                    current_task = None
                update_queue_display()
                return
            m = re.search(r'\[download\]\s+(\d+\.?\d*)%', line)
            if m:
                prog = float(m.group(1))
                with lock:
                    task["progress"] = prog
                update_queue_display()
        current_process.wait()
        if current_process.returncode == 0:
            log_to_gui(f"下载完成: {task['title']}")
            with lock:
                task["status"] = "已完成"
                task["progress"] = 100
                task["completed_time"] = datetime.now().strftime("%H:%M:%S")
                completed_tasks.append(task)
                current_task = None
            update_queue_display()
        else:
            log_to_gui(f"下载失败: {task['title']} (错误码 {current_process.returncode})")
            with lock:
                task["status"] = "失败"
                task["progress"] = 0
                download_queue.insert(0, task)
                current_task = None
            update_queue_display()
    except Exception as e:
        log_to_gui(f"异常: {task['title']} - {str(e)}")
        with lock:
            current_task = None
        update_queue_display()
    finally:
        current_process = None
        start_if_idle()

def start_all():
    start_if_idle()

def pause_all():
    global stop_current
    if current_process and current_process.poll() is None:
        stop_current = True
        time.sleep(0.5)
        stop_current = False

def clear_completed():
    with lock:
        completed_tasks.clear()
    update_queue_display()

class ModernDownloader:
    def __init__(self, root):
        self.root = root
        root.title("YouTube 连续下载管理器 · 现代版")
        root.geometry("1100x750")
        root.minsize(900, 600)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", rowheight=60, font=('Segoe UI', 10))
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        style.map("Treeview", background=[('selected', '#3B82F6')])

        self.create_input_area()
        self.create_status_cards()
        self.create_task_table()
        self.create_bottom_area()
        self.poll_gui_queue()
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_input_area(self):
        frame = tk.Frame(self.root, highlightbackground="#22C55E", highlightthickness=2, bd=0, padx=15, pady=15)
        frame.pack(fill=tk.X, padx=10, pady=(10,5))
        tk.Label(frame, text="🔗 新链接", font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        tk.Label(frame, text="输入 YouTube 链接后按回车或点击「添加」", font=('Segoe UI', 9), fg="gray").pack(anchor='w')
        entry_frame = tk.Frame(frame)
        entry_frame.pack(fill=tk.X, pady=(5,0))
        self.url_entry = ttk.Entry(entry_frame, font=('Segoe UI', 11))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.url_entry.bind("<Return>", lambda e: self.add_from_entry())
        add_btn = tk.Button(entry_frame, text="➕ 添加", bg="#22C55E", fg="white", font=('Segoe UI', 10, 'bold'),
                            padx=15, pady=5, command=self.add_from_entry, relief=tk.FLAT)
        add_btn.pack(side=tk.RIGHT, padx=(10,0))

    def add_from_entry(self):
        url = self.url_entry.get()
        if url:
            add_video(url)
            self.url_entry.delete(0, tk.END)

    def create_status_cards(self):
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.X, padx=20, pady=10)
        self.downloading_card = tk.Frame(frame, bg="#3B82F6", relief=tk.RIDGE, bd=0, padx=10, pady=10)
        self.downloading_card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        tk.Label(self.downloading_card, text="📥 当前下载中", font=('Segoe UI', 11, 'bold'), bg="#3B82F6", fg="white").pack(anchor='w')
        self.downloading_count = tk.Label(self.downloading_card, text="0", font=('Segoe UI', 28, 'bold'), bg="#3B82F6", fg="white")
        self.downloading_count.pack(anchor='center', pady=5)
        self.waiting_card = tk.Frame(frame, bg="#F59E0B", relief=tk.RIDGE, bd=0, padx=10, pady=10)
        self.waiting_card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        tk.Label(self.waiting_card, text="⏳ 等待队列", font=('Segoe UI', 11, 'bold'), bg="#F59E0B", fg="white").pack(anchor='w')
        self.waiting_count = tk.Label(self.waiting_card, text="0", font=('Segoe UI', 28, 'bold'), bg="#F59E0B", fg="white")
        self.waiting_count.pack(anchor='center', pady=5)
        self.completed_card = tk.Frame(frame, bg="#22C55E", relief=tk.RIDGE, bd=0, padx=10, pady=10)
        self.completed_card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        tk.Label(self.completed_card, text="✅ 已完成", font=('Segoe UI', 11, 'bold'), bg="#22C55E", fg="white").pack(anchor='w')
        self.completed_count = tk.Label(self.completed_card, text="0", font=('Segoe UI', 28, 'bold'), bg="#22C55E", fg="white")
        self.completed_count.pack(anchor='center', pady=5)

    def create_task_table(self):
        columns = ("status", "title", "uploader", "progress", "url", "time")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=12)
        self.tree.heading("status", text="状态")
        self.tree.heading("title", text="视频标题")
        self.tree.heading("uploader", text="上传者")
        self.tree.heading("progress", text="进度")
        self.tree.heading("url", text="链接")
        self.tree.heading("time", text="完成时间")
        self.tree.column("status", width=80, anchor='center')
        self.tree.column("title", width=350)
        self.tree.column("uploader", width=150)
        self.tree.column("progress", width=120, anchor='center')
        self.tree.column("url", width=300)
        self.tree.column("time", width=100, anchor='center')
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10,0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,10), pady=5)

    def create_bottom_area(self):
        bottom = tk.Frame(self.root)
        bottom.pack(fill=tk.X, padx=10, pady=5)
        btn_frame = tk.Frame(bottom)
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="▶ 全部开始", bg="#3B82F6", fg="white", font=('Segoe UI', 10),
                  command=start_all, padx=15, pady=5, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="⏸ 暂停当前", bg="#F59E0B", fg="white", font=('Segoe UI', 10),
                  command=pause_all, padx=15, pady=5, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑 清空已完成", bg="#EF4444", fg="white", font=('Segoe UI', 10),
                  command=clear_completed, padx=15, pady=5, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        log_frame = tk.LabelFrame(bottom, text="📋 最近操作", font=('Segoe UI', 9))
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10,0))
        self.log_text = tk.Text(log_frame, height=6, font=('Consolas', 9), wrap=tk.WORD, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def update_status_cards(self):
        with lock:
            downloading = 1 if current_task else 0
            waiting = len(download_queue)
            completed = len(completed_tasks)
        self.downloading_count.config(text=str(downloading))
        self.waiting_count.config(text=str(waiting))
        self.completed_count.config(text=str(completed))

    def update_task_table(self):
        tasks = []
        with lock:
            if current_task:
                tasks.append(current_task)
            tasks.extend(download_queue)
            tasks.extend(completed_tasks)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for task in tasks:
            status = task["status"]
            if status == "下载中":
                status_display = "▶ 下载中"
            elif status == "等待中":
                status_display = "⏳ 等待中"
            elif status == "已完成":
                status_display = "✅ 已完成"
            else:
                status_display = "❌ 失败"
            prog = task.get("progress", 0)
            if status == "已完成":
                prog_display = "100% ██████████"
            elif status == "下载中":
                filled = int(prog / 10)
                bar = "█" * filled + "░" * (10 - filled)
                prog_display = f"{prog:.1f}% {bar}"
            else:
                prog_display = "等待中"
            completed_time = task.get("completed_time", "")
            self.tree.insert("", tk.END, values=(
                status_display,
                task["title"],
                task["uploader"],
                prog_display,
                task["url"],
                completed_time
            ))

    def add_log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        if int(self.log_text.index('end-1c').split('.')[0]) > 30:
            self.log_text.delete(1.0, 2.0)

    def poll_gui_queue(self):
        try:
            while True:
                msg_type, data = gui_queue.get_nowait()
                if msg_type == "log":
                    self.add_log(data)
                elif msg_type == "refresh":
                    self.update_status_cards()
                    self.update_task_table()
        except queue.Empty:
            pass
        self.root.after(200, self.poll_gui_queue)

    def on_closing(self):
        if current_process and current_process.poll() is None:
            if messagebox.askyesno("确认", "正在下载，确定退出吗？\n（当前下载将被终止）"):
                global stop_current
                stop_current = True
                time.sleep(0.5)
                stop_event.set()
                self.root.destroy()
        else:
            stop_event.set()
            self.root.destroy()

if __name__ == "__main__":
    if not os.path.exists(YTDLP):
        print(f"错误：找不到 yt-dlp.exe，请放在 {BASE_DIR} 目录下")
        input("按回车退出...")
        sys.exit(1)
    root = tk.Tk()
    app = ModernDownloader(root)
    root.mainloop()