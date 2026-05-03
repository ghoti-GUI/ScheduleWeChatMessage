import os
import time
import json
import pyautogui
import pyperclip
import win32clipboard
import schedule
from pathlib import Path
from datetime import datetime
from pywinauto import Desktop
from pywinauto.controls.uiawrapper import UIAWrapper
from PIL import Image
from io import BytesIO
import threading
import uiautomation as auto
from ctypes import windll
import sys

WECHAT_PATH = r"D:\Program Files\Tencent\Weixin\Weixin.exe"

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

CONFIG_FILE = BASE_DIR / "config.json"
LOG_FILE = BASE_DIR / "send_log.txt"

scheduler_thread = None
stop_event = threading.Event()

# 记录当前聊天对象
CUR_GROUP = "" 

WECHAT_HOTKEY = "{Ctrl}{Alt}w"

def is_wechat_visible():
    win = auto.WindowControl(Depth=1, Name="微信", searchDepth=1)

    if not win.Exists(0, 0):
        return False

    hwnd = win.NativeWindowHandle
    user32 = windll.user32

    return user32.IsWindowVisible(hwnd) and not user32.IsIconic(hwnd)

def open_or_activate_wechat()->UIAWrapper:
    """ 
    通过快捷键打开微信窗口
    """
    win = auto.WindowControl(Depth=1, Name="微信")

    if is_wechat_visible():
        win.SetFocus()
        time.sleep(0.5)
        return win

    auto.SendKeys(WECHAT_HOTKEY)
    time.sleep(1)

    win = auto.WindowControl(Depth=1, Name="微信")

    if not win.Exists(3, 0.5):
        raise ValueError("未能唤起微信，请确认微信已登录，并且显示/隐藏窗口快捷键是 Ctrl+Alt+W")

    win.SetFocus()
    time.sleep(0.5)
    return win



def find_group(group_name):
    """
    从微信搜索中寻找群组。
    """
    if not group_name or not group_name.strip():
        raise ValueError("请输入正确的群组名称")

    group_name = group_name.strip()

    # 进入搜索框搜索
    pyautogui.hotkey("ctrl", "f")
    time.sleep(0.3)
    pyperclip.copy(group_name)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.3)

    # 进入聊天框
    pyautogui.press("enter")
    time.sleep(1)

    # 记录当前聊天对象
    global CUR_GROUP
    CUR_GROUP = group_name

def copy_img_to_clipboard(image_path):
    """
    复制图片到剪贴板
    """

    # 检测图片是否存在
    file_path = str(Path(image_path).resolve())
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"图片不存在：{file_path}")

    print("img = ", file_path)

    # 把图片写入image变量中
    # 用open函数处理后，图像对象的模式都是 RGB
    image = Image.open(file_path)

    # 声明output字节对象
    output = BytesIO()

    # 用BMP (Bitmap) 格式存储
    # 这里是位图，然后用output字节对象来存储
    image.save(output, 'BMP')

    # BMP图片有14字节的header，需要额外去除
    data = output.getvalue()[14:]

    # 关闭
    output.close()

    # DIB: 设备无关位图(device-independent bitmap)，名如其意
    # BMP的图片有时也会以.DIB和.RLE作扩展名
    # 设置好剪贴板的数据格式，再传入对应格式的数据，才能正确向剪贴板写入数据
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(
        win32clipboard.CF_DIB,
        data
    )
    win32clipboard.CloseClipboard()

def send_message(message=None, image_path=None):
    """
    向当前打开的聊天窗口发送文字或图片
    """

    # 发送文字
    if message:
        pyperclip.copy(message)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)
        pyautogui.press("enter")
        time.sleep(1)

    # 发送图片
    if image_path:
        copy_img_to_clipboard(image_path)
        time.sleep(1)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(1)

