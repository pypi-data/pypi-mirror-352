import json
import logging
from dataclasses import replace
from typing import Callable, Iterator
from urllib.parse import urljoin

import requests

from gridgs.sdk.auth import Client as AuthClient
from .params import PaginatedQueryParams


class BaseClient:
    __iterator_chunk_size = 500

    def __init__(self, base_url: str, auth_client: AuthClient, logger: logging.Logger, verify=True):
        self.__base_url = base_url
        self.__auth_client = auth_client
        self.__logger = logger
        self.__verify = verify

    def request(self, method: str, path: str, params: dict | None = None, data: dict | None = None) -> requests.Response:
        return requests.request(
            method,
            urljoin(self.__base_url, path),
            params=params,
            data=json.dumps(data) if isinstance(data, dict) and data else None,
            headers=self.__build_auth_header(),
            verify=self.__verify
        )

    def __build_auth_header(self) -> dict:
        token = self.__auth_client.token()
        return {'Authorization': 'Bearer ' + token.access_token}

    def _iterate_items(self, params: PaginatedQueryParams, items_fetcher: Callable[[PaginatedQueryParams], requests.Response], item_builder: Callable[[dict], object]) -> Iterator:
        iterated = 0
        total_limit = params.limit if isinstance(params.limit, int) else 0
        chunk_size = min(total_limit, self.__iterator_chunk_size) if total_limit > 0 else self.__iterator_chunk_size
        total = params.offset + 1  # to run while loop it should be more than offset
        params = replace(params, limit=chunk_size)  # limit plays role of chunk size here

        while params.offset < total:
            if 0 < total_limit <= iterated:
                return

            response = items_fetcher(params)

            for row in response.json():
                if 0 < total_limit <= iterated:
                    return

                yield item_builder(row)
                iterated += 1

            total = int(response.headers.get('Pagination-Count'))
            params = replace(params, offset=params.offset + params.limit)
