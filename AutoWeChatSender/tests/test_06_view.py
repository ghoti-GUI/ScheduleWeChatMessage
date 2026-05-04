import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_PARENT = PROJECT_ROOT.parent

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_PARENT))


class FakeViewModel:
    def __init__(self):
        self.running = False
        self.quit_called = False

    def start_scheduler(self):
        if self.running:
            return False, "已在运行中"

        self.running = True
        return True, "运行中"

    def stop_scheduler(self):
        if not self.running:
            return False, "当前未运行"

        self.running = False
        return True, "已停止"

    def quit_app(self):
        self.quit_called = True
        self.running = False


class FakeTrayIcon:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.stopped = False

    def run(self):
        pass

    def stop(self):
        self.stopped = True


class TestMainView(unittest.TestCase):
    def test_create_main_view_and_click_buttons(self):
        import views.main_view as view_module

        with patch.object(view_module.pystray, "Icon", FakeTrayIcon):
            view = view_module.MainView(FakeViewModel())

            self.assertIsNotNone(view.root)
            self.assertIsNotNone(view.status_dot)
            self.assertIsNotNone(view.status_text)

            view.start_button_click()
            self.assertEqual(view.status_text.cget("text"), "运行中")
            self.assertEqual(view.status_dot.cget("fg"), "green")

            view.stop_button_click()
            self.assertEqual(view.status_text.cget("text"), "已停止")
            self.assertEqual(view.status_dot.cget("fg"), "red")

            view.root.destroy()


if __name__ == "__main__":
    unittest.main()