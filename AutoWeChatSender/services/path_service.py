import sys
from pathlib import Path


class PathService:
    """
    统一管理运行时路径。

    开发环境：
        项目根目录/data/config.json
        项目根目录/log/send_log.txt

    PyInstaller 打包后：
        exe 所在目录/data/config.json
        exe 所在目录/log/send_log.txt
    """

    @staticmethod
    def base_dir() -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).parent
        return Path(__file__).resolve().parent.parent

    @classmethod
    def data_dir(cls) -> Path:
        return cls.base_dir() / "data"

    @classmethod
    def log_dir(cls) -> Path:
        return cls.base_dir() / "log"

    @classmethod
    def config_file(cls) -> Path:
        return cls.data_dir() / "config.json"

    @classmethod
    def log_file(cls) -> Path:
        return cls.log_dir() / "send_log.txt"

    @classmethod
    def init_runtime_files(cls) -> None:
        cls.data_dir().mkdir(parents=True, exist_ok=True)
        cls.log_dir().mkdir(parents=True, exist_ok=True)
        cls.log_file().touch(exist_ok=True)
