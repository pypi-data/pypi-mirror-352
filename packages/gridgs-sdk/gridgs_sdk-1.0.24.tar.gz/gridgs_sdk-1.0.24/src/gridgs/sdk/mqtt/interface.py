from abc import ABC, abstractmethod
from typing import Callable

from paho.mqtt.client import MQTTMessageInfo
from paho.mqtt.enums import MQTTErrorCode

from gridgs.sdk.entity import Frame, Session


class Connector(ABC):
    @abstractmethod
    def connect(self, session: Session, on_connected: Callable[[Session], None] | None = None) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> MQTTErrorCode:
        pass


class Sender(ABC):
    @abstractmethod
    def send(self, raw_data: bytes) -> MQTTMessageInfo:
        pass


class Receiver(ABC):
    @abstractmethod
    def on_downlink(self, on_downlink: Callable[[Frame], None]):
        pass
