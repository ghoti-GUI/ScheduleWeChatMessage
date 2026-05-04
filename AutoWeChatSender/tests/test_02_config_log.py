import tempfile
import unittest
from pathlib import Path


class TestConfigAndLog(unittest.TestCase):
    def test_config_service_create_and_load_config(self):
        from services.path_service import PathService
        from services.config_service import ConfigService

        original_base_dir = PathService.base_dir

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                PathService.base_dir = classmethod(lambda cls: temp_path)

                service = ConfigService()
                service.init_config()

                config_file = PathService.config_file()

                print("测试配置文件路径：", config_file)

                self.assertTrue(config_file.exists())

                config = service.load_config()

                self.assertIsInstance(config, dict)
                self.assertIn("tasks", config)
                self.assertIsInstance(config["tasks"], list)

            finally:
                PathService.base_dir = original_base_dir

    def test_log_service_write_log(self):
        from services.path_service import PathService
        from services.log_service import LogService

        original_base_dir = PathService.base_dir

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                PathService.base_dir = classmethod(lambda cls: temp_path)

                service = LogService()
                service.write("测试日志")

                log_file = PathService.log_file()

                print("测试日志文件路径：", log_file)

                self.assertTrue(log_file.exists())

                content = log_file.read_text(encoding="utf-8")
                self.assertIn("测试日志", content)

            finally:
                PathService.base_dir = original_base_dir


if __name__ == "__main__":
    unittest.main()