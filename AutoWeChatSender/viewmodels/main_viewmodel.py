from services.config_service import ConfigService
from services.log_service import LogService
from services.scheduler_service import SchedulerService
from services.wechat_service import WeChatService


class MainViewModel:
    """
    ViewModel：
    - View 只调用这里；
    - View 不直接接触 WeChatService / SchedulerService；
    - 以后要增加 AI 代理、订单、库存等功能，也从这里暴露给界面。
    """

    def __init__(self):
        self.log_service = LogService()
        self.config_service = ConfigService(self.log_service)
        self.wechat_service = WeChatService(self.log_service)

        self.scheduler_service = SchedulerService(
            config_service=self.config_service,
            wechat_service=self.wechat_service,
            log_service=self.log_service
        )

    def init_app(self) -> None:
        self.config_service.init_config()
        self.log_service.write("程序初始化完成")

    def start_scheduler(self) -> tuple[bool, str]:
        started = self.scheduler_service.start_thread()

        if started:
            return True, "运行中"

        return False, "已在运行中"

    def stop_scheduler(self) -> tuple[bool, str]:
        stopped = self.scheduler_service.stop_thread()

        if stopped:
            return True, "已停止"

        return False, "当前未运行"

    def quit_app(self) -> None:
        self.scheduler_service.stop_thread() # 有没有关闭软件？

    def is_running(self) -> bool:
        return self.scheduler_service.is_running()
