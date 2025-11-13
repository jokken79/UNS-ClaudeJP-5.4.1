'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import {
  ArrowLeftIcon,
  ArrowRightIcon,
  BuildingOfficeIcon,
  UserIcon,
  CalendarIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';

interface TransferForm {
  assignment_id: number | '';
  from_apartment_id: number | '';
  to_apartment_id: number | '';
  transfer_date: string;
  reason: string;
  notes: string;
}

interface Assignment {
  id: number;
  employee_id: number;
  apartment_id: number;
  is_active: boolean;
  employee: {
    full_name_kanji: string;
    hakenmoto_id: number;
  };
  apartment: {
    apartment_code: string;
    address: string;
  };
}

interface Apartment {
  id: number;
  apartment_code: string;
  address: string;
  capacity: number;
  employees_count: number;
  is_available: boolean;
}

export default function TransferAssignmentPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [form, setForm] = useState<TransferForm>({
    assignment_id: '',
    from_apartment_id: '',
    to_apartment_id: '',
    transfer_date: new Date().toISOString().split('T')[0],
    reason: '',
    notes: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Fetch active assignments
  const { data: assignments = [] } = useQuery({
    queryKey: ['active-assignments'],
    queryFn: async () => {
      const response = await api.get('/apartment-assignments/?status=active');
      return response.data as Assignment[];
    },
  });

  // Fetch available apartments
  const { data: apartments = [] } = useQuery({
    queryKey: ['available-apartments-for-transfer'],
    queryFn: async () => {
      const response = await api.get('/apartments-v2/apartments');
      return response.data as Apartment[];
    },
  });

  // Transfer mutation
  const transferMutation = useMutation({
    mutationFn: async (data: TransferForm) => {
      const response = await api.post('/apartment-assignments/transfer', {
        assignment_id: Number(data.assignment_id),
        to_apartment_id: Number(data.to_apartment_id),
        transfer_date: data.transfer_date,
        reason: data.reason,
        notes: data.notes || null,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apartment-assignments'] });
      queryClient.invalidateQueries({ queryKey: ['apartment-assignments-stats'] });
      router.push('/apartment-assignments');
    },
    onError: (error: any) => {
      if (error.response?.data?.detail) {
        setErrors({ general: error.response.data.detail });
      }
    },
  });

  const handleChange = (field: keyof TransferForm, value: string | number) => {
    setForm(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  // Auto-select from_apartment when assignment changes
  const selectedAssignment = assignments.find(a => a.id === form.assignment_id);
  React.useEffect(() => {
    if (selectedAssignment && selectedAssignment.apartment_id !== form.from_apartment_id) {
      setForm(prev => ({ ...prev, from_apartment_id: selectedAssignment.apartment_id }));
    }
  }, [selectedAssignment, form.from_apartment_id]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const newErrors: Record<string, string> = {};
    if (!form.assignment_id) newErrors.assignment_id = 'Debes seleccionar una asignación';
    if (!form.to_apartment_id) newErrors.to_apartment_id = 'Debes seleccionar un apartamento destino';
    if (!form.transfer_date) newErrors.transfer_date = 'La fecha es requerida';
    if (!form.reason.trim()) newErrors.reason = 'El motivo es requerido';
    if (form.from_apartment_id === form.to_apartment_id) {
      newErrors.to_apartment_id = 'El apartamento destino debe ser diferente al actual';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    transferMutation.mutate(form);
  };

  const availableApartments = apartments.filter(
    a => a.id !== form.from_apartment_id && a.is_available
  );

  const selectedToApartment = apartments.find(a => a.id === form.to_apartment_id);

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
          <h1 className="text-3xl font-bold">Transferir Asignación</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Mover un empleado a un apartamento diferente
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

          {/* Transfer Flow */}
          <div className="bg-muted p-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex-1 text-center">
                <p className="text-sm text-muted-foreground mb-1">Desde</p>
                <p className="font-medium">Apartamento Actual</p>
              </div>
              <ArrowRightIcon className="h-8 w-8 text-primary mx-4" />
              <div className="flex-1 text-center">
                <p className="text-sm text-muted-foreground mb-1">Hacia</p>
                <p className="font-medium">Apartamento Destino</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Assignment Selection */}
            <div>
              <label className="block text-sm font-medium mb-2">
                <UserIcon className="inline h-4 w-4 mr-1" />
                Asignación a Transferir *
              </label>
              <select
                value={form.assignment_id}
                onChange={(e) => handleChange('assignment_id', e.target.value ? Number(e.target.value) : '')}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  errors.assignment_id ? 'border-red-500' : ''
                }`}
              >
                <option value="">Seleccionar asignación</option>
                {assignments.map((assignment) => (
                  <option key={assignment.id} value={assignment.id}>
                    {assignment.employee.full_name_kanji} (ID: {assignment.employee.hakenmoto_id})
                    {' - '}
                    {assignment.apartment.apartment_code}
                  </option>
                ))}
              </select>
              {errors.assignment_id && (
                <p className="text-sm text-red-500 mt-1">{errors.assignment_id}</p>
              )}
            </div>

            {/* From Apartment (Read-only) */}
            <div>
              <label className="block text-sm font-medium mb-2">
                <BuildingOfficeIcon className="inline h-4 w-4 mr-1" />
                Apartamento Origen
              </label>
              <div className="px-3 py-2 border rounded-lg bg-muted">
                {selectedAssignment ? (
                  <div>
                    <p className="font-medium">{selectedAssignment.apartment.apartment_code}</p>
                    <p className="text-sm text-muted-foreground">{selectedAssignment.apartment.address}</p>
                  </div>
                ) : (
                  <p className="text-muted-foreground">Selecciona una asignación</p>
                )}
              </div>
            </div>

            {/* To Apartment */}
            <div>
              <label className="block text-sm font-medium mb-2">
                <BuildingOfficeIcon className="inline h-4 w-4 mr-1" />
                Apartamento Destino *
              </label>
              <select
                value={form.to_apartment_id}
                onChange={(e) => handleChange('to_apartment_id', e.target.value ? Number(e.target.value) : '')}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  errors.to_apartment_id ? 'border-red-500' : ''
                }`}
              >
                <option value="">Seleccionar apartamento</option>
                {availableApartments.map((apartment) => (
                  <option key={apartment.id} value={apartment.id}>
                    {apartment.apartment_code} - {apartment.address}
                    {' '}({apartment.employees_count}/{apartment.capacity})
                  </option>
                ))}
              </select>
              {errors.to_apartment_id && (
                <p className="text-sm text-red-500 mt-1">{errors.to_apartment_id}</p>
              )}
            </div>

            {/* Transfer Date */}
            <div>
              <label className="block text-sm font-medium mb-2">
                <CalendarIcon className="inline h-4 w-4 mr-1" />
                Fecha de Transferencia *
              </label>
              <input
                type="date"
                value={form.transfer_date}
                onChange={(e) => handleChange('transfer_date', e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  errors.transfer_date ? 'border-red-500' : ''
                }`}
              />
              {errors.transfer_date && (
                <p className="text-sm text-red-500 mt-1">{errors.transfer_date}</p>
              )}
            </div>
          </div>

          {/* Reason */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Motivo de Transferencia *
            </label>
            <select
              value={form.reason}
              onChange={(e) => handleChange('reason', e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                errors.reason ? 'border-red-500' : ''
              }`}
            >
              <option value="">Seleccionar motivo</option>
              <option value="capacity_issues">Problemas de capacidad</option>
              <option value="employee_request">Solicitud del empleado</option>
              <option value="company_needs">Necesidades de la empresa</option>
              <option value="maintenance">Mantenimiento</option>
              <option value="disciplinary">Motivos disciplinarios</option>
              <option value="other">Otro</option>
            </select>
            {errors.reason && (
              <p className="text-sm text-red-500 mt-1">{errors.reason}</p>
            )}
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
              placeholder="Información adicional sobre la transferencia"
              rows={4}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Preview */}
          {selectedAssignment && selectedToApartment && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-semibold mb-3">Vista Previa de la Transferencia</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Empleado:</p>
                  <p className="font-medium">{selectedAssignment.employee.full_name_kanji}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Desde:</p>
                  <p className="font-medium">{selectedAssignment.apartment.apartment_code}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Hacia:</p>
                  <p className="font-medium">{selectedToApartment.apartment_code}</p>
                  <p className="text-xs text-muted-foreground">
                    {selectedToApartment.employees_count}/{selectedToApartment.capacity} ocupados
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Fecha:</p>
                  <p className="font-medium">
                    {new Date(form.transfer_date).toLocaleDateString('es-ES')}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-3 pt-4 border-t">
            <button
              type="submit"
              disabled={transferMutation.isPending || !selectedAssignment || !selectedToApartment}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {transferMutation.isPending ? 'Transfiriendo...' : 'Transferir Asignación'}
            </button>
            <button
              type="button"
              onClick={() => router.back()}
              className="flex items-center gap-2 px-4 py-2 border rounded-lg hover:bg-accent transition-colors"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
