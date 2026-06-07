'use client';

import { useState } from 'react';
import { ApartmentForm } from '@/components/forms/ApartmentForm';
import { PriceDisplay } from '@/components/PriceDisplay';
import { ApartmentFeatures, PredictionResponse } from '@/types/apartment';
import { api } from '@/lib/api';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: ApartmentFeatures) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const prediction = await api.predict(data);
      setResult(prediction);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="header">
        <div className="logo">
          <span className="logo-icon">🏠</span>
          <h1>DomPrice</h1>
        </div>
        <div className="subtitle">Оценка рыночной стоимости квартиры в Казахстане</div>
      </div>
      
      <div className="main-layout">
        <div className="card">
          <div className="card-title">Параметры квартиры</div>
          <div className="card-subtitle">Заполните характеристики объекта</div>
          <ApartmentForm onSubmit={handleSubmit} isLoading={isLoading} />
        </div>
        
        <div className="card">
          <div className="card-title">Результат оценки</div>
          {error ? (
            <div className="result-placeholder" style={{ color: '#EF4444' }}>
              <p>{error}</p>
            </div>
          ) : (
            <PriceDisplay result={result} />
          )}
        </div>
      </div>
    </div>
  );
}