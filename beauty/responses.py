from pydantic import BaseModel


class User(BaseModel):
    pass


class LoginResponse(BaseModel):
    token: str
    user: User
