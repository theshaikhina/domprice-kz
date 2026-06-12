from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

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
    allow_origins=[
        "https://domprice-kz.vercel.app",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://domprice-kz-production.up.railway.app",
    ],
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
def get_cities(lang: str = "ru"):
    column = "city_en" if lang == "en" else "city"

    return {
        "cities": get_unique_values(
            value_column="city",
            label_column=column,
        )
    }


@app.get("/options/districts")
def get_districts(city: str, lang: str = "ru"):
    label_column = "district_en" if lang == "en" else "district"

    return {
        "city": city,
        "districts": get_districts_by_city(
            city=city,
            value_column="district",
            label_column=label_column,
        )
    }


@app.get("/options/residential-complexes")
def get_complexes(
    city: str,
    district: Optional[str] = None,
    lang: str = "ru",
):
    label_column = (
        "residential_complex_en"
        if lang == "en"
        else "residential_complex"
    )

    return {
        "city": city,
        "district": district,
        "residential_complexes": get_residential_complexes(
            city=city,
            district=district,
            value_column="residential_complex",
            label_column=label_column,
        )
    }


@app.get("/options/house-types")
def get_house_types(lang: str = "ru"):
    label_column = "house_type_en" if lang == "en" else "house_type"

    options = get_unique_values(
        value_column="house_type",
        label_column=label_column,
        unknown_label="Other" if lang == "en" else "Другое",
    )

    options = [
        option for option in options
        if option["value"] != "unknown"
    ]

    return {
        "house_types": options
    }


@app.get("/options/conditions")
def get_conditions(lang: str = "ru"):
    label_column = "condition_en" if lang == "en" else "condition"
    unknown_label = "Other" if lang == "en" else "Другое"

    return {
        "conditions": get_unique_values(
            value_column="condition",
            label_column=label_column,
            unknown_label=unknown_label,
        )
    }


@app.get("/options/bathrooms")
def get_bathrooms(lang: str = "ru"):
    label_column = "bathroom_en" if lang == "en" else "bathroom"
    unknown_label = "Other" if lang == "en" else "Другое"
    return {
        "bathrooms": get_unique_values(
            value_column="bathroom",
            label_column=label_column,
            unknown_label=unknown_label,
        )
    }