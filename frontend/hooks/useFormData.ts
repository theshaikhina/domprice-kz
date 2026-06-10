import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '@/lib/api';

interface UseFormDataReturn {
  cities: { value: string; label: string }[];
  districts: { value: string; label: string }[];
  residentialComplexes: { value: string; label: string }[];
  houseTypes: { value: string; label: string }[];
  conditions: { value: string; label: string }[];
  bathrooms: { value: string; label: string }[];
  isLoadingCities: boolean;
  isLoadingDistricts: boolean;
  isLoadingComplexes: boolean;
  loadDistricts: (city: string) => Promise<void>;
  loadResidentialComplexes: (city: string, district: string) => Promise<void>;
}

export const useFormData = (): UseFormDataReturn => {
  const [cities, setCities] = useState<{ value: string; label: string }[]>([]);
  const [districts, setDistricts] = useState<{ value: string; label: string }[]>([]);
  const [residentialComplexes, setResidentialComplexes] = useState<{ value: string; label: string }[]>([]);
  const [houseTypes, setHouseTypes] = useState<{ value: string; label: string }[]>([]);
  const [conditions, setConditions] = useState<{ value: string; label: string }[]>([]);
  const [bathrooms, setBathrooms] = useState<{ value: string; label: string }[]>([]);
  
  const [isLoadingDistricts, setIsLoadingDistricts] = useState(false);
  const [isLoadingComplexes, setIsLoadingComplexes] = useState(false);
  
  const staticDataLoaded = useRef(false);

  useEffect(() => {
    if (staticDataLoaded.current) return;
    staticDataLoaded.current = true;
    
    const loadStaticData = async () => {
      const [citiesData, houseTypesData, conditionsData, bathroomsData] = await Promise.all([
        api.getCities(),
        api.getHouseTypes(),
        api.getConditions(),
        api.getBathrooms(),
      ]);
      setCities(citiesData);
      setHouseTypes(houseTypesData);
      setConditions(conditionsData);
      setBathrooms(bathroomsData);
    };
    
    loadStaticData();
  }, []);

  const loadDistricts = useCallback(async (city: string) => {
    if (!city) {
      setDistricts([]);
      return;
    }
    setIsLoadingDistricts(true);
    const districtsData = await api.getDistricts(city);
    setDistricts(districtsData);
    setIsLoadingDistricts(false);
  }, []);

  const loadResidentialComplexes = useCallback(async (city: string, district: string) => {
    if (!city || !district) {
      setResidentialComplexes([]);
      return;
    }
    setIsLoadingComplexes(true);
    const complexesData = await api.getResidentialComplexes(city, district);
    setResidentialComplexes(complexesData);
    setIsLoadingComplexes(false);
  }, []);

  return {
    cities,
    districts,
    residentialComplexes,
    houseTypes,
    conditions,
    bathrooms,
    isLoadingCities: false,
    isLoadingDistricts,
    isLoadingComplexes,
    loadDistricts,
    loadResidentialComplexes,
  };
};