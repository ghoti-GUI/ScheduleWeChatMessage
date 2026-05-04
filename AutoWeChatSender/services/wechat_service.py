import os
import time
from ctypes import windll
from io import BytesIO
from pathlib import Path

import pyautogui
import pyperclip
import uiautomation as auto
import win32clipboard
from PIL import Image


class WeChatService:
    """
    负责微信窗口唤起、群聊搜索、文字/图片发送。

    注意：
    - 不使用 subprocess.Popen 启动微信；
    - 通过微信“显示/隐藏窗口”快捷键唤起窗口；
    - 默认快捷键为 Ctrl + Alt + W。
    """

    def __init__(self, log_service, wechat_hotkey: str = "{Ctrl}{Alt}w"):
        self.log_service = log_service
        self.wechat_hotkey = wechat_hotkey
        self.cur_group = ""

    def is_wechat_visible(self) -> bool:
        win = auto.WindowControl(Depth=1, Name="微信", searchDepth=1)

        if not win.Exists(0, 0):
            return False

        hwnd = win.NativeWindowHandle
        user32 = windll.user32

        return user32.IsWindowVisible(hwnd) and not user32.IsIconic(hwnd)

    def open_or_activate_wechat(self):
        win = auto.WindowControl(Depth=1, Name="微信")

        if self.is_wechat_visible():
            win.SetFocus()
            time.sleep(0.5)
            return win

        auto.SendKeys(self.wechat_hotkey)
        time.sleep(1)

        win = auto.WindowControl(Depth=1, Name="微信")

        if not win.Exists(3, 0.5):
            raise ValueError("未能唤起微信，请确认微信已登录，并且显示/隐藏窗口快捷键是 Ctrl+Alt+W")

        win.SetFocus()
        time.sleep(0.5)
        return win

    def find_group(self, group_name: str) -> None:
        if not group_name or not group_name.strip():
            raise ValueError("请输入正确的群组名称")

        group_name = group_name.strip()

        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.3)

        pyperclip.copy(group_name)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)

        pyautogui.press("enter")
        time.sleep(1)

        self.cur_group = group_name

    def copy_img_to_clipboard(self, image_path: str) -> None:
        file_path = str(Path(image_path).resolve())

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"图片不存在：{file_path}")

        image = Image.open(file_path)
        output = BytesIO()

        image.save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

    def send_message(self, message: str = "", image_path: str = "") -> None:
        if message:
            pyperclip.copy(message)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.5)
            pyautogui.press("enter")
            time.sleep(1)

        if image_path:
            self.copy_img_to_clipboard(image_path)
            time.sleep(1)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(1)
            pyautogui.press("enter")
            time.sleep(1)

    def send_wechat_message(self, group_name: str, message: str = "", image_path: str = "") -> None:
        self.open_or_activate_wechat()

        if self.cur_group != group_name:
            self.find_group(group_name)

        self.send_message(message, image_path)

        self.log_service.write(
            f"消息已发送至 {group_name}，消息内容：{message}，图片：{image_path}"
        )

    def clear_current_group(self) -> None:
        self.cur_group = ""
