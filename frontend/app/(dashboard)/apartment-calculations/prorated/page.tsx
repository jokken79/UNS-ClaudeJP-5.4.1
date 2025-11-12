'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import api from '@/lib/api';
import {
  ArrowLeftIcon,
  CalculatorIcon,
  CalendarIcon,
  CurrencyYenIcon,
  BuildingOfficeIcon,
  InformationCircleIcon,
} from '@heroicons/react/24/outline';

interface ProratedCalculationForm {
  apartment_id: number | '';
  start_date: string;
  end_date: string;
  daily_rate: number | '';
}

interface Apartment {
  id: number;
  apartment_code: string;
  address: string;
  monthly_rent: number;
  capacity: number;
  employees_count: number;
}

interface ProratedResult {
  apartment: Apartment;
  total_days: number;
  occupied_days: number;
  daily_rate: number;
  base_amount: number;
  calculated_amount: number;
  percentage: number;
  breakdown: {
    description: string;
    amount: number;
  }[];
}

export default function ProratedCalculationPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [form, setForm] = useState<ProratedCalculationForm>({
    apartment_id: '',
    start_date: new Date().toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    daily_rate: '',
  });
  const [result, setResult] = useState<ProratedResult | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Fetch apartments
  const { data: apartments = [] } = useQuery({
    queryKey: ['apartments'],
    queryFn: async () => {
      const response = await api.get('/apartments-v2/apartments');
      return response.data as Apartment[];
    },
  });

  // Calculate prorated mutation
  const calculateMutation = useMutation({
    mutationFn: async (data: ProratedCalculationForm) => {
      const response = await api.post('/apartment-calculations/prorated', {
        apartment_id: Number(data.apartment_id),
        start_date: data.start_date,
        end_date: data.end_date,
        daily_rate: data.daily_rate ? Number(data.daily_rate) : undefined,
      });
      return response.data as ProratedResult;
    },
    onSuccess: (data) => {
      setResult(data);
    },
    onError: (error: any) => {
      if (error.response?.data?.detail) {
        setErrors({ general: error.response.data.detail });
      }
    },
  });

  const handleChange = (field: keyof ProratedCalculationForm, value: string | number) => {
    setForm(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  // Auto-calculate daily rate when apartment changes
  const selectedApartment = apartments.find(a => a.id === form.apartment_id);
  React.useEffect(() => {
    if (selectedApartment && !form.daily_rate) {
      const daily = selectedApartment.monthly_rent / 30;
      setForm(prev => ({ ...prev, daily_rate: daily }));
    }
  }, [selectedApartment, form.daily_rate]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setResult(null);

    const newErrors: Record<string, string> = {};
    if (!form.apartment_id) newErrors.apartment_id = 'Debes seleccionar un apartamento';
    if (!form.start_date) newErrors.start_date = 'La fecha de inicio es requerida';
    if (!form.end_date) newErrors.end_date = 'La fecha de fin es requerida';
    if (form.start_date && form.end_date && form.start_date > form.end_date) {
      newErrors.end_date = 'La fecha de fin debe ser posterior a la de inicio';
    }
    if (form.daily_rate && Number(form.daily_rate) <= 0) {
      newErrors.daily_rate = 'La tarifa diaria debe ser mayor a 0';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    calculateMutation.mutate(form);
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => router.back()}
          className="p-2 hover:bg-accent rounded-lg transition-colors"
        >
          <ArrowLeftIcon className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-3xl font-bold">Cálculo de Prorrateo</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Calcula la renta proporcional por días de ocupación
          </p>
        </div>
      </div>

      {/* Info Box */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-3">
          <InformationCircleIcon className="h-6 w-6 text-blue-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-blue-800">¿Qué es el prorrateo?</h3>
            <p className="text-sm text-blue-700 mt-1">
              El prorrateo calcula la renta proporcional basada en los días reales de ocupación
              en un período determinado. Fórmula: (Renta Mensual ÷ 30) × Días Ocupados
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="bg-card border rounded-lg p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {errors.general && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {errors.general}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Apartment Selection */}
            <div>
              <label className="block text-sm font-medium mb-2">
                <BuildingOfficeIcon className="inline h-4 w-4 mr-1" />
                Apartamento *
              </label>
              <select
                value={form.apartment_id}
                onChange={(e) => handleChange('apartment_id', e.target.value ? Number(e.target.value) : '')}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  errors.apartment_id ? 'border-red-500' : ''
                }`}
              >
                <option value="">Seleccionar apartamento</option>
                {apartments.map((apartment) => (
                  <option key={apartment.id} value={apartment.id}>
                    {apartment.apartment_code} - {apartment.address}
                  </option>
                ))}
              </select>
              {errors.apartment_id && (
                <p className="text-sm text-red-500 mt-1">{errors.apartment_id}</p>
              )}
            </div>

            {/* Daily Rate */}
            <div>
              <label className="block text-sm font-medium mb-2">
                <CurrencyYenIcon className="inline h-4 w-4 mr-1" />
                Tarifa Diaria (¥) *
              </label>
              <input
                type="number"
                value={form.daily_rate}
                onChange={(e) => handleChange('daily_rate', e.target.value ? Number(e.target.value) : '')}
                placeholder="Ej: 1666"
                min="0"
                step="0.01"
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  errors.daily_rate ? 'border-red-500' : ''
                }`}
              />
              {errors.daily_rate && (
                <p className="text-sm text-red-500 mt-1">{errors.daily_rate}</p>
              )}
              {selectedApartment && (
                <p className="text-xs text-muted-foreground mt-1">
                  Renta mensual: ¥{selectedApartment.monthly_rent.toLocaleString()} (¥{Math.round(selectedApartment.monthly_rent / 30).toLocaleString()}/día)
                </p>
              )}
            </div>

            {/* Start Date */}
            <div>
              <label className="block text-sm font-medium mb-2">
                <CalendarIcon className="inline h-4 w-4 mr-1" />
                Fecha de Inicio *
              </label>
              <input
                type="date"
                value={form.start_date}
                onChange={(e) => handleChange('start_date', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  errors.start_date ? 'border-red-500' : ''
                }`}
              />
              {errors.start_date && (
                <p className="text-sm text-red-500 mt-1">{errors.start_date}</p>
              )}
            </div>

            {/* End Date */}
            <div>
              <label className="block text-sm font-medium mb-2">
                <CalendarIcon className="inline h-4 w-4 mr-1" />
                Fecha de Fin *
              </label>
              <input
                type="date"
                value={form.end_date}
                onChange={(e) => handleChange('end_date', e.target.value)}
                min={form.start_date}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  errors.end_date ? 'border-red-500' : ''
                }`}
              />
              {errors.end_date && (
                <p className="text-sm text-red-500 mt-1">{errors.end_date}</p>
              )}
            </div>
          </div>

          {/* Days Preview */}
          {form.start_date && form.end_date && form.start_date <= form.end_date && (
            <div className="p-4 bg-muted rounded-lg">
              <p className="text-sm font-medium">
                Período: {Math.floor(
                  (new Date(form.end_date).getTime() - new Date(form.start_date).getTime()) /
                    (1000 * 60 * 60 * 24)
                ) + 1} días
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-3 pt-4 border-t">
            <button
              type="submit"
              disabled={calculateMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              <CalculatorIcon className="h-5 w-5" />
              {calculateMutation.isPending ? 'Calculando...' : 'Calcular Prorrateo'}
            </button>
          </div>
        </form>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Result Card */}
          <div className="bg-card border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Resultado del Cálculo</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">Apartamento</p>
                  <p className="font-medium">{result.apartment.apartment_code}</p>
                  <p className="text-sm text-muted-foreground">{result.apartment.address}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Días</p>
                    <p className="text-2xl font-bold">{result.total_days}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Días Ocupados</p>
                    <p className="text-2xl font-bold text-green-600">{result.occupied_days}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Tarifa Diaria</p>
                    <p className="text-lg font-medium">¥{result.daily_rate.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Porcentaje</p>
                    <p className="text-lg font-medium">{result.percentage.toFixed(1)}%</p>
                  </div>
                </div>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                <p className="text-sm text-green-700 mb-2">Monto a Cobrar</p>
                <p className="text-4xl font-bold text-green-800">
                  ¥{result.calculated_amount.toLocaleString()}
                </p>
                <p className="text-sm text-green-600 mt-2">
                  De ¥{result.base_amount.toLocaleString()} (100%)
                </p>
              </div>
            </div>

            {/* Breakdown */}
            <div className="mt-6 pt-6 border-t">
              <h3 className="font-semibold mb-3">Desglose del Cálculo</h3>
              <div className="space-y-2 text-sm">
                {result.breakdown.map((item, index) => (
                  <div key={index} className="flex justify-between">
                    <span className="text-muted-foreground">{item.description}</span>
                    <span className="font-medium">¥{item.amount.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <button
              onClick={() => {
                try {
                  const calculationRecord = {
                    id: Date.now(),
                    timestamp: new Date().toISOString(),
                    type: 'prorated',
                    form: {
                      apartment_id: form.apartment_id,
                      start_date: form.start_date,
                      end_date: form.end_date,
                      daily_rate: form.daily_rate,
                    },
                    result: {
                      apartment: result.apartment,
                      total_days: result.total_days,
                      occupied_days: result.occupied_days,
                      daily_rate: result.daily_rate,
                      base_amount: result.base_amount,
                      calculated_amount: result.calculated_amount,
                      percentage: result.percentage,
                      breakdown: result.breakdown,
                    },
                  };

                  const saved = JSON.parse(localStorage.getItem('apartment_calculations') || '[]');
                  saved.push(calculationRecord);
                  localStorage.setItem('apartment_calculations', JSON.stringify(saved));

                  toast.success('計算結果を保存しました');
                } catch (error) {
                  console.error('Error saving calculation:', error);
                  toast.error('保存に失敗しました');
                }
              }}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Guardar Cálculo
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
