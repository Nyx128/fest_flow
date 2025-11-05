from pydantic import BaseModel

class FestBase(BaseModel):
    name: str
    year: int


class FestCreate(FestBase):
    pass


class Fest(FestBase):
    fest_id: int

    class Config:
        from_attributes = True