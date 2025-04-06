from fastapi import HTTPException


class UserNotAuthorizedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="User is not authorized")


class UserCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Incorrect email or password")


class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User with this email already exists")


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid token")


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="User not found",
        )


class UserAlreadyVerified(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=409,
            detail="User already verified",
        )

class NotFoundRelationship(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Not found relationship for user")

class ItemNotExist(Exception):
    pass

class TaskNotExist(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Задачи не существует.")

class UserAlreadyEmailVerified(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User email already verified!")


class InvalidEmailExeption(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=422,
            detail="Invalid email",
        )


class InvalidPasswordExeption(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=422,
            detail="Invalid password",
        )
