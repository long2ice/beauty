from pydantic import BaseModel, NonNegativeInt


class Page(BaseModel):
    limit: NonNegativeInt = 1000
    offset: NonNegativeInt = 0
