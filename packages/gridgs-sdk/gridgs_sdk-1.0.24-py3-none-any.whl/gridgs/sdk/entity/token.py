class Token:
    def __init__(self, username: str, company_id: int, access_token: str):
        if not access_token:
            raise ValueError('Access token is empty')
        self.__username = username
        self.__company_id = company_id
        self.__access_token = access_token

    @property
    def username(self) -> str:
        return self.__username

    @property
    def company_id(self) -> int:
        return self.__company_id

    @property
    def access_token(self) -> str:
        return self.__access_token

