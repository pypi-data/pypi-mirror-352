class ValidationError(Exception):
    """Error indicating the model configuration is invalid.

    Parameters
    ----------
    description : str
        Detailed description of the error as reported by SRS.

    Attributes
    ----------
    message : str
        Message describing the error.
    """

    def __init__(self, description: str):
        super().__init__(f"Model configuration error: {description}")


class UnauthorizedUserError(Exception):
    """Error indicating the user is not authorized to perform requested action.

    This can be thrown in the following circumstances:
        * User is not found in the Platform system
        * User does not have a subscription
        * User does not have sufficient compute credits

    Parameters
    ----------
    description : str
        Detailed description of the error as reported by SRS.

    Attributes
    ----------
    message : str
        Message describing the error.
    """

    def __init__(self, description: str):
        super().__init__(f"Authorization error: {description}")


class NotFoundError(Exception):
    """Custom exception for not found errors.

    Parameters
    ----------
    description : str
        Detailed description of the error as reported by SRS.
    """

    def __init__(self, description: str):
        super().__init__(f"NotFound error: {description}")


class RunConfigError(Exception):
    """Error indicating there was a run configuration error.

    This is thrown when FRED Cloud API has reported an issue with the user's
    request.

    Parameters
    ----------
    key : str
        The general category of the error reported by FRED Cloud API, e.g.
        ``size`` for errors related to instance size, or ``fredVersion`` if the
        specified FRED version is not recognized.
    desc : str
        Detailed description of the error.

    Attributes
    ----------
    key : str
        The general category of the error reported by FRED Cloud API, e.g.
        ``size`` for errors related to instance size, or ``fredVersion`` if the
        specified FRED version is not recognized.
    desc : str
        Detailed description of the error.
    message : str
        Summary message describing the error.
    """

    def __init__(self, key: str, desc: str):
        self.key = key
        self.desc = desc
        super().__init__(f"{self.key} error: {self.desc}")
