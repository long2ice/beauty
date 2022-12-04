from pydantic import BaseModel, NonNegativeInt, conint


class Page(BaseModel):
    limit: conint(le=20) = 10
    offset: NonNegativeInt = 0
