class UnknownRequestType(Exception):
    """Raised when a request is unable to be matched to a handler."""

    def __init__(self, request: object, type_name: str) -> None:
        self.request = request
        self.type_name = type_name
        super().__init__(
            "Unable to locate a registered handler for request '{}' (type: {})".format(
                request, type_name
            )
        )
