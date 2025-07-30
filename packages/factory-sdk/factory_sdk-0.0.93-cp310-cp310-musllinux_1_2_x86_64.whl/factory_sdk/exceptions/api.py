class FactoryException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundException(FactoryException):
    def __init__(self, message: str = "Not Found"):
        super().__init__(message)


class ConflictException(FactoryException):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message)


class AuthenticationException(FactoryException):
    def __init__(self, message: str = "Authentication Exception"):
        super().__init__(message)


class GeneralAPIException(FactoryException):
    def __init__(self, message: str = "General API Exception"):
        super().__init__(message)


class FileUploadException(FactoryException):
    def __init__(self, message: str = "File Upload Exception"):
        super().__init__(message)
