import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


class FakeConfigService:
    def load_tasks(self):
        from models.send_task import SendTask

        return [
            SendTask(
                comment="测试1",
                group_name="文件传输助手",
                message="测试消息1",
                image_path="",
                weekday="周日",
                time="18:00",
                enabled=True,
            ),
            SendTask(
                comment="测试2",
                group_name="文件传输助手",
                message="测试消息2",
                image_path="",
                weekday="7",
                time="18:00",
                enabled=True,
            ),
        ]


class FakeWeChatService:
    def __init__(self):
        self.sent = []
        self.cleared = False

    def send_wechat_message(self, group_name, message="", image_path=""):
        self.sent.append({
            "group_name": group_name,
            "message": message,
            "image_path": image_path,
        })

    def clear_current_group(self):
        self.cleared = True


class FakeLogService:
    def __init__(self):
        self.logs = []

    def write(self, text: str):
        self.logs.append(text)


class TestSchedulerService(unittest.TestCase):
    def test_normalize_weekday(self):
        from services.scheduler_service import SchedulerService

        scheduler_service = SchedulerService(
            config_service=FakeConfigService(),
            wechat_service=FakeWeChatService(),
            log_service=FakeLogService()
        )

        self.assertEqual(scheduler_service.normalize_weekday("monday"), "monday")
        self.assertEqual(scheduler_service.normalize_weekday("1"), "monday")
        self.assertEqual(scheduler_service.normalize_weekday("周一"), "monday")
        self.assertEqual(scheduler_service.normalize_weekday("星期日"), "sunday")
        self.assertEqual(scheduler_service.normalize_weekday(7), "sunday")
        self.assertIsNone(scheduler_service.normalize_weekday("错误星期"))

    def test_run_task_batch(self):
        from services.scheduler_service import SchedulerService

        wechat_service = FakeWeChatService()

        scheduler_service = SchedulerService(
            config_service=FakeConfigService(),
            wechat_service=wechat_service,
            log_service=FakeLogService()
        )

        tasks = FakeConfigService().load_tasks()
        scheduler_service.run_task_batch(tasks)

        self.assertEqual(len(wechat_service.sent), 2)
        self.assertTrue(wechat_service.cleared)

    def test_register_weekly_tasks(self):
        import schedule
        from services.scheduler_service import SchedulerService

        schedule.clear()

        scheduler_service = SchedulerService(
            config_service=FakeConfigService(),
            wechat_service=FakeWeChatService(),
            log_service=FakeLogService()
        )

        scheduler_service.register_weekly_tasks()

        self.assertGreaterEqual(len(schedule.jobs), 1)

        schedule.clear()


if __name__ == "__main__":
    unittest.main()