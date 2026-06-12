import { ApartmentFeatures, PredictionResponse } from '@/types/apartment';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  'https://domprice-kz-production.up.railway.app';

export type Option = {
  value: string;
  label: string;
};

type ApiResponse<T> = T | { [key: string]: T };

function extractArray<T>(data: ApiResponse<T[]>, key: string): T[] {
  if (Array.isArray(data)) return data;

  if (data && typeof data === 'object' && key in data) {
    const value = (data as Record<string, T[]>)[key];
    if (Array.isArray(value)) return value;
  }

  return [];
}

export const api = {
  async getCities(lang: string = 'ru'): Promise<Option[]> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/options/cities?lang=${encodeURIComponent(lang)}`
      );
      const data = await response.json();
      return extractArray<Option>(data, 'cities');
    } catch (error) {
      console.error('Error fetching cities:', error);
      return [];
    }
  },

  async getDistricts(city: string, lang: string = 'ru'): Promise<Option[]> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/options/districts?city=${encodeURIComponent(
          city
        )}&lang=${encodeURIComponent(lang)}`
      );
      const data = await response.json();
      return extractArray<Option>(data, 'districts');
    } catch (error) {
      console.error('Error fetching districts:', error);
      return [];
    }
  },

  async getResidentialComplexes(
    city: string,
    district: string,
    lang: string = 'ru'
  ): Promise<Option[]> {
    try {
      let url = `${API_BASE_URL}/options/residential-complexes?city=${encodeURIComponent(
        city
      )}&lang=${encodeURIComponent(lang)}`;

      if (district) {
        url += `&district=${encodeURIComponent(district)}`;
      }

      const response = await fetch(url);
      const data = await response.json();

      return extractArray<Option>(data, 'residential_complexes');
    } catch (error) {
      console.error('Error fetching residential complexes:', error);
      return [];
    }
  },

  async getHouseTypes(lang: string = 'ru'): Promise<Option[]> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/options/house-types?lang=${encodeURIComponent(lang)}`
      );
      const data = await response.json();

      return extractArray<Option>(data, 'house_types');
    } catch (error) {
      console.error('Error fetching house types:', error);
      return [];
    }
  },

  async getConditions(lang: string = 'ru'): Promise<Option[]> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/options/conditions?lang=${encodeURIComponent(lang)}`
      );
      const data = await response.json();

      return extractArray<Option>(data, 'conditions');
    } catch (error) {
      console.error('Error fetching conditions:', error);
      return [];
    }
  },

  async getBathrooms(lang: string = 'ru'): Promise<Option[]> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/options/bathrooms?lang=${encodeURIComponent(lang)}`
      );
      const data = await response.json();

      return extractArray<Option>(data, 'bathrooms');
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