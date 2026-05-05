import tkinter as tk


class SettingsView:
    def __init__(self, parent, settings_viewmodel, on_saved=None):
        self.parent = parent
        self.settings_viewmodel = settings_viewmodel
        self.on_saved = on_saved

        self.window = tk.Toplevel(parent)
        self.window.title("设置")
        self.window.geometry("380x250")
        self.window.resizable(False, False)

        self.hide_to_tray_var = tk.BooleanVar()
        self.ask_on_close_var = tk.BooleanVar()

        self.status_text = None

        self.build_ui()
        self.load_settings()

    def build_ui(self) -> None:
        title_label = tk.Label(
            self.window,
            text="设置",
            font=("Microsoft YaHei", 13, "bold")
        )
        title_label.pack(pady=12)

        ask_on_close_check = tk.Checkbutton(
            self.window,
            text="点击关闭按钮时询问",
            variable=self.ask_on_close_var,
            font=("Microsoft YaHei", 10)
        )
        ask_on_close_check.pack(pady=4)

        hide_to_tray_check = tk.Checkbutton(
            self.window,
            text="默认关闭行为：隐藏到托盘",
            variable=self.hide_to_tray_var,
            font=("Microsoft YaHei", 10)
        )
        hide_to_tray_check.pack(pady=4)

        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)

        save_btn = tk.Button(
            button_frame,
            text="保存",
            width=10,
            command=self.save_settings
        )
        save_btn.grid(row=0, column=0, padx=8)

        cancel_btn = tk.Button(
            button_frame,
            text="取消",
            width=10,
            command=self.window.destroy
        )
        cancel_btn.grid(row=0, column=1, padx=8)

        self.status_text = tk.Label(
            self.window,
            text="",
            font=("Microsoft YaHei", 9),
            fg="gray"
        )
        self.status_text.pack()

    def load_settings(self) -> None:
        hide_to_tray = self.settings_viewmodel.get_hide_to_tray()
        ask_on_close = self.settings_viewmodel.get_ask_on_close()

        self.hide_to_tray_var.set(hide_to_tray)
        self.ask_on_close_var.set(ask_on_close)

    def save_settings(self) -> None:
        hide_to_tray = self.hide_to_tray_var.get()
        ask_on_close = self.ask_on_close_var.get()

        success, message = self.settings_viewmodel.save_close_settings(
            hide_to_tray=hide_to_tray,
            ask_on_close=ask_on_close
        )

        self.status_text.config(text=message)

        if success and self.on_saved:
            self.on_saved()