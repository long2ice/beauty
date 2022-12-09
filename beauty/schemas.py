from pydantic import BaseModel, NonNegativeInt


class Page(BaseModel):
    limit: NonNegativeInt = 10
    offset: NonNegativeInt = 0
