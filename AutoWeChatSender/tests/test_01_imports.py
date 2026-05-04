import sys
import unittest
import importlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_PARENT = PROJECT_ROOT.parent

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_PARENT))


class TestImports(unittest.TestCase):
    def test_import_modules(self):
        modules = [
            "main",
            "models.send_task",
            "services.path_service",
            "services.config_service",
            "services.log_service",
            "services.wechat_service",
            "services.scheduler_service",
            "viewmodels.main_viewmodel",
            "views.main_view",
        ]

        for module_name in modules:
            with self.subTest(module=module_name):
                importlib.import_module(module_name)


if __name__ == "__main__":
    unittest.main()