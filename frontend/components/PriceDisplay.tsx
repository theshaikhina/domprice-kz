'use client';

import { PredictionResponse } from '@/types/apartment';
import {
  TrendingUp,
  Shield,
} from 'lucide-react';

interface PriceDisplayProps {
  result: PredictionResponse | null;
}

export const PriceDisplay = ({ result }: PriceDisplayProps) => {
  if (!result) {
    return (
      <div className="result-placeholder">
        <div>
          <p style={{ fontSize: '1.125rem', marginBottom: '0.5rem' }}>Введите параметры квартиры</p>
          <p style={{ fontSize: '0.875rem' }}>и нажмите «Рассчитать стоимость» для получения прогноза</p>
        </div>
      </div>
    );
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-KZ').format(Math.round(price));
  };

  const formatMillions = (price: number) => {
    return (price / 1000000).toFixed(1);
  };

  return (
    <div className="result-content">
      <div className="price-main">
        <div className="price-label">Оценочная стоимость квартиры</div>
        <div className="price-value">{formatPrice(result.price)} ₸</div>
      </div>
      
      <div className="price-per-meter">
        <div className="label">Цена за квадратный метр</div>
        <div className="value">{formatPrice(result.price_per_m2)} ₸ / м²</div>
      </div>
      
      <div className="range-card">
        <div className="range-header">
          <TrendingUp size={32} />
          <div className="range-title">Ориентировочный диапазон стоимости</div>
        </div>
        <div className="range-values">
          <span className="range-min">{formatMillions(result.min_price)} млн ₸</span>
          <span className="range-dash">—</span>
          <span className="range-max">{formatMillions(result.max_price)} млн ₸</span>
        </div>
        <div className="range-bar">
          <div 
            className="range-fill" 
            style={{ 
              left: '0%', 
              width: '100%' 
            }}
          />
        </div>
        <div className="range-percent">
          <span className="negative">-{result.mape}%</span>
          <span>Оценка модели</span>
          <span className="positive">+{result.mape}%</span>
        </div>
        <div className="range-note">
          Диапазон рассчитан с учетом ошибки (MAPE {result.mape}%)
        </div>
      </div>
      
      <div className="info-card">
        <div className="info-header">
          <div className="icon-box">
            <Shield size={20} />
          </div>
          <div className="info-title">Важно</div>
        </div>
        <div className="info-text">
          Это предварительная оценка, полученная с помощью ML-модели.
          Фактическая стоимость может отличаться в зависимости от деталей объявления и рыночной ситуации.
        </div>
      </div>
    </div>
  );
};