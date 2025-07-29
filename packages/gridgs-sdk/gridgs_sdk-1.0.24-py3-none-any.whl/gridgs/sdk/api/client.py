from .frame_client import FrameClient
from .session_client import SessionClient


class Client(SessionClient, FrameClient):
    pass
