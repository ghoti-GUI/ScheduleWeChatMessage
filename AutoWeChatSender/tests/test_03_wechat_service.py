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


class TestWeChatService(unittest.TestCase):
    def test_same_group_should_not_find_group_again(self):
        from services.wechat_service import WeChatService

        log_service = FakeLogService()
        service = WeChatService(log_service)

        service.cur_group = "文件传输助手"

        with patch.object(service, "open_or_activate_wechat") as mock_open, \
             patch.object(service, "find_group") as mock_find_group, \
             patch.object(service, "send_message") as mock_send_message:

            service.send_wechat_message(
                group_name="文件传输助手",
                message="测试消息",
                image_path=""
            )

            mock_open.assert_called_once()
            mock_find_group.assert_not_called()
            mock_send_message.assert_called_once_with("测试消息", "")

    def test_different_group_should_find_group(self):
        from services.wechat_service import WeChatService

        log_service = FakeLogService()
        service = WeChatService(log_service)

        service.cur_group = "旧群聊"

        with patch.object(service, "open_or_activate_wechat") as mock_open, \
             patch.object(service, "find_group") as mock_find_group, \
             patch.object(service, "send_message") as mock_send_message:

            service.send_wechat_message(
                group_name="文件传输助手",
                message="测试消息",
                image_path=""
            )

            mock_open.assert_called_once()
            mock_find_group.assert_called_once_with("文件传输助手")
            mock_send_message.assert_called_once_with("测试消息", "")

    def test_clear_current_group(self):
        from services.wechat_service import WeChatService

        log_service = FakeLogService()
        service = WeChatService(log_service)

        service.cur_group = "文件传输助手"
        service.clear_current_group()

        self.assertEqual(service.cur_group, "")


if __name__ == "__main__":
    unittest.main()