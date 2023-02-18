from pydantic import BaseModel, root_validator

from beauty.third.s3 import format_url


class User(BaseModel):
    avatar: str
    nickname: str

    @root_validator(pre=True)
    def validate_avatar(cls, values):
        avatar = values.get("avatar")
        if not avatar.startswith("http"):
            values["avatar"] = format_url(avatar)
        return values


class LoginResponse(BaseModel):
    token: str
    user: User


class Picture(BaseModel):
    id: int
    url: str
    favorite_count: int
    like_count: int
    like: bool
    favorite: bool
    description: str

    @root_validator(pre=True)
    def validate(cls, values):
        url = values.get("url")
        values["url"] = format_url(url)
        return values


class PictureResponse(BaseModel):
    data: list[Picture]
    total: int


class Collection(BaseModel):
    id: int
    title: str
    description: str
    url: str

    @root_validator(pre=True)
    def validate(cls, values):
        url = values.get("url")
        values["url"] = format_url(url)
        return values


class CollectionResponse(BaseModel):
    data: list[Collection]
    total: int
