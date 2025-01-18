""" Request Verb Definition """

from enum import Enum


class RequestVerbType(str, Enum):
    """Defines the types of requests supported."""

    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    HEAD = "head"
    OPTIONS = "options"
