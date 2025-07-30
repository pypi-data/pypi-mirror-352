import logging
from typing import List

import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from rekonify import constants, exceptions, __version__
from rekonify.models import Transaction

logger = logging.getLogger(__name__)


class RekonifyClient:
    """
    Python SDK for interacting with the Rekonify API.
    Supports both synchronous and asynchronous requests.
    """

    _uri = ""
    base_url = "https://api.rekonify.com"

    def __init__(self, api_key: str = None, app_key: str = None, version="v1"):
        self.api_key = api_key
        self.app_key = app_key
        self.version = version
        self.__session = requests.Session()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(
            (exceptions.RekonifyRateLimitError, requests.exceptions.Timeout)
        ),
    )
    def post_transaction(self, transaction: Transaction):
        """
        Post single transaction for recon
        :param transaction:
        :return:
        """
        self._uri = "ingestion/transactions"

        return self.__api_call(method="POST", payload=transaction.model_dump())

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(requests.exceptions.Timeout),
    )
    def post_bulk_transactions(self, transactions: List[Transaction]):
        """
        Post Bulk transactions for recon
        :param transactions:
        :return:
        """
        self._uri = "ingestion/transactions"

        transactions = [trx.model_dump() for trx in transactions]

        return self.__api_call(method="PUT", payload=transactions)

    async def apost_transaction(self):
        pass

    async def abulk_transactions(self):
        pass

    def __api_call(self, method="GET", payload=None):
        """
        Calls Endpoint with appropriate payload
        :param method:
        :param payload:
        :return:
        """
        if payload is None:
            payload = {}

        endpoint = f"{self.base_url}/{self.version}/{self._uri}"

        logger.debug(f"Making {method} request to {endpoint}")

        headers = {
            "User-Agent": f"RekonifyClient/{__version__} Python SDK",
            "Content-Type": "application/json",
            constants.X_API_KEY: self.api_key,
            constants.X_APP_KEY: self.app_key,
        }

        print(headers)

        try:
            response = self.__session.request(
                method=method,
                url=endpoint,
                json=payload,
                headers=headers,
                timeout=constants.DEFAULT_TIMEOUT,
            )

            if response.status_code == 401:
                raise exceptions.RekonifyError(
                    "Authentication failed - check your credentials"
                )

            if response.status_code == 429:
                raise exceptions.RekonifyError("Rate limit exceeded")

            response.raise_for_status()

            if response.status_code == 204:
                return True

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise exceptions.RekonifyRequestError(f"API request failed: {str(e)}")
