'use client';

import React, { useState, useEffect, useRef } from 'react';

interface NumberInputProps {
  label: string;
  value: number | null;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  stepPrecision?: number;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
}

export const NumberInput = ({
  label,
  value,
  onChange,
  min = 0,
  max = 1000,
  step = 1,
  stepPrecision = 0,
  placeholder,
  required,
  disabled = false,
}: NumberInputProps) => {
  const [localValue, setLocalValue] = useState<string>(value === null ? '' : value.toString());
  const isInternalChange = useRef(false);

  const roundToPrecision = (num: number): number => {
    if (stepPrecision === 0) return Math.round(num);
    const factor = Math.pow(10, stepPrecision);
    return Math.round(num * factor) / factor;
  };

  useEffect(() => {
    if (!isInternalChange.current) {
      setLocalValue(value === null ? '' : value.toString());
    }
    isInternalChange.current = false;
  }, [value]);

  const handleIncrement = () => {
    if (disabled) return;
    const currentValue = value ?? min;
    let newValue = currentValue + step;
    newValue = roundToPrecision(newValue);
    if (newValue <= max) {
      isInternalChange.current = true;
      onChange(newValue);
      setLocalValue(newValue.toString());
    }
  };

  const handleDecrement = () => {
    if (disabled) return;
    const currentValue = value ?? min;
    let newValue = currentValue - step;
    newValue = roundToPrecision(newValue);
    if (newValue >= min) {
      isInternalChange.current = true;
      onChange(newValue);
      setLocalValue(newValue.toString());
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let rawValue = e.target.value;
    
    rawValue = rawValue.replace(',', '.');
    
    if (stepPrecision > 0 && rawValue.includes('.')) {
      const parts = rawValue.split('.');
      if (parts[1] && parts[1].length > stepPrecision) {
        parts[1] = parts[1].slice(0, stepPrecision);
        rawValue = parts.join('.');
      }
    }
    
    setLocalValue(rawValue);
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    if (disabled) return;
    let rawValue = e.target.value;
    
    rawValue = rawValue.replace(',', '.');
    
    if (rawValue === '') {
      isInternalChange.current = true;
      onChange(min);
      setLocalValue(min.toString());
      return;
    }
    
    let numValue = parseFloat(rawValue);
    if (!isNaN(numValue)) {
      numValue = roundToPrecision(numValue);
      
      let clampedValue = numValue;
      if (clampedValue < min) clampedValue = min;
      if (clampedValue > max) clampedValue = max;
      clampedValue = roundToPrecision(clampedValue);
      
      isInternalChange.current = true;
      onChange(clampedValue);
      
      let displayValue = clampedValue.toString();
      if (stepPrecision > 0) {
        displayValue = clampedValue.toFixed(stepPrecision);
      }
      setLocalValue(displayValue);
    } else {
      const syncValue = value === null ? '' : (stepPrecision > 0 ? value.toFixed(stepPrecision) : value.toString());
      setLocalValue(syncValue);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur();
    }
  };

  return (
    <div className="number-input-group">
      <label className="number-input-label">
        {label}
        {required && <span className="required">*</span>}
      </label>
      <div className="number-input-wrapper">
        <input
          type="text"
          inputMode={stepPrecision > 0 ? "decimal" : "numeric"}
          pattern={stepPrecision > 0 ? "[0-9]*[.,]?[0-9]*" : "[0-9]*"}
          className="number-input"
          value={localValue}
          onChange={handleInputChange}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
        />
        <div className="number-input-buttons">
          <button
            type="button"
            className="number-input-btn"
            onClick={handleIncrement}
            disabled={disabled || (value ?? min) >= max}
          >
            +
          </button>
          <button
            type="button"
            className="number-input-btn"
            onClick={handleDecrement}
            disabled={disabled || (value ?? min) <= min}
          >
            −
          </button>
        </div>
      </div>
    </div>
  );
};