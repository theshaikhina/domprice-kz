import { ApartmentFeatures, PredictionResponse } from '@/types/apartment';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://domprice-kz-production.up.railway.app';

const formatOptionLabel = (value: string): string => {
  if (!value || value === 'unknown') return 'Другое';
  if (value === 'unknown район') return 'Другой район';
  if (value === 'unknown ЖК') return 'Другой';
  return value;
};

type ApiResponse<T> = T | { [key: string]: T[] };

function extractArray<T>(data: ApiResponse<T[]>, key: string): T[] {
  if (Array.isArray(data)) return data;
  if (data && typeof data === 'object' && key in data) {
    const value = (data as Record<string, T[]>)[key];
    if (Array.isArray(value)) return value;
  }
  return [];
}

export const api = {
  async getCities(): Promise<{ value: string; label: string }[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/options/cities`);
      const data = await response.json();
      const cities = extractArray<string>(data, 'cities');
      return cities.map((city: string) => ({
        value: city,
        label: formatOptionLabel(city),
      }));
    } catch (error) {
      console.error('Error fetching cities:', error);
      return [];
    }
  },

  async getDistricts(city: string): Promise<{ value: string; label: string }[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/options/districts?city=${encodeURIComponent(city)}`);
      const data = await response.json();
      const districts = extractArray<string>(data, 'districts');
      return districts.map((district: string) => ({
        value: district,
        label: formatOptionLabel(district),
      }));
    } catch (error) {
      console.error('Error fetching districts:', error);
      return [];
    }
  },

  async getResidentialComplexes(city: string, district: string): Promise<{ value: string; label: string }[]> {
    try {
      let url = `${API_BASE_URL}/options/residential-complexes?city=${encodeURIComponent(city)}`;
      if (district) {
        url += `&district=${encodeURIComponent(district)}`;
      }
      const response = await fetch(url);
      const data = await response.json();
      const complexes = extractArray<string>(data, 'residential_complexes');
      return complexes.map((complex: string) => ({
        value: complex,
        label: formatOptionLabel(complex),
      }));
    } catch (error) {
      console.error('Error fetching residential complexes:', error);
      return [];
    }
  },

  async getHouseTypes(): Promise<{ value: string; label: string }[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/options/house-types`);
      const data = await response.json();
      const houseTypes = extractArray<string>(data, 'house_types');
      return houseTypes.map((type: string) => ({
        value: type,
        label: formatOptionLabel(type),
      }));
    } catch (error) {
      console.error('Error fetching house types:', error);
      return [];
    }
  },

  async getConditions(): Promise<{ value: string; label: string }[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/options/conditions`);
      const data = await response.json();
      const conditions = extractArray<string>(data, 'conditions');
      return conditions.map((condition: string) => ({
        value: condition,
        label: formatOptionLabel(condition),
      }));
    } catch (error) {
      console.error('Error fetching conditions:', error);
      return [];
    }
  },

  async getBathrooms(): Promise<{ value: string; label: string }[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/options/bathrooms`);
      const data = await response.json();
      const bathrooms = extractArray<string>(data, 'bathrooms');
      return bathrooms.map((bathroom: string) => ({
        value: bathroom,
        label: formatOptionLabel(bathroom),
      }));
    } catch (error) {
      console.error('Error fetching bathrooms:', error);
      return [];
    }
  },

  async predict(data: ApartmentFeatures): Promise<PredictionResponse> {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Ошибка при получении прогноза');
    }

    const result = await response.json();
    
    return {
      price: result.price,
      price_per_m2: result.price_per_m2,
      min_price: result.min_price,
      max_price: result.max_price,
      mape: result.mape || 11.2,
    };
  },
};