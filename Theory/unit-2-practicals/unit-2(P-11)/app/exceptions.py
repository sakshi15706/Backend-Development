"""Domain errors. Services raise these; main.py turns them into HTTP responses.
That keeps HTTP details out of the business logic."""


class AppError(Exception):
    status_code = 500

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class ForbiddenError(AppError):
    status_code = 403
