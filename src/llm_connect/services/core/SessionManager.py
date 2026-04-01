from abc import ABC, abstractmethod


class SessionManager(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def accept(self, session, activity, interaction):
        pass

    @abstractmethod
    async def evaluate(self, interaction) -> bool:
        pass

    @abstractmethod
    async def is_final(self, session, activity):
        pass

    @abstractmethod
    async def update(self, session, activity):
        pass

    @abstractmethod
    async def can_move(self, session_id: str, content: str) -> bool:
        pass

    @abstractmethod
    async def move(self):
        pass

    @abstractmethod
    async def re_interact(self, session, activity, content: str):
        pass
