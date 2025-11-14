"""
HTTP Status Code Constants
Use these for all HTTPException status_code parameters
"""

from enum import IntEnum


class HTTPStatus(IntEnum):
    """Standard HTTP status codes as IntEnum for numeric compatibility with FastAPI"""

    # Success codes (2xx)
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    # Client error codes (4xx)
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422

    # Server error codes (5xx)
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503

