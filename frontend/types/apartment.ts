export interface ApartmentFeatures {
  city: string;
  district: string;
  residential_complex: string;
  house_type: string;
  condition: string;
  bathroom: string;
  rooms: number | null;
  area: number | null;
  floor: number | null;
  total_floors: number | null;
  ceiling_height: number | null;
  year_built: number | null;
}

export interface PredictionResponse {
  price: number;
  price_per_m2: number;
  min_price: number;
  max_price: number;
  mape: number;
}

export interface Option {
  value: string;
  label: string;
}