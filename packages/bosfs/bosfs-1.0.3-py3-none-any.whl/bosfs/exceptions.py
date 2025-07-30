import errno

from baidubce.exception import BceError

ERROR_CODE_TO_EXCEPTION = {
    404: FileNotFoundError,
    403: PermissionError,
    "NoSuchBucket": FileNotFoundError,
    "NoSuchKey": FileNotFoundError,
    "NotFound": FileNotFoundError,
    "InvalidBucketName": FileNotFoundError,
    "AccessDenied": PermissionError,
}

def translate_bos_error(
    error: BceError, *args, message=None, set_cause=True, **kwargs
) -> BaseException:
    """Convert a ClientError exception into a Python one.
    Parameters
    ----------
    error : baidubce.exception.BceError
        The exception returned by the BOS Server or BOS SDK Client.
    message : str
        An error message to use for the returned exception. If not given, the
        error message returned by the server is used instead.
    set_cause : bool
        Whether to set the __cause__ attribute to the previous exception if the
        exception is translated.
    *args, **kwargs :
        Additional arguments to pass to the exception constructor, after the
        error message. Useful for passing the filename arguments to
        ``IOError``.
    Returns
    -------
    An instantiated exception ready to be thrown. If the error code isn't
    recognized, an IOError with the original error message is returned.
    """
    if not isinstance(error, BceError):
        # not a bos error:
        return error
    code = error.code
    if not code:
        code = error.status_code
    #print(code)
    constructor = ERROR_CODE_TO_EXCEPTION.get(code)
    if constructor:
        if not message:
            message = error.args[0]
        custom_exc = constructor(message, *args, **kwargs)
    else:
        # No match found, wrap this in an IOError with the appropriate message.
        custom_exc = OSError(errno.EIO, message or str(error), *args)

    if set_cause:
        custom_exc.__cause__ = error
    return custom_exc