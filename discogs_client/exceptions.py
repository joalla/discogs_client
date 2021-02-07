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
            "Failed to make request due to the API"
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
