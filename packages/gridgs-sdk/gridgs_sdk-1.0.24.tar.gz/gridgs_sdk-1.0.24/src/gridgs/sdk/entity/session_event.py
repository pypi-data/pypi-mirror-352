from dataclasses import dataclass

from .session import Session, session_from_dict


@dataclass(frozen=True)
class SessionEvent:
    EVENT_CREATE = 'created'
    EVENT_UPDATE = 'updated'
    EVENT_REMOVE = 'removed'

    type: str
    session: Session


def session_event_from_dict(obj: dict) -> SessionEvent:
    return SessionEvent(type=obj['type'], session=session_from_dict(obj['entity']))
