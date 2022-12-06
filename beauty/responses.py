from pydantic import BaseModel, root_validator

from beauty.settings import settings


class User(BaseModel):
    avatar: str
    nickname: str

    @root_validator(pre=True)
    def validate_avatar(cls, v):
        if not v["avatar"].startswith("http"):
            v["avatar"] = f"{settings.SITE_URL}/static/avatar/{v['avatar']}"
        return v


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
        if "netbian" in url:
            values["url"] = url.replace(
                "http://img.netbian.com", settings.SITE_URL + "/img.netbian.com"
            )
        return values


class PictureResponse(BaseModel):
    data: list[Picture]
    total: int


class Collection(BaseModel):
    id: int
    title: str
    description: str
    url: str


class CollectionResponse(BaseModel):
    data: list[Collection]
    total: int
