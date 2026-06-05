from fastapi import FastAPI

from api.schemas import ApartmentInput
from src.predict import (
    predict_price,
    get_unique_values,
    get_districts_by_city,
    get_residential_complexes,
)


app = FastAPI(
    title="Krisha KZ Apartment Price Prediction API",
    description="API для предсказания стоимости квартир в Казахстане",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Krisha KZ price prediction API is running"
    }


@app.post("/predict")
def predict(apartment: ApartmentInput):
    result = predict_price(apartment.dict())
    return result


@app.get("/options/cities")
def get_cities():
    return {
        "cities": get_unique_values("city")
    }


@app.get("/options/districts")
def get_districts(city: str):
    return {
        "city": city,
        "districts": get_districts_by_city(city)
    }


@app.get("/options/residential-complexes")
def get_complexes(city: str, district: str | None = None):
    return {
        "city": city,
        "district": district,
        "residential_complexes": get_residential_complexes(
            city=city,
            district=district,
        )
    }


@app.get("/options/house-types")
def get_house_types():
    return {
        "house_types": get_unique_values("house_type")
    }


@app.get("/options/conditions")
def get_conditions():
    return {
        "conditions": get_unique_values("condition")
    }


@app.get("/options/bathrooms")
def get_bathrooms():
    return {
        "bathrooms": get_unique_values("bathroom")
    }