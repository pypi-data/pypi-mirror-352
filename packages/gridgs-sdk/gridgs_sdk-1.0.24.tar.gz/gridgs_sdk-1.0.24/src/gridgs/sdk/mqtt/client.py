import json
import logging
import threading
import uuid
from typing import Callable

from paho.mqtt.client import Client as PahoMqttClient, MQTTMessageInfo, MQTTMessage, MQTT_ERR_SUCCESS, error_string
from paho.mqtt.enums import MQTTErrorCode

from gridgs.sdk.auth import Client as AuthClient
from gridgs.sdk.entity import Frame, frame_from_dict, Session
from gridgs.sdk.logger_fields import with_frame, with_session, with_frame_payload_size
from gridgs.sdk.ssl import Settings as SslSettings
from .exceptions import SessionNotFoundException, SendUplinkException
from .interface import Connector, Sender, Receiver


class Client(Connector, Sender, Receiver):
    def __init__(self, host: str, port: int, auth_client: AuthClient, ssl_settings: SslSettings | None, logger: logging.Logger):
        self.__is_running_lock = threading.Lock()
        self.__stop_event = threading.Event()

        self.__host = host
        self.__port = port
        self.__auth_client = auth_client
        self.__mqtt_client = PahoMqttClient(client_id='api-frames-' + str(uuid.uuid4()), reconnect_on_failure=True)
        if isinstance(ssl_settings, SslSettings):
            self.__mqtt_client.tls_set(tls_version=ssl_settings.version)
            self.__mqtt_client.tls_insecure_set(ssl_settings.verify)
        self.__session: Session | None = None
        self.__logger = logger

    def on_downlink(self, on_downlink: Callable[[Frame], None]):
        def __on_message(client, userdata, msg: MQTTMessage):
            try:
                frame_dict = json.loads(msg.payload)
                frame = frame_from_dict(frame_dict)
                self.__logger.info('Downlink frame', extra=with_frame(frame))
                on_downlink(frame)
            except Exception as e:
                self.__logger.error(f'Error processing downlink: {e}', exc_info=True, extra={'frame_payload': msg.payload})

        self.__mqtt_client.on_message = __on_message

    def connect(self, session: Session, on_connected: Callable[[Session], None] | None = None):
        if not isinstance(session, Session):
            raise SessionNotFoundException("Pass session to connect")
        with self.__is_running_lock:
            self.__stop_event.clear()

            self.__logger.info('Connecting', extra=with_session(session))
            self.__session = session

            def __on_mqtt_connect(client: PahoMqttClient, userdata, flags, reason_code):
                extra_logger_fields = with_session(session)
                extra_logger_fields['rc'] = reason_code

                if self.__stop_event.is_set():
                    self.__logger.info('Connected. Ignore Subscribing. Stop is called', extra=extra_logger_fields)
                    client.disconnect()
                    return

                self.__logger.info('Connected. Subscribing', extra=extra_logger_fields)
                client.subscribe(topic=_build_downlink_topic(session))

            self.__mqtt_client.on_connect = __on_mqtt_connect

            def __on_subscribed(client: PahoMqttClient, userdata, mid, granted_qos):
                self.__logger.info(f'Subscribed', extra=with_session(session))
                if on_connected:
                    on_connected(session)

            self.__mqtt_client.on_subscribe = __on_subscribed

            def __on_disconnect(client, userdata, rc):
                self.__logger.info(f'Disconnected: {error_string(rc)}', extra=with_session(session))
                if rc != MQTT_ERR_SUCCESS and not self.__stop_event.is_set():
                    self.__set_credentials()

            self.__mqtt_client.on_disconnect = __on_disconnect

            self.__set_credentials()
            self.__mqtt_client.connect(self.__host, self.__port)
            self.__mqtt_client.loop_forever(retry_first_connection=True)

    def disconnect(self) -> MQTTErrorCode:
        self.__logger.info('Disconnecting', extra=with_session(self.__session))
        self.__stop_event.set()
        return self.__mqtt_client.disconnect()

    def send(self, raw_data: bytes) -> MQTTMessageInfo:
        self.__logger.info('Sending uplink', extra=with_frame_payload_size(raw_data) | with_session(self.__session))
        if not isinstance(self.__session, Session):
            raise SessionNotFoundException('Session not found. Connect first')
        message_info = self.__mqtt_client.publish(topic=_build_uplink_topic(self.__session), payload=raw_data)
        if not message_info.rc == MQTT_ERR_SUCCESS:
            raise SendUplinkException(f'Uplink frame can not be sent: {error_string(message_info.rc)}')
        return message_info

    def __set_credentials(self):
        token = self.__auth_client.token()
        self.__mqtt_client.username_pw_set(username=token.username, password=token.access_token)


def _build_downlink_topic(session: Session) -> str:
    return f'satellite/{session.satellite.id}/downlink/gs/{session.ground_station.id}'


def _build_uplink_topic(session: Session) -> str:
    return f'satellite/{session.satellite.id}/uplink/gs/{session.ground_station.id}'
