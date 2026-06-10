'use client';

import { useState, useEffect } from 'react';
import { Select } from '@/components/ui/Select';
import { NumberInput } from '@/components/ui/NumberInput';
import { ApartmentFeatures } from '@/types/apartment';
import { useFormData } from '@/hooks/useFormData';

interface ApartmentFormProps {
  onSubmit: (data: ApartmentFeatures) => void;
  isLoading: boolean;
}

export const ApartmentForm = ({ onSubmit, isLoading }: ApartmentFormProps) => {
  const {
    cities,
    districts,
    residentialComplexes,
    houseTypes,
    conditions,
    bathrooms,
    isLoadingCities,
    isLoadingDistricts,
    isLoadingComplexes,
    loadDistricts,
    loadResidentialComplexes,
  } = useFormData();

  const [formData, setFormData] = useState<ApartmentFeatures>({
  city: '',
  district: '',
  residential_complex: '',
  house_type: '',
  condition: '',
  bathroom: '',
  rooms: null,
  area: null,
  floor: null,
  total_floors: null,
  ceiling_height: null,
  year_built: null,
});

  useEffect(() => {
    if (formData.city) {
      loadDistricts(formData.city);
    }
  }, [formData.city, loadDistricts]);

  useEffect(() => {
    if (formData.city && formData.district) {
      loadResidentialComplexes(formData.city, formData.district);
    }
  }, [formData.city, formData.district, loadResidentialComplexes]);

  const handleSelectChange = (field: keyof ApartmentFeatures, value: string) => {
    setFormData((prev) => {
      const newData = { ...prev, [field]: value };
      
      if (field === 'city') {
        newData.district = '';
        newData.residential_complex = '';
      }
      
      if (field === 'district') {
        newData.residential_complex = '';
      }
      
      return newData;
    });
  };

  const handleNumberChange = (field: keyof ApartmentFeatures, value: number) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const requiredFields: (keyof ApartmentFeatures)[] = [
      'city', 'district', 'residential_complex', 'house_type', 'condition', 'bathroom'
    ];
    
    const numberFields: (keyof ApartmentFeatures)[] = [
      'rooms', 'area', 'floor', 'total_floors', 'ceiling_height', 'year_built'
    ];
    
    const isAllSelectsFilled = requiredFields.every(field => formData[field] !== '');
    const isAllNumbersValid = numberFields.every(field => {
      const value = formData[field] as number;
      return value > 0;
    });
    
    if (!isAllSelectsFilled || !isAllNumbersValid) {
      alert('Пожалуйста, заполните все поля формы');
      return;
    }
    
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-grid">
        <Select
          label="Город"
          options={cities}
          value={formData.city}
          onChange={(e) => handleSelectChange('city', e.target.value)}
          required
          disabled={isLoadingCities}
        />
        
        <NumberInput
          label="Количество комнат"
          value={formData.rooms}
          onChange={(value) => handleNumberChange('rooms', value)}
          min={0}
          max={20}
          step={1}
          placeholder="Например, 3"
          required
        />
        
        <Select
          label="Район"
          options={districts}
          value={formData.district}
          onChange={(e) => handleSelectChange('district', e.target.value)}
          required
          disabled={!formData.city || isLoadingDistricts}
        />
        
        <NumberInput
          label="Площадь, м²"
          value={formData.area}
          onChange={(value) => handleNumberChange('area', value)}
          min={0}
          max={1000}
          step={0.1}
          stepPrecision={1}
          placeholder="Например, 75.5"
          required
        />
        
        <Select
          label="Жилой комплекс"
          options={residentialComplexes}
          value={formData.residential_complex}
          onChange={(e) => handleSelectChange('residential_complex', e.target.value)}
          required
          disabled={!formData.district || isLoadingComplexes}
        />

        <NumberInput
          label="Этажность дома"
          value={formData.total_floors}
          onChange={(value) => handleNumberChange('total_floors', value)}
          min={1}
          max={50}
          step={1}
          placeholder="Например, 16"
          required
        />
        
        <Select
          label="Тип дома"
          options={houseTypes}
          value={formData.house_type}
          onChange={(e) => handleSelectChange('house_type', e.target.value)}
          required
        />
        
        <NumberInput
          label="Этаж"
          value={formData.floor}
          onChange={(value) => handleNumberChange('floor', value)}
          min={1}
          max={formData.total_floors || 100}
          step={1}
          placeholder="Например, 5"
          required
        />
        
        <Select
          label="Состояние"
          options={conditions}
          value={formData.condition}
          onChange={(e) => handleSelectChange('condition', e.target.value)}
          required
        />
        
        <NumberInput
          label="Высота потолков, м"
          value={formData.ceiling_height}
          onChange={(value) => handleNumberChange('ceiling_height', value)}
          min={1}
          max={5}
          step={0.1}
          stepPrecision={1}
          placeholder="Например, 3.0"
          required
        />
        
        <Select
          label="Санузел"
          options={bathrooms}
          value={formData.bathroom}
          onChange={(e) => handleSelectChange('bathroom', e.target.value)}
          required
        />
        
        <NumberInput
          label="Год постройки"
          value={formData.year_built}
          onChange={(value) => handleNumberChange('year_built', value)}
          min={1500}
          max={2026}
          step={1}
          placeholder="Например, 2020"
          required
        />
      </div>
      
      <button type="submit" className="submit-btn" disabled={isLoading}>
        {isLoading ? <span className="loader"></span> : 'Рассчитать стоимость'}
      </button>
    </form>
  );
};