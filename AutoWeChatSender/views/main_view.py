import threading
import tkinter as tk
import pystray
from PIL import Image, ImageDraw

from viewmodels.main_viewmodel import MainViewModel
from views.close_confirm_dialog import CloseConfirmDialog
from views.settings_view import SettingsView


class MainView:
    """
    View：
    只负责界面展示、按钮事件、托盘；
    不直接处理微信、配置、日志、定时器细节。
    """

    def __init__(self, viewmodel: MainViewModel):
        self.viewmodel = viewmodel
        self.root = tk.Tk()
        self.tray_icon = None

        self.status_dot = None
        self.status_text = None

        self.init_window()
        self.setup_tray()
        self.build_ui()

    def init_window(self) -> None:
        self.root.title("微信定时发送工具")
        self.root.geometry("360x250")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_button_click)

    def build_ui(self) -> None:
        title_label = tk.Label(
            self.root,
            text="微信定时发送工具",
            font=("Microsoft YaHei", 14, "bold")
        )
        title_label.pack(pady=15)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        start_btn = tk.Button(
            button_frame,
            text="启动定时发送",
            width=14,
            height=2,
            command=self.start_button_click
        )
        start_btn.grid(row=0, column=0, padx=8)

        stop_btn = tk.Button(
            button_frame,
            text="停止定时发送",
            width=14,
            height=2,
            command=self.stop_button_click
        )
        stop_btn.grid(row=0, column=1, padx=8)

        settings_btn = tk.Button(
            self.root,
            text="设置",
            width=12,
            command=self.open_settings_window
        )
        settings_btn.pack(pady=4)

        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=10)

        self.status_dot = tk.Label(
            status_frame,
            text="●",
            fg="red",
            font=("Arial", 18)
        )
        self.status_dot.pack(side="left", padx=5)

        self.status_text = tk.Label(
            status_frame,
            text="已停止",
            font=("Microsoft YaHei", 10)
        )
        self.status_text.pack(side="left")

    def set_status_running(self) -> None:
        self.status_dot.config(fg="green")
        self.status_text.config(text="运行中")

    def set_status_stopped(self) -> None:
        self.status_dot.config(fg="red")
        self.status_text.config(text="已停止")

    def set_status_info(self, text: str) -> None:
        self.status_text.config(text=text)

    def start_button_click(self) -> None:
        success, message = self.viewmodel.start_scheduler()

        if success:
            self.set_status_running()
        else:
            self.set_status_info(message)

    def stop_button_click(self) -> None:
        success, message = self.viewmodel.stop_scheduler()

        if success:
            self.set_status_stopped()
        else:
            self.set_status_info(message)

    def create_tray_image(self):
        image = Image.new("RGB", (64, 64), "white")
        draw = ImageDraw.Draw(image)
        draw.ellipse((12, 12, 52, 52), fill="green")
        return image

    def show_window(self, icon=None, item=None) -> None:
        self.root.after(0, self.root.deiconify)

    def quit_app(self, icon=None, item=None) -> None:
        self.viewmodel.quit_app()

        if self.tray_icon:
            self.tray_icon.stop()

        self.root.after(0, self.root.destroy)

    def hide_to_tray(self) -> None:
        self.root.withdraw()

    def on_close_button_click(self) -> None:
        ask_on_close = self.viewmodel.get_ask_on_close()

        if not ask_on_close:
            hide_to_tray = self.viewmodel.get_hide_to_tray()

            if hide_to_tray:
                self.hide_to_tray()
            else:
                self.quit_app()

            return

        dialog = CloseConfirmDialog(self.root)
        result = dialog.show()

        if not result:
            return

        action = result.get("action")
        do_not_ask_again = result.get("do_not_ask_again", False)

        if action == "cancel":
            return

        if action == "hide_to_tray":
            if do_not_ask_again:
                self.viewmodel.save_close_settings(
                    hide_to_tray=True,
                    ask_on_close=False
                )

            self.hide_to_tray()
            return

        if action == "exit_app":
            if do_not_ask_again:
                self.viewmodel.save_close_settings(
                    hide_to_tray=False,
                    ask_on_close=False
                )

            self.quit_app()
            return
        
    def open_settings_window(self) -> None:
        SettingsView(
            parent=self.root,
            settings_viewmodel=self.viewmodel.settings_viewmodel,
            on_saved=self.refresh_settings
        )

    def refresh_settings(self) -> None:
        # self.set_status_info("设置已更新")
        return

    def setup_tray(self) -> None:
        menu = pystray.Menu(
            pystray.MenuItem("显示窗口", self.show_window),
            pystray.MenuItem("退出程序", self.quit_app), 
            pystray.MenuItem("编辑消息", None) # todo: 增加从托盘标签进入消息编辑页面
        )

        self.tray_icon = pystray.Icon(
            "AutoWeChatSender",
            self.create_tray_image(),
            "微信定时发送工具",
            menu
        )

        threading.Thread(
            target=self.tray_icon.run,
            daemon=True
        ).start()

    def run(self) -> None:
        self.root.mainloop()
