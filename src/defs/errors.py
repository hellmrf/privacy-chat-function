class StatusCodeError(Exception):
    status_code: int
    message: str

    def __init__(self,
                 status_code: int = 500,
                 message: str | Exception = "") -> None:
        self.message = str(message)
        self.status_code = status_code


class BadRequestError(StatusCodeError):

    def __init__(self, message: str | Exception = "Bad request") -> None:
        super().__init__(400, message)


class NotFoundError(StatusCodeError):

    def __init__(self, message: str | Exception = "Not found") -> None:
        super().__init__(404, message)


class InternalServerError(StatusCodeError):

    def __init__(self,
                 message: str | Exception = "Internal server error") -> None:
        super().__init__(500, message)
