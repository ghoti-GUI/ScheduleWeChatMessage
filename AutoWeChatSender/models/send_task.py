from dataclasses import dataclass


@dataclass
class SendTask:
    comment: str = ""
    group_name: str = ""
    message: str = ""
    image_path: str = ""
    weekday: str = ""
    time: str = ""
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "SendTask":
        return cls(
            comment=str(data.get("comment", "")),
            group_name=str(data.get("group_name", "")),
            message=str(data.get("message", "")),
            image_path=str(data.get("image_path", "")),
            weekday=str(data.get("weekday", "")),
            time=str(data.get("time", "")),
            enabled=bool(data.get("enabled", True)),
        )
