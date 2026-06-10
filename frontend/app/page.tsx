'use client';

import { useState } from 'react';
import { ApartmentForm } from '@/components/forms/ApartmentForm';
import { PriceDisplay } from '@/components/PriceDisplay';
import { ApartmentFeatures, PredictionResponse } from '@/types/apartment';
import { api } from '@/lib/api';

import {
  Building2,
  SlidersHorizontal,
  BadgeDollarSign,
  TrendingUp,
} from 'lucide-react';

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
        <div className="header-top">
          <div className="logo">
            <Building2 size={32} />
            <h1>DomPrice</h1>
          </div>

          {result && (
            <div className="accuracy-card">
              <div className="icon-box">
                <TrendingUp size={32} />
              </div>
              <div className="accuracy-info">
                <div className="accuracy-header">Точность модели (MAPE)</div>
                <div className="accuracy-value">{result.mape}%</div>
              </div>
            </div>
          )}
        </div>
        <div className="subtitle">
          Оценка рыночной стоимости квартиры в Казахстане
        </div>
      </div>

      <div className="main-layout">
        <div className="card">
          <div className="card-title">
            <div className="icon-box">
              <SlidersHorizontal size={20} />
            </div>
            <span>Параметры квартиры</span>
          </div>

          <div className="card-subtitle">
            Заполните характеристики объекта
          </div>

          <ApartmentForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
          />
        </div>

        <div className="card">
          <div className="card-title">
            <div className="icon-box">
              <BadgeDollarSign size={20} />
            </div>
            <span>Результат оценки</span>
          </div>

          {error ? (
            <div
              className="result-placeholder"
              style={{ color: '#EF4444' }}
            >
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