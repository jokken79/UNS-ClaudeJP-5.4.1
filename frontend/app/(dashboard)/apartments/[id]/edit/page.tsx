'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import {
  ArrowLeftIcon,
  BuildingOfficeIcon,
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

interface Apartment {
  id: number;
  apartment_code: string;
  address: string;
  monthly_rent: number;
  capacity: number;
  is_available: boolean;
  notes: string | null;
  created_at: string;
  employees_count: number;
  occupancy_rate: number;
  status: 'disponible' | 'parcial' | 'lleno';
}

interface ApartmentUpdateData {
  apartment_code: string;
  address: string;
  monthly_rent: number;
  capacity: number;
  is_available: boolean;
  notes: string;
}

export default function EditApartmentPage() {
  const router = useRouter();
  const params = useParams();
  const apartmentId = params.id as string;
  const queryClient = useQueryClient();

  // Form state
  const [formData, setFormData] = useState<ApartmentUpdateData>({
    apartment_code: '',
    address: '',
    monthly_rent: 0,
    capacity: 1,
    is_available: true,
    notes: '',
  });

  // Validation errors
  const [errors, setErrors] = useState<Partial<Record<keyof ApartmentUpdateData, string>>>({});

  // Fetch apartment data
  const { data: apartment, isLoading, error } = useQuery({
    queryKey: ['apartment', apartmentId],
    queryFn: async () => {
      const response = await api.get(`/apartments/${apartmentId}`);
      return response.data as Apartment;
    },
  });

  // Load data into form when fetched
  useEffect(() => {
    if (apartment) {
      setFormData({
        apartment_code: apartment.apartment_code,
        address: apartment.address,
        monthly_rent: apartment.monthly_rent,
        capacity: apartment.capacity,
        is_available: apartment.is_available,
        notes: apartment.notes || '',
      });
    }
  }, [apartment]);

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: async (data: ApartmentUpdateData) => {
      const response = await api.put(`/apartments/${apartmentId}`, data);
      return response.data;
    },
    onSuccess: () => {
      toast.success('Apartamento actualizado exitosamente');
      // Invalidate queries to force refresh
      queryClient.invalidateQueries({ queryKey: ['apartment', apartmentId] });
      queryClient.invalidateQueries({ queryKey: ['apartments'] });
      queryClient.invalidateQueries({ queryKey: ['apartments-stats'] });
      // Navigate back to details page
      router.push(`/apartments/${apartmentId}`);
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || 'Error al actualizar el apartamento';
      toast.error(errorMessage);
    },
  });

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof ApartmentUpdateData, string>> = {};

    // Apartment code validation
    if (!formData.apartment_code.trim()) {
      newErrors.apartment_code = 'El código del apartamento es requerido';
    }

    // Address validation
    if (!formData.address.trim()) {
      newErrors.address = 'La dirección es requerida';
    }

    // Monthly rent validation
    if (!formData.monthly_rent || formData.monthly_rent <= 0) {
      newErrors.monthly_rent = 'La renta mensual debe ser un número positivo';
    }

    // Capacity validation
    if (!formData.capacity || formData.capacity < 1 || !Number.isInteger(formData.capacity)) {
      newErrors.capacity = 'La capacidad debe ser un número entero mayor o igual a 1';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submit
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error('Por favor, corrige los errores en el formulario');
      return;
    }

    updateMutation.mutate(formData);
  };

  // Handle input changes
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
    } else if (type === 'number') {
      setFormData((prev) => ({ ...prev, [name]: parseFloat(value) || 0 }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }

    // Clear error for this field
    if (errors[name as keyof ApartmentUpdateData]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  // Handle cancel
  const handleCancel = () => {
    router.push(`/apartments/${apartmentId}`);
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="text-center py-12">Cargando datos del apartamento...</div>
      </div>
    );
  }

  if (error || !apartment) {
    return (
      <div className="p-6">
        <div className="text-center py-12 text-red-500">
          Error al cargar el apartamento. Por favor, intenta de nuevo.
        </div>
      </div>
    );
  }

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
          <h1 className="text-3xl font-bold">Editar Apartamento</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {apartment.apartment_code}
          </p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="max-w-4xl">
        <div className="bg-card border rounded-lg p-6 space-y-6">
          {/* Icon header */}
          <div className="flex items-center gap-3 pb-4 border-b">
            <BuildingOfficeIcon className="h-8 w-8 text-primary" />
            <h2 className="text-xl font-semibold">Información del Apartamento</h2>
          </div>

          {/* Form fields grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Apartment Code */}
            <div>
              <label htmlFor="apartment_code" className="block text-sm font-medium mb-2">
                Código del Apartamento <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="apartment_code"
                name="apartment_code"
                value={formData.apartment_code}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  errors.apartment_code ? 'border-red-500' : ''
                }`}
                placeholder="Ej: APT-001"
              />
              {errors.apartment_code && (
                <p className="text-red-500 text-sm mt-1">{errors.apartment_code}</p>
              )}
            </div>

            {/* Address */}
            <div>
              <label htmlFor="address" className="block text-sm font-medium mb-2">
                Dirección <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="address"
                name="address"
                value={formData.address}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  errors.address ? 'border-red-500' : ''
                }`}
                placeholder="Ej: Tokyo, Shibuya..."
              />
              {errors.address && (
                <p className="text-red-500 text-sm mt-1">{errors.address}</p>
              )}
            </div>

            {/* Monthly Rent */}
            <div>
              <label htmlFor="monthly_rent" className="block text-sm font-medium mb-2">
                Renta Mensual (¥) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                id="monthly_rent"
                name="monthly_rent"
                value={formData.monthly_rent}
                onChange={handleChange}
                min="0"
                step="1000"
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  errors.monthly_rent ? 'border-red-500' : ''
                }`}
                placeholder="Ej: 50000"
              />
              {errors.monthly_rent && (
                <p className="text-red-500 text-sm mt-1">{errors.monthly_rent}</p>
              )}
            </div>

            {/* Capacity */}
            <div>
              <label htmlFor="capacity" className="block text-sm font-medium mb-2">
                Capacidad (personas) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                id="capacity"
                name="capacity"
                value={formData.capacity}
                onChange={handleChange}
                min="1"
                step="1"
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  errors.capacity ? 'border-red-500' : ''
                }`}
                placeholder="Ej: 4"
              />
              {errors.capacity && (
                <p className="text-red-500 text-sm mt-1">{errors.capacity}</p>
              )}
            </div>
          </div>

          {/* Is Available Checkbox */}
          <div className="flex items-center gap-2 pt-2">
            <input
              type="checkbox"
              id="is_available"
              name="is_available"
              checked={formData.is_available}
              onChange={handleChange}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            />
            <label htmlFor="is_available" className="text-sm font-medium">
              Disponible para asignación
            </label>
          </div>

          {/* Notes */}
          <div>
            <label htmlFor="notes" className="block text-sm font-medium mb-2">
              Notas
            </label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={4}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              placeholder="Notas adicionales sobre el apartamento..."
            />
          </div>

          {/* Form Actions */}
          <div className="flex items-center gap-3 pt-4 border-t">
            <button
              type="submit"
              disabled={updateMutation.isPending}
              className="flex-1 md:flex-initial px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {updateMutation.isPending ? 'Guardando...' : 'Guardar'}
            </button>
            <button
              type="button"
              onClick={handleCancel}
              disabled={updateMutation.isPending}
              className="flex-1 md:flex-initial px-6 py-2 border rounded-lg hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancelar
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
