class DiscogsAPIError(Exception):
    """Root Exception class for Discogs API errors."""
    pass


class TooManyAttemptsError(DiscogsAPIError):
    """
    Exception class for when the ratelimit for the API is hit too many times
    consecutively and backing off has not helped.
    """
    def __init__(self):
        self.msg = (
            "Failed to make request due to the API "
            "returning 429, rate limited response, consecutively too many times. "
            "Back off function has not helped."
        )

    def __str__(self):
        return self.msg

class ConfigurationError(DiscogsAPIError):
    """Exception class for problems with the configuration of this client."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class HTTPError(DiscogsAPIError):
    """Exception class for HTTP errors."""
    def __init__(self, message, code):
        self.status_code = code
        self.msg = '{0}: {1}'.format(code, message)

    def __str__(self):
        return self.msg


class AuthorizationError(HTTPError):
    """The server rejected the client's credentials."""
    def __init__(self, message, code, response):
        super(AuthorizationError, self).__init__(message, code)
        self.msg = '{0} Response: {1!r}'.format(self.msg, response)


class MalformedResponseError(DiscogsAPIError):
    """
    Raised when the Discogs API returns a response body that cannot be
    parsed as JSON. This is distinct from ``json.JSONDecodeError`` so that
    callers have a stable, library-specific exception to catch and retry
    on, without depending on the JSON parser's own exception type.
    """
    def __init__(self, status_code, content, original_exception=None):
        self.status_code = status_code
        self.content = content
        self.original_exception = original_exception
        self.msg = (
            'Discogs API returned a response that could not be parsed as '
            'JSON (status code {0}): {1!r}'.format(status_code, content)
        )

    def __str__(self):
        return self.msg
