from pydantic import BaseModel, root_validator

from beauty.settings import settings


class User(BaseModel):
    pass


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

    @root_validator(pre=True)
    def validate(cls, values):
        url = values.get("url")
        if "netbian" in url:
            values["url"] = url.replace(
                "http://img.netbian.com", settings.SITE_URL + "/img.netbian.com"
            )
        return values


class PictureResponse(BaseModel):
    data: list[Picture]
    total: int
