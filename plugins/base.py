from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PluginContext:
    user_id: int
    username: str
    user_is_admin: bool
    message_id: int = None
    chat_id: int = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class PluginResponse:
    success: bool
    message: str
    data: dict = None
    ephemeral: bool = False

    @classmethod
    def ok(cls, message: str, data: dict = None, **kwargs):
        return cls(success=True, message=message, data=data, **kwargs)

    @classmethod
    def error(cls, message: str, **kwargs):
        return cls(success=False, message=message, **kwargs)


class BasePlugin(ABC):
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    commands: dict[str, str] = {}
    required_role: str = None
    cooldown: int = 0

    def __init__(self):
        self._last_used: dict[int, datetime] = {}

    @abstractmethod
    def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        pass

    def can_execute(self, ctx: PluginContext) -> tuple:
        if self.required_role == 'admin' and not ctx.user_is_admin:
            return False, "Только для админов"
        return True, ""

    def record_usage(self, ctx: PluginContext):
        self._last_used[ctx.user_id] = datetime.now()