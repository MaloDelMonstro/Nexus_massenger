from abc import ABC, abstractmethod
from enum import Enum


class GameState(Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"


class BaseGame(ABC):

    name: str = ""
    description: str = ""
    min_players: int = 1
    max_players: int = 2

    def __init__(self):
        self.state = GameState.WAITING
        self.players: list = []
        self.metadata: dict[str, ...] = {}

    @abstractmethod
    def get_state(self) -> dict[str, ...]:
        pass

    @abstractmethod
    def load_state(self, state: dict[str, ...]):
        pass

    def is_finished(self) -> bool:
        return self.state == GameState.FINISHED

    def add_player(self, user_id: int) -> bool:
        if len(self.players) >= self.max_players:
            return False
        if user_id not in self.players:
            self.players.append(user_id)
            if len(self.players) >= self.min_players:
                self.state = GameState.PLAYING
            return True
        return False