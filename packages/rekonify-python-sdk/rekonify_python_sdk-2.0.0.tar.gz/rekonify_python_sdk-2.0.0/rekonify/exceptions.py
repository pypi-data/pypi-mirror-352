class RekonifyError(Exception):
    """Base exception for all Rekonify errors"""
    pass


class RekonifyRequestError(RekonifyError):
    """Errors related to HTTP requests"""
    pass


class RekonifyClientError(RekonifyError):
    """4xx errors from the API"""
    pass


class RekonifyServerError(RekonifyError):
    """5xx errors from the API"""
    pass


class RekonifyAuthenticationError(RekonifyClientError):
    """Authentication failed"""
    pass


class RekonifyRateLimitError(RekonifyClientError):
    """Rate limit exceeded"""
    pass
