import ssl
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    version: ssl._SSLMethod = ssl.PROTOCOL_TLSv1_2
    verify: bool = True