from dataclasses import dataclass


@dataclass
class AppSettings:
    hide_to_tray: bool = True
    ask_on_close: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "AppSettings":
        if not isinstance(data, dict):
            data = {}

        return cls(
            hide_to_tray=bool(data.get("hide_to_tray", True)),
            ask_on_close=bool(data.get("ask_on_close", True)),
        )

    def to_dict(self) -> dict:
        return {
            "hide_to_tray": self.hide_to_tray,
            "ask_on_close": self.ask_on_close,
        }