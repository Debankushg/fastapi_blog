class AppException(Exception):
    status_code = 500
    detail = "Internal server error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail
        super().__init__(self.detail)


class NotFoundError(AppException):
    status_code = 404
    detail = "Resource not found"


class ConflictError(AppException):
    status_code = 409
    detail = "Resource already exists"


class UnauthorizedError(AppException):
    status_code = 401
    detail = "Invalid credentials"


class ForbiddenError(AppException):
    status_code = 403
    detail = "You do not have permission to perform this action"
