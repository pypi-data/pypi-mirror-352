import json
import logging
import threading
import typing
import uuid

from paho.mqtt.client import Client as PahoMqttClient, MQTT_ERR_SUCCESS, error_string
from paho.mqtt.client import MQTTMessage
from paho.mqtt.enums import MQTTErrorCode

from gridgs.sdk.auth import Client as AuthClient
from gridgs.sdk.entity import session_event_from_dict, SessionEvent, Token
from gridgs.sdk.logger_fields import with_session_event
from gridgs.sdk.ssl import Settings as SslSettings


class Subscriber:
    def __init__(self, host: str, port: int, auth_client: AuthClient, ssl_settings: SslSettings | None, logger: logging.Logger):
        self.__is_running_lock = threading.Lock()
        self.__stop_event = threading.Event()

        self.__host = host
        self.__port = port
        self.__auth_client = auth_client
        self.__mqtt_client = PahoMqttClient(client_id='api-events-' + str(uuid.uuid4()), reconnect_on_failure=True)
        if isinstance(ssl_settings, SslSettings):
            self.__mqtt_client.tls_set(tls_version=ssl_settings.version)
            self.__mqtt_client.tls_insecure_set(ssl_settings.verify)
        self.__logger = logger

        def mqtt_client_log_callback(client, userdata, level, buf):
            self.__logger.debug(f'PahoMqtt: {buf}')

        self.__mqtt_client.on_log = mqtt_client_log_callback




    def on_event(self, func: typing.Callable[[SessionEvent], None]):
        def on_message(client, userdata, msg: MQTTMessage):
            try:
                session_event_dict = json.loads(msg.payload)
                session_event = session_event_from_dict(session_event_dict)
                self.__logger.info('Session event received', extra=with_session_event(session_event))
                func(session_event)
            except Exception as e:
                self.__logger.error(f'Error processing session event: {e}', exc_info=True, extra={'session_event_payload': msg.payload})

        self.__mqtt_client.on_message = on_message

    def run(self):
        with self.__is_running_lock:
            self.__stop_event.clear()

            self.__logger.info('Starting')

            token = self.__get_token_and_set_credentials()

            def __on_connect(client: PahoMqttClient, userdata, flags, reason_code):
                if self.__stop_event.is_set():
                    self.__logger.info('Connected. Ignore Subscribing. Stop is called')
                    client.disconnect()
                    return

                self.__logger.info('Connected. Subscribing')
                client.subscribe(topic=_build_sessions_event_topic(token.company_id))

            self.__mqtt_client.on_connect = __on_connect

            def __on_disconnect(client, userdata, rc):
                self.__logger.info(f'Disconnected: {error_string(rc)}')
                if rc != MQTT_ERR_SUCCESS and not self.__stop_event.is_set():
                    self.__get_token_and_set_credentials()

            self.__mqtt_client.on_disconnect = __on_disconnect

            self.__mqtt_client.connect(self.__host, self.__port)
            self.__mqtt_client.loop_forever(retry_first_connection=True)

    def stop(self) -> MQTTErrorCode:
        self.__logger.info('Stopping...')
        self.__stop_event.set()
        return self.__mqtt_client.disconnect()

    def __get_token_and_set_credentials(self) -> Token:
        token = self.__auth_client.token()
        self.__mqtt_client.username_pw_set(username=token.username, password=token.access_token)
        return token


def _build_sessions_event_topic(company_id: int) -> str:
    return f'company/{company_id}/session_event'
