class SettingsViewModel:
    def __init__(self, config_service, log_service):
        self.config_service = config_service
        self.log_service = log_service

    def get_hide_to_tray(self) -> bool:
        settings = self.config_service.load_settings()
        return settings.hide_to_tray

    def get_ask_on_close(self) -> bool:
        settings = self.config_service.load_settings()
        return settings.ask_on_close

    def set_hide_to_tray(self, hide_to_tray: bool) -> tuple[bool, str]:
        settings = self.config_service.load_settings()
        settings.hide_to_tray = hide_to_tray

        self.config_service.save_settings(settings)
        self.log_service.write(f"设置已更新：hide_to_tray = {hide_to_tray}")

        return True, "设置已保存"

    def set_ask_on_close(self, ask_on_close: bool) -> tuple[bool, str]:
        settings = self.config_service.load_settings()
        settings.ask_on_close = ask_on_close

        self.config_service.save_settings(settings)
        self.log_service.write(f"设置已更新：ask_on_close = {ask_on_close}")

        return True, "设置已保存"

    def save_close_settings(
        self,
        hide_to_tray: bool,
        ask_on_close: bool
    ) -> tuple[bool, str]:
        settings = self.config_service.load_settings()
        settings.hide_to_tray = hide_to_tray
        settings.ask_on_close = ask_on_close

        self.config_service.save_settings(settings)

        self.log_service.write(
            f"关闭按钮设置已更新：hide_to_tray = {hide_to_tray}, ask_on_close = {ask_on_close}"
        )

        return True, "设置已保存"