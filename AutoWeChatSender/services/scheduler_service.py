import threading
import time

import schedule

from models.send_task import SendTask


class SchedulerService:
    """
    负责定时任务注册、启动、停止。

    同一 weekday + time 的任务会合并成一个批次执行；
    批次内复用 WeChatService.cur_group；
    批次结束后统一清空当前聊天对象。
    """

    def __init__(self, config_service, wechat_service, log_service):
        self.config_service = config_service
        self.wechat_service = wechat_service
        self.log_service = log_service

        self.scheduler_thread = None
        self.stop_event = threading.Event()

    def normalize_weekday(self, weekday) -> str | None:
        weekday = str(weekday).strip().lower()

        mapping = {
            "monday": "monday", "1": "monday", "周一": "monday", "星期一": "monday",
            "tuesday": "tuesday", "2": "tuesday", "周二": "tuesday", "星期二": "tuesday",
            "wednesday": "wednesday", "3": "wednesday", "周三": "wednesday", "星期三": "wednesday",
            "thursday": "thursday", "4": "thursday", "周四": "thursday", "星期四": "thursday",
            "friday": "friday", "5": "friday", "周五": "friday", "星期五": "friday",
            "saturday": "saturday", "6": "saturday", "周六": "saturday", "星期六": "saturday",
            "sunday": "sunday", "7": "sunday", "周日": "sunday", "星期日": "sunday",
            "周天": "sunday", "星期天": "sunday",
        }

        return mapping.get(weekday)

    def run_task(self, task: SendTask) -> None:
        if not task.enabled:
            return

        try:
            self.wechat_service.send_wechat_message(
                group_name=task.group_name,
                message=task.message,
                image_path=task.image_path
            )
            self.log_service.write(f"发送成功：{task.group_name}")

        except Exception as e:
            self.log_service.write(f"发送失败：{task.group_name}，原因：{e}")

    def run_task_batch(self, tasks: list[SendTask]) -> None:
        try:
            for task in tasks:
                self.run_task(task)
        finally:
            self.wechat_service.clear_current_group()
            self.log_service.write("当前聊天对象已清空")

    def register_weekly_tasks(self) -> None:
        tasks = self.config_service.load_tasks()
        grouped_tasks: dict[tuple[str, str], list[SendTask]] = {}

        for task in tasks:
            if not task.enabled:
                continue

            weekday = self.normalize_weekday(task.weekday)
            send_time = task.time

            if not weekday or not send_time:
                self.log_service.write(f"无效任务配置：{task}")
                continue

            key = (weekday, send_time)
            grouped_tasks.setdefault(key, []).append(task)

        for (weekday, send_time), task_list in grouped_tasks.items():
            job = lambda ts=task_list: self.run_task_batch(ts)

            getattr(schedule.every(), weekday).at(send_time).do(job)

            self.log_service.write(
                f"已注册任务：{weekday} {send_time}，共 {len(task_list)} 个任务"
            )

    def start(self) -> None:
        schedule.clear()
        self.register_weekly_tasks()

        self.log_service.write("定时发送程序已启动")

        while not self.stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.log_service.write(f"定时器运行异常：{e}")
                time.sleep(1)

        schedule.clear()
        self.wechat_service.clear_current_group()
        self.log_service.write("定时发送程序已停止")

    def start_thread(self) -> bool:
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            return False

        self.stop_event.clear()

        self.scheduler_thread = threading.Thread(
            target=self.start,
            daemon=True
        )
        self.scheduler_thread.start()

        return True

    def stop_thread(self) -> bool:
        if not self.scheduler_thread or not self.scheduler_thread.is_alive():
            return False

        self.stop_event.set()
        return True

    def is_running(self) -> bool:
        return self.scheduler_thread is not None and self.scheduler_thread.is_alive()
