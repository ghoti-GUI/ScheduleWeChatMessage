import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


class FakeLogService:
    def __init__(self):
        self.logs = []

    def write(self, text: str):
        self.logs.append(text)


class FakeConfigService:
    def __init__(self, log_service=None):
        self.log_service = log_service
        self.inited = False

    def init_config(self):
        self.inited = True

    def load_tasks(self):
        return []


class FakeWeChatService:
    def __init__(self, log_service, wechat_hotkey="{Ctrl}{Alt}w"):
        self.log_service = log_service
        self.wechat_hotkey = wechat_hotkey


class FakeSchedulerService:
    def __init__(self, config_service, wechat_service, log_service):
        self.config_service = config_service
        self.wechat_service = wechat_service
        self.log_service = log_service
        self.running = False

    def start_thread(self):
        if self.running:
            return False

        self.running = True
        return True

    def stop_thread(self):
        if not self.running:
            return False

        self.running = False
        return True

    def is_running(self):
        return self.running


class TestMainViewModel(unittest.TestCase):
    def test_viewmodel_start_stop(self):
        import viewmodels.main_viewmodel as viewmodel_module

        with patch.object(viewmodel_module, "LogService", FakeLogService), \
             patch.object(viewmodel_module, "ConfigService", FakeConfigService), \
             patch.object(viewmodel_module, "WeChatService", FakeWeChatService), \
             patch.object(viewmodel_module, "SchedulerService", FakeSchedulerService):

            viewmodel = viewmodel_module.MainViewModel()

            viewmodel.init_app()
            self.assertTrue(viewmodel.config_service.inited)

            success, message = viewmodel.start_scheduler()
            self.assertTrue(success)
            self.assertEqual(message, "运行中")

            success, message = viewmodel.start_scheduler()
            self.assertFalse(success)
            self.assertEqual(message, "已在运行中")

            success, message = viewmodel.stop_scheduler()
            self.assertTrue(success)
            self.assertEqual(message, "已停止")

            success, message = viewmodel.stop_scheduler()
            self.assertFalse(success)
            self.assertEqual(message, "当前未运行")


if __name__ == "__main__":
    unittest.main()