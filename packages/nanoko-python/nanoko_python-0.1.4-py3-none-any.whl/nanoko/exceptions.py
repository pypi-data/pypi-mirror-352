import httpx


class NanokoException(Exception):
    """Base exception for all Nanoko exceptions."""

    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class NanokoAPIException(NanokoException):
    """Exception for all API exceptions."""

    def __init__(self, message: str, status_code: int, response: httpx.Response):
        self.message = message
        self.status_code = status_code
        self.response = response

    def __str__(self):
        return f"Status code: {self.status_code} - {self.message}"


class NanokoAPI400BadRequestError(NanokoAPIException):
    """Exception for all 400 bad request errors."""

    def __init__(self, message: str, response: httpx.Response):
        super().__init__(message, 400, response)


class NanokoAPI401UnauthorizedError(NanokoAPIException):
    """Exception for all 401 unauthorized errors."""

    def __init__(self, message: str, response: httpx.Response):
        super().__init__(message, 401, response)


class NanokoAPI403ForbiddenError(NanokoAPIException):
    """Exception for all 403 forbidden errors."""

    def __init__(self, message: str, response: httpx.Response):
        super().__init__(message, 403, response)


class NanokoAPI404NotFoundError(NanokoAPIException):
    """Exception for all 404 not found errors."""

    def __init__(self, message: str, response: httpx.Response):
        super().__init__(message, 404, response)


class NanokoAPI405MethodNotAllowedError(NanokoAPIException):
    """Exception for all 405 method not allowed errors."""

    def __init__(self, message: str, response: httpx.Response):
        super().__init__(message, 405, response)


class NanokoAPI415UnsupportedMediaTypeError(NanokoAPIException):
    """Exception for all 415 unsupported media type errors."""

    def __init__(self, message: str, response: httpx.Response):
        super().__init__(message, 415, response)


class NanokoAPI422ValidationError(NanokoAPIException):
    """Exception for all 422 validation errors."""

    def __init__(self, message: str, response: httpx.Response):
        super().__init__(message, 422, response)


class NanokoAPI500InternalServerError(NanokoAPIException):
    """Exception for all 500 internal server errors."""

    def __init__(self, message: str, response: httpx.Response):
        super().__init__(message, 500, response)


api_exceptions = {
    400: NanokoAPI400BadRequestError,
    401: NanokoAPI401UnauthorizedError,
    403: NanokoAPI403ForbiddenError,
    404: NanokoAPI404NotFoundError,
    405: NanokoAPI405MethodNotAllowedError,
    415: NanokoAPI415UnsupportedMediaTypeError,
    422: NanokoAPI422ValidationError,
    500: NanokoAPI500InternalServerError,
}


def raise_nanoko_api_exception(response: httpx.Response):
    """Raise the appropriate Nanoko API exception based on the response status code.

    Args:
        response (httpx.Response): The response from the API.

    Raises:
        NanokoAPIException: The appropriate Nanoko API exception based on the response status code.
    """
    exception_class = api_exceptions.get(response.status_code)
    if exception_class:
        raise exception_class(response.text, response)
