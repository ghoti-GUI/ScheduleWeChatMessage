import tkinter as tk


class CloseConfirmDialog:
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.do_not_ask_again_var = tk.BooleanVar(value=False)

        self.window = tk.Toplevel(parent)
        self.window.title("关闭确认")
        self.window.geometry("380x180")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()

        self.build_ui()
        self.center_window()

        self.window.protocol("WM_DELETE_WINDOW", self.cancel)

    def build_ui(self) -> None:
        message_label = tk.Label(
            self.window,
            text="你希望如何处理当前窗口？",
            font=("Microsoft YaHei", 11)
        )
        message_label.pack(pady=18)

        checkbox = tk.Checkbutton(
            self.window,
            text="以后不再询问，记住本次选择",
            variable=self.do_not_ask_again_var,
            font=("Microsoft YaHei", 9)
        )
        checkbox.pack(pady=4)

        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=14)

        hide_btn = tk.Button(
            button_frame,
            text="隐藏到托盘",
            width=12,
            command=self.choose_hide_to_tray
        )
        hide_btn.grid(row=0, column=0, padx=6)

        exit_btn = tk.Button(
            button_frame,
            text="退出程序",
            width=12,
            command=self.choose_exit_app
        )
        exit_btn.grid(row=0, column=1, padx=6)

        cancel_btn = tk.Button(
            button_frame,
            text="取消",
            width=8,
            command=self.cancel
        )
        cancel_btn.grid(row=0, column=2, padx=6)

    def center_window(self) -> None:
        self.window.update_idletasks()

        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()

        window_w = self.window.winfo_width()
        window_h = self.window.winfo_height()

        x = parent_x + (parent_w - window_w) // 2
        y = parent_y + (parent_h - window_h) // 2

        self.window.geometry(f"+{x}+{y}")

    def choose_hide_to_tray(self) -> None:
        self.result = {
            "action": "hide_to_tray",
            "do_not_ask_again": self.do_not_ask_again_var.get()
        }
        self.window.destroy()

    def choose_exit_app(self) -> None:
        self.result = {
            "action": "exit_app",
            "do_not_ask_again": self.do_not_ask_again_var.get()
        }
        self.window.destroy()

    def cancel(self) -> None:
        self.result = {
            "action": "cancel",
            "do_not_ask_again": False
        }
        self.window.destroy()

    def show(self):
        self.parent.wait_window(self.window)
        return self.result