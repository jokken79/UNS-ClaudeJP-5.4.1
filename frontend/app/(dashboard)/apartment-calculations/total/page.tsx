'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import api from '@/lib/api';
import {
  ArrowLeftIcon,
  CurrencyYenIcon,
  CalendarIcon,
  BuildingOfficeIcon,
  DocumentTextIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

interface TotalCalculationForm {
  apartment_id: number | '';
  month: string;
  year: number;
  base_rent: number | '';
  additional_charges: number;
  deductions: number;
  notes: string;
}

interface Apartment {
  id: number;
  apartment_code: string;
  address: string;
  monthly_rent: number;
}

interface CalculationResult {
  apartment: Apartment;
  month: string;
  year: number;
  base_rent: number;
  additional_charges: number;
  deductions: number;
  total_amount: number;
  breakdown: {
    description: string;
    amount: number;
    type: 'charge' | 'deduction';
  }[];
}

export default function TotalCalculationPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const currentDate = new Date();
  const [form, setForm] = useState<TotalCalculationForm>({
    apartment_id: '',
    month: String(currentDate.getMonth() + 1).padStart(2, '0'),
    year: currentDate.getFullYear(),
    base_rent: '',
    additional_charges: 0,
    deductions: 0,
    notes: '',
  });
  const [result, setResult] = useState<CalculationResult | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Fetch apartments
  const { data: apartments = [] } = useQuery({
    queryKey: ['apartments'],
    queryFn: async () => {
      const response = await api.get('/apartments/');
      return response.data as Apartment[];
    },
  });

  // Auto-fill base rent when apartment changes
  const selectedApartment = apartments.find(a => a.id === form.apartment_id);
  React.useEffect(() => {
    if (selectedApartment) {
      setForm(prev => ({ ...prev, base_rent: selectedApartment.monthly_rent }));
    }
  }, [selectedApartment]);

  // Calculate total mutation
  const calculateMutation = useMutation({
    mutationFn: async (data: TotalCalculationForm) => {
      const response = await api.post('/apartment-calculations/total', {
        apartment_id: Number(data.apartment_id),
        month: data.month,
        year: data.year,
        base_rent: Number(data.base_rent),
        additional_charges: data.additional_charges,
        deductions: data.deductions,
        notes: data.notes || null,
      });
      return response.data as CalculationResult;
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

  const handleChange = (field: keyof TotalCalculationForm, value: string | number) => {
    setForm(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setResult(null);

    const newErrors: Record<string, string> = {};
    if (!form.apartment_id) newErrors.apartment_id = 'Debes seleccionar un apartamento';
    if (!form.month) newErrors.month = 'El mes es requerido';
    if (!form.year) newErrors.year = 'El año es requerido';
    if (!form.base_rent || Number(form.base_rent) <= 0) {
      newErrors.base_rent = 'La renta base debe ser mayor a 0';
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
          <h1 className="text-3xl font-bold">Cálculo de Total</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Calcula el monto total incluyendo cargos y deducciones
          </p>
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

            {/* Month & Year */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  <CalendarIcon className="inline h-4 w-4 mr-1" />
                  Mes *
                </label>
                <select
                  value={form.month}
                  onChange={(e) => handleChange('month', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                    errors.month ? 'border-red-500' : ''
                  }`}
                >
                  {Array.from({ length: 12 }, (_, i) => (
                    <option key={i + 1} value={String(i + 1).padStart(2, '0')}>
                      {i + 1}
                    </option>
                  ))}
                </select>
                {errors.month && (
                  <p className="text-sm text-red-500 mt-1">{errors.month}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Año *</label>
                <input
                  type="number"
                  value={form.year}
                  onChange={(e) => handleChange('year', Number(e.target.value))}
                  min="2020"
                  max="2030"
                  className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                    errors.year ? 'border-red-500' : ''
                  }`}
                />
                {errors.year && (
                  <p className="text-sm text-red-500 mt-1">{errors.year}</p>
                )}
              </div>
            </div>

            {/* Base Rent */}
            <div>
              <label className="block text-sm font-medium mb-2">
                <CurrencyYenIcon className="inline h-4 w-4 mr-1" />
                Renta Base (¥) *
              </label>
              <input
                type="number"
                value={form.base_rent}
                onChange={(e) => handleChange('base_rent', e.target.value ? Number(e.target.value) : '')}
                placeholder="Ej: 50000"
                min="0"
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  errors.base_rent ? 'border-red-500' : ''
                }`}
              />
              {errors.base_rent && (
                <p className="text-sm text-red-500 mt-1">{errors.base_rent}</p>
              )}
              {selectedApartment && (
                <p className="text-xs text-muted-foreground mt-1">
                  Renta mensual registrada: ¥{selectedApartment.monthly_rent.toLocaleString()}
                </p>
              )}
            </div>

            {/* Additional Charges */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Cargos Adicionales (¥)
              </label>
              <input
                type="number"
                value={form.additional_charges}
                onChange={(e) => handleChange('additional_charges', Number(e.target.value))}
                placeholder="Ej: 5000"
                min="0"
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Ej: Servicios, mantenimiento, etc.
              </p>
            </div>

            {/* Deductions */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Deducciones (¥)
              </label>
              <input
                type="number"
                value={form.deductions}
                onChange={(e) => handleChange('deductions', Number(e.target.value))}
                placeholder="Ej: 3000"
                min="0"
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Ej: Descuentos, ajustes, etc.
              </p>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium mb-2">
              <DocumentTextIcon className="inline h-4 w-4 mr-1" />
              Notas
            </label>
            <textarea
              value={form.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              placeholder="Información adicional sobre el cálculo"
              rows={3}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3 pt-4 border-t">
            <button
              type="submit"
              disabled={calculateMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {calculateMutation.isPending ? 'Calculando...' : 'Calcular Total'}
            </button>
          </div>
        </form>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Result Card */}
          <div className="bg-card border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">
              Resultado del Cálculo - {result.month}/{result.year}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">Apartamento</p>
                  <p className="font-medium">{result.apartment.apartment_code}</p>
                  <p className="text-sm text-muted-foreground">{result.apartment.address}</p>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Renta Base:</span>
                    <span className="font-medium">¥{result.base_rent.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Cargos Adicionales:</span>
                    <span className="font-medium">¥{result.additional_charges.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Deducciones:</span>
                    <span className="font-medium text-red-600">-¥{result.deductions.toLocaleString()}</span>
                  </div>
                  <div className="pt-2 border-t flex justify-between text-lg font-bold">
                    <span>Total a Pagar:</span>
                    <span className="text-green-600">¥{result.total_amount.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                <p className="text-sm text-green-700 mb-2">Monto Final</p>
                <p className="text-4xl font-bold text-green-800">
                  ¥{result.total_amount.toLocaleString()}
                </p>
                <p className="text-sm text-green-600 mt-2">
                  Base: ¥{result.base_rent.toLocaleString()} + Adicional: ¥{result.additional_charges.toLocaleString()} - Deducción: ¥{result.deductions.toLocaleString()}
                </p>
              </div>
            </div>

            {/* Breakdown */}
            <div className="mt-6 pt-6 border-t">
              <h3 className="font-semibold mb-3">Desglose Detallado</h3>
              <div className="space-y-2 text-sm">
                {result.breakdown.map((item, index) => (
                  <div key={index} className="flex justify-between">
                    <span className="text-muted-foreground">{item.description}</span>
                    <span className={`font-medium ${item.type === 'deduction' ? 'text-red-600' : ''}`}>
                      {item.type === 'deduction' ? '-' : ''}¥{item.amount.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={() => {
                try {
                  const calculationRecord = {
                    id: Date.now(),
                    timestamp: new Date().toISOString(),
                    type: 'total',
                    form: {
                      apartment_id: form.apartment_id,
                      month: form.month,
                      year: form.year,
                      base_rent: form.base_rent,
                      additional_charges: form.additional_charges,
                      deductions: form.deductions,
                      notes: form.notes,
                    },
                    result: {
                      apartment: result.apartment,
                      month: result.month,
                      year: result.year,
                      base_rent: result.base_rent,
                      additional_charges: result.additional_charges,
                      deductions: result.deductions,
                      total_amount: result.total_amount,
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
            <button
              onClick={() => router.push('/apartment-calculations')}
              className="px-4 py-2 border rounded-lg hover:bg-accent transition-colors"
            >
              Ver Todos los Cálculos
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
