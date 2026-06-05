# 🏠 DomPrice — Apartment Valuation Platform for Kazakhstan

A machine learning project for estimating apartment prices in Kazakhstan based on real estate listings.

The model predicts the price per square meter using apartment characteristics, building features, and geographic information.

---

## 🎯 Objective

The goal of this project is to build a machine learning model for residential property valuation and investigate the factors that influence housing prices.

Main objectives:

* predict apartment price per square meter;
* analyze the impact of location on property value;
* evaluate the contribution of geographic and textual features;
* develop an API for model inference.

---

## 📊 Dataset

The dataset consists of apartment sale listings collected from the Kazakhstan real estate market.

Main features include:

* city;
* district;
* residential complex;
* apartment area;
* number of rooms;
* floor;
* total floors in the building;
* building type;
* apartment condition;
* ceiling height;
* building age;
* property description;
* geographic coordinates.

---

## ⚙️ Feature Engineering

Several additional features were created.

### Building Features

* `house_age`
* `floor_ratio`
* `is_first_floor`
* `is_last_floor`

### Text Features

* `description_len`

### Geographic Features

* `latitude`
* `longitude`
* `coordinates_found`

For a subset of properties, coordinates were recovered through address geocoding.

---

## 🤖 Model

Model used:

* CatBoost Regressor

Target variable:

```python
price_per_m2
```

To stabilize the target distribution, logarithmic transformation was applied:

```python
y = np.log1p(price_per_m2)
```

---

## 📈 Results

Best model performance:

| Metric |   Value |
| ------ | ------: |
| MAPE   |  11.20% |
| MAE    |  80,354 |
| RMSE   | 115,716 |

---

## 🔍 Key Findings

### Location is a critical factor

After adding geographic coordinates:

```text
RMSE:
118,766 → 115,716
```

Latitude and longitude became some of the most important features in the model.

### Coordinates do not replace district information

Experiments showed that:

```text
district + lat/lon > lat/lon
```

District information captures additional factors such as neighborhood prestige and local infrastructure.

### Premium properties are harder to predict

Most prediction errors are concentrated in high-end apartments located in premium areas of Almaty.

---

## 📁 Project Structure

```text
Prediction_pr_KZ/
│
├── api/
├── data/
├── models/
├── notebooks/
├── reports/
├── src/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🚀 Model Training

```bash
python -m src.train
```

---

## 🌐 Run API

```bash
uvicorn api.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## 🛠️ Tech Stack

* Python
* Pandas
* NumPy
* Scikit-Learn
* CatBoost
* MLflow
* FastAPI
* Geopy

---

## 🔮 Future Improvements

* residential complex class estimation;
* additional geocoding coverage;
* infrastructure-based features;
* distance to city center;
* ensemble models (CatBoost + LightGBM + XGBoost);
* full-featured frontend application.