def send_wechat_message(group_name, message=None, image_path=None):
    # 打开微信
    main_window = open_or_activate_wechat()

    # 寻找并打开群聊
    print("CUR_GROUP = ", CUR_GROUP, " group_name = ", group_name)
    if CUR_GROUP != group_name:
        find_group(group_name)
        print("2-CUR_GROUP = ", CUR_GROUP, " group_name = ", group_name)

    # 发送消息
    send_message(message, image_path)
    write_log(f"消息已发送至{{group_name}}， 消息内容：{message}，图片：{image_path}")

def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def write_log(text: str) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now}] {text}\n")

def run_task(task: dict):
    if not task.get("enabled", True):
        return

    group_name = task.get("group_name")
    message = task.get("message")
    image_path = task.get("image_path")

    try:
        send_wechat_message(
            group_name=group_name,
            message=message,
            image_path=image_path
        )

        write_log(f"发送成功：{group_name}")

    except Exception as e:
        write_log(f"发送失败：{group_name}，原因：{e}")

def run_task_batch(tasks: list):
    """
    执行同一时间点的一批任务。
    执行过程中复用 CUR_GROUP，全部执行完后再清空。
    """
    global CUR_GROUP

    try:
        for task in tasks:
            run_task(task)
    finally:
        CUR_GROUP = ""
        write_log("当前聊天对象已清空")

def register_weekly_tasks() -> None:
    config = load_config()
    tasks = config.get("tasks", [])

    grouped_tasks = {}

    for task in tasks:
        if not task.get("enabled", True):
            continue

        weekday = task.get("weekday")
        send_time = task.get("time")

        if not weekday or not send_time:
            continue
        

        weekday = str(weekday).lower()

        if weekday in ["monday", "1"]:
            weekday = "monday"
        elif weekday in ["tuesday", "2"]:
            weekday = "tuesday"
        elif weekday in ["wednesday", "3"]:
            weekday = "wednesday"
        elif weekday in ["thursday", "4"]:
            weekday = "thursday"
        elif weekday in ["friday", "5"]:
            weekday = "friday"
        elif weekday in ["saturday", "6"]:
            weekday = "saturday"
        elif weekday in ["sunday", "7"]:
            weekday = "sunday"
        else:
            write_log(f"无效星期配置：{weekday}")

        key = (weekday, send_time)
        grouped_tasks.setdefault(key, []).append(task)

    for (weekday, send_time), task_list in grouped_tasks.items():

        job = lambda ts=task_list: run_task_batch(ts)

        if weekday in ["monday", "1"]:
            schedule.every().monday.at(send_time).do(job)
        elif weekday in ["tuesday", "2"]:
            schedule.every().tuesday.at(send_time).do(job)
        elif weekday in ["wednesday", "3"]:
            schedule.every().wednesday.at(send_time).do(job)
        elif weekday in ["thursday", "4"]:
            schedule.every().thursday.at(send_time).do(job)
        elif weekday in ["friday", "5"]:
            schedule.every().friday.at(send_time).do(job)
        elif weekday in ["saturday", "6"]:
            schedule.every().saturday.at(send_time).do(job)
        elif weekday in ["sunday", "7"]:
            schedule.every().sunday.at(send_time).do(job)
        else:
            write_log(f"无效星期配置：{weekday}")

        write_log(f"已注册任务：{weekday} {send_time}，发送对象：{task.get('group_name')}，发送内容：{task.get('message')}，图片：{task.get('image_path')}")

def start_scheduler():
    global CUR_GROUP

    schedule.clear()
    register_weekly_tasks()

    write_log("定时发送程序已启动")

    while not stop_event.is_set():
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            write_log(f"定时器运行异常：{e}")
            time.sleep(1)

    schedule.clear()
    CUR_GROUP = ""
    write_log("定时发送程序已停止")

def start_scheduler_thread():
    global scheduler_thread

    if scheduler_thread and scheduler_thread.is_alive():
        return False

    stop_event.clear()

    scheduler_thread = threading.Thread(
        target=start_scheduler,
        daemon=True
    )
    scheduler_thread.start()

    return True


def stop_scheduler_thread():
    if not scheduler_thread or not scheduler_thread.is_alive():
        return False

    stop_event.set()
    return True

if __name__ == "__main__":
    start_scheduler()
    # open_or_activate_wechat()