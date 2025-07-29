from abc import ABC, abstractmethod
from typing import Optional

from pipelex.mission.mission import Mission


class MissionManagerAbstract(ABC):
    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def teardown(self) -> None:
        pass

    @abstractmethod
    def get_optional_mission(self, mission_id: str) -> Optional[Mission]:
        pass

    @abstractmethod
    def get_mission(self, mission_id: str) -> Mission:
        pass

    @abstractmethod
    def add_new_mission(self) -> Mission:
        pass
