class EndtrzException(Exception):
    """Base exception for this script.

    :note: This exception should not be raised directly."""
    pass


class QueryReturnedBadRequestException(EndtrzException):
    pass


class QueryReturnedForbiddenException(EndtrzException):
    pass


class ProfileNotExistsException(EndtrzException):
    pass


class ProfileHasNoPicsException(EndtrzException):
    """
    .. deprecated:: 4.2.2
       Not raised anymore.
    """
    pass


class PrivateProfileNotFollowedException(EndtrzException):
    pass


class LoginRequiredException(EndtrzException):
    pass


class LoginException(EndtrzException):
    pass


class TwoFactorAuthRequiredException(LoginException):
    pass


class InvalidArgumentException(EndtrzException):
    pass


class BadResponseException(EndtrzException):
    pass


class BadCredentialsException(LoginException):
    pass


class ConnectionException(EndtrzException):
    pass


class PostChangedException(EndtrzException):
    """.. versionadded:: 4.2.2"""
    pass


class QueryReturnedNotFoundException(ConnectionException):
    pass


class TooManyRequestsException(ConnectionException):
    pass

class IPhoneSupportDisabledException(EndtrzException):
    pass

class AbortDownloadException(Exception):
    """
    Exception that is not catched in the error catchers inside the download loop and so aborts the
    download loop.

    This exception is not a subclass of ``EndtrzException``.

    .. versionadded:: 4.7
    """
    pass
