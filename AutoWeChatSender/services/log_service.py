from datetime import datetime

from services.path_service import PathService


class LogService:
    def __init__(self):
        PathService.init_runtime_files()
        self.log_file = PathService.log_file()

    def write(self, text: str) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{now}] {text}\n")
