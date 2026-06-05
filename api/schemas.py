from pydantic import BaseModel


class ApartmentInput(BaseModel):
    city: str
    district: str
    residential_complex: str

    house_type: str
    condition: str
    bathroom: str

    rooms: int
    area: float
    floor: int
    total_floors: int

    ceiling_height: float
    year_built: int