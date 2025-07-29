import base64
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .ground_station import GroundStation, ground_station_from_dict
from .satellite import Satellite, satellite_from_dict
from .session import Session, session_from_dict

class FrameType(Enum):
    RECEIVED = 1
    SENT = 2


@dataclass(frozen=True)
class Frame:
    id: uuid.UUID
    created_at: datetime
    type: FrameType
    satellite: Satellite
    ground_station: GroundStation
    session: Session
    raw_data: bytes
    extra_data: dict = None


def frame_from_dict(frame_dict: dict) -> Frame:
    return Frame(
        id=uuid.UUID(frame_dict['id']),
        created_at=datetime.fromisoformat(frame_dict['createdAt']) if 'createdAt' in frame_dict else None,
        type=FrameType(frame_dict['type']) if 'type' in frame_dict else None,
        satellite=satellite_from_dict(frame_dict['satellite']) if 'satellite' in frame_dict else None,
        ground_station=ground_station_from_dict(frame_dict['groundStation']) if 'groundStation' in frame_dict else None,
        session=session_from_dict(frame_dict['communicationSession']) if 'communicationSession' in frame_dict else None,
        raw_data=base64.b64decode(frame_dict['rawData']) if 'rawData' in frame_dict else None,
        extra_data=frame_dict.get('extraData'),
    )
