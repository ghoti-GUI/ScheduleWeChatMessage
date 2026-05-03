import tkinter as tk
from tkinter import messagebox
import threading
from PIL import Image, ImageDraw
import pystray

from autoSendMessage import start_scheduler_thread, stop_scheduler_thread



tray_icon = None


def create_tray_image():
    image = Image.new("RGB", (64, 64), "white")
    draw = ImageDraw.Draw(image)
    draw.ellipse((12, 12, 52, 52), fill="green")
    return image


def show_window(icon=None, item=None):
    root.after(0, root.deiconify)


def quit_app(icon=None, item=None):
    global tray_icon

    stop_scheduler_thread()

    if tray_icon:
        tray_icon.stop()

    root.after(0, root.destroy)


def hide_to_tray():
    root.withdraw()

def setup_tray():
    global tray_icon

    menu = pystray.Menu(
        pystray.MenuItem("显示窗口", show_window),
        pystray.MenuItem("退出程序", quit_app)
    )

    tray_icon = pystray.Icon(
        "WeChatSender",
        create_tray_image(),
        "微信定时发送工具",
        menu
    )

    threading.Thread(
        target=tray_icon.run,
        daemon=True
    ).start()

def set_status_running():
    status_dot.config(fg="green")
    status_text.config(text="运行中")


def set_status_stopped():
    status_dot.config(fg="red")
    status_text.config(text="已停止")


def start_button_click():
    started = start_scheduler_thread()

    if started:
        set_status_running()
    else:
        messagebox.showinfo("提示", "定时发送已经在运行中")


def stop_button_click():
    stopped = stop_scheduler_thread()

    if stopped:
        set_status_stopped()
    else:
        messagebox.showinfo("提示", "定时发送当前未运行")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("微信定时发送工具")
    root.geometry("360x180")
    root.resizable(False, False)

    root.protocol("WM_DELETE_WINDOW", hide_to_tray)
    setup_tray()

    title_label = tk.Label(
        root,
        text="微信定时发送工具",
        font=("Microsoft YaHei", 14, "bold")
    )
    title_label.pack(pady=15)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    start_btn = tk.Button(
        button_frame,
        text="启动定时发送",
        width=14,
        height=2,
        command=start_button_click
    )
    start_btn.grid(row=0, column=0, padx=8)

    stop_btn = tk.Button(
        button_frame,
        text="停止定时发送",
        width=14,
        height=2,
        command=stop_button_click
    )
    stop_btn.grid(row=0, column=1, padx=8)

    status_frame = tk.Frame(root)
    status_frame.pack(pady=10)

    status_dot = tk.Label(
        status_frame,
        text="●",
        fg="red",
        font=("Arial", 18)
    )
    status_dot.pack(side="left", padx=5)

    status_text = tk.Label(
        status_frame,
        text="已停止",
        font=("Microsoft YaHei", 10)
    )
    status_text.pack(side="left")

    root.mainloop()