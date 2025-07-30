"""
All helper functions here
"""
import logging

import requests

from rekonify.constants import VERSION, X_API_KEY, X_APP_KEY, DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


class BaseAPI:
    base_url: str = 'https://api.rekonify.com'
    _uri = ''

    def __init__(self):
        self._session = requests.Session()
