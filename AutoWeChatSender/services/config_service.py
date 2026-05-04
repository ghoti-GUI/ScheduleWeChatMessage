import json

from models.send_task import SendTask
from services.path_service import PathService


class ConfigService:
    def __init__(self, log_service=None):
        self.log_service = log_service
        PathService.init_runtime_files()
        self.config_file = PathService.config_file()

    def default_config(self) -> dict:
        return {
            "tasks": [
                {
                    "comment": "测试用例",
                    "group_name": "文件传输助手",
                    "message": "测试文字定时自动发送",
                    "image_path": "",
                    "weekday": "sunday",
                    "time": "18:00",
                    "enabled": True
                }
            ]
        }

    def init_config(self) -> None:
        if not self.config_file.exists():
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.default_config(), f, ensure_ascii=False, indent=4)

    def load_config(self) -> dict:
        self.init_config()

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            if self.log_service:
                self.log_service.write(f"配置文件读取失败：{e}")
            return {"tasks": []}

    def load_tasks(self) -> list[SendTask]:
        config = self.load_config()
        raw_tasks = config.get("tasks", [])
        return [SendTask.from_dict(task) for task in raw_tasks]
