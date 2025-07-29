import logging
from datetime import datetime, timedelta
from threading import Lock

from keycloak import KeycloakOpenID, KeycloakError

from gridgs.sdk.entity import Token


class Client:
    __PRE_EXPIRATION_SECONDS = 20

    def __init__(self, open_id_client: KeycloakOpenID, username: str, password: str, company_id: int, logger: logging.Logger):
        self.__lock = Lock()
        self.__open_id_client = open_id_client
        self.__username = username
        self.__password = password
        self.__company_id = company_id
        self.__token: Token | None = None
        self.__token_expires_at: datetime = datetime.min
        self.__refresh_token_value: str = ''
        self.__refresh_expires_at: datetime = datetime.min
        self.__logger = logger

    def token(self) -> Token:
        with self.__lock:
            if self.__token is None or not self.__refresh_token_value or datetime.now() >= self.__refresh_expires_at:
                self.__obtain_new_token()
            elif datetime.now() >= self.__token_expires_at:
                try:
                    self.__refresh_token()
                except KeycloakError as e:
                    self.__logger.warning(f'Can not refresh token: {e.error_message}', exc_info=True)
                    self.__obtain_new_token()

            return self.__token

    def __obtain_new_token(self):
        self.__logger.info('Requesting token')
        oauth_token = self.__open_id_client.token(username=self.__username, password=self.__password)
        self.__set_tokens_values(oauth_token)

    def __refresh_token(self):
        self.__logger.info('Refreshing token')
        oauth_token = self.__open_id_client.refresh_token(refresh_token=self.__refresh_token_value)
        self.__set_tokens_values(oauth_token)

    def __set_tokens_values(self, oauth_token: dict):
        self.__token = Token(username=self.__username, company_id=self.__company_id, access_token=oauth_token.get('access_token'))
        self.__token_expires_at = datetime.now() + timedelta(seconds=int(oauth_token.get('expires_in', 0))) - timedelta(seconds=self.__PRE_EXPIRATION_SECONDS)

        self.__refresh_token_value = oauth_token.get('refresh_token')
        self.__refresh_expires_at = datetime.now() + timedelta(seconds=int(oauth_token.get('refresh_expires_in', 0))) - timedelta(seconds=self.__PRE_EXPIRATION_SECONDS)

        self.__logger.info('Token info', extra=_log_with_auth_token(oauth_token))

    def logout(self) -> None:
        with self.__lock:
            self.__logger.info('Logging out')
            if self.__refresh_token_value:
                self.__open_id_client.logout(self.__refresh_token_value)
            self.__refresh_token_value = ''
            self.__token_expires_at = datetime.min
            self.__refresh_expires_at = datetime.min


def _log_with_auth_token(value: dict) -> dict:
    if isinstance(value, dict):
        return {
            'oauth_with_token': True if value.get('access_token') else False,
            'oauth_expires_in': value.get('expires_in'),
            'oauth_with_refresh': True if value.get('refresh_token') else False,
            'oauth_refresh_expires_at': value.get('refresh_expires_in')}
    return {}
