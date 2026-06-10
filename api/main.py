from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
def get_complexes(city: str, district: Optional[str] = None
):
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