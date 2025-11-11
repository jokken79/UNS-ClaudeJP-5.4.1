'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Calendar,
  User,
  Search,
  TrendingDown,
  Clock,
  FileText,
  Filter
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface YukyuUsageDetail {
  id: number;
  request_id: number;
  balance_id: number;
  usage_date: string;
  days_deducted: number;
  request_type: string;
  request_status: string;
  fiscal_year: number;
  notes?: string;
}

interface EmployeeInfo {
  id: number;
  full_name_kanji: string;
  rirekisho_id: string;
  total_available: number;
  total_used: number;
  total_expired: number;
}

export default function YukyuHistoryPage() {
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [fiscalYear, setFiscalYear] = useState<string>('');

  // Fetch employees
  const { data: employees } = useQuery({
    queryKey: ['employees'],
    queryFn: async () => {
      const res = await fetch('/api/employees', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
      });
      if (!res.ok) throw new Error('Failed to fetch employees');
      const data = await res.json();
      return data.items || [];
    }
  });

  // Fetch employee yukyu summary
  const { data: employeeInfo } = useQuery({
    queryKey: ['yukyu-employee-info', selectedEmployeeId],
    queryFn: async () => {
      const res = await fetch(`/api/yukyu/balances/${selectedEmployeeId}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
      });
      if (!res.ok) throw new Error('Failed to fetch employee info');
      return res.json();
    },
    enabled: !!selectedEmployeeId
  });

  // Fetch usage history (simulated - backend endpoint may need to be created)
  const { data: usageHistory, isLoading: historyLoading } = useQuery({
    queryKey: ['yukyu-usage-history', selectedEmployeeId, startDate, endDate, fiscalYear],
    queryFn: async () => {
      // TODO: Este endpoint debe ser creado en el backend si no existe
      // Por ahora retorna datos mock
      const res = await fetch(`/api/yukyu/usage-history/${selectedEmployeeId}?start_date=${startDate}&end_date=${endDate}&fiscal_year=${fiscalYear}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
      });
      if (!res.ok) {
        // Fallback a datos mock si el endpoint no existe aún
        return [];
      }
      return res.json();
    },
    enabled: false // Solo ejecutar cuando usuario haga click en buscar
  });

  const handleSearch = () => {
    if (!selectedEmployeeId) {
      return;
    }
    // Trigger refetch
  };

  const getRequestTypeLabel = (type: string) => {
    const types: Record<string, string> = {
      'yukyu': '有給休暇',
      'hankyu': '半休',
      'ikkikokoku': '一時帰国',
      'taisha': '退社'
    };
    return types[type] || type;
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { bg: string; text: string }> = {
      'approved': { bg: 'bg-green-100', text: 'text-green-800' },
      'pending': { bg: 'bg-yellow-100', text: 'text-yellow-800' },
      'rejected': { bg: 'bg-red-100', text: 'text-red-800' }
    };
    const variant = variants[status] || { bg: 'bg-gray-100', text: 'text-gray-800' };
    return (
      <Badge variant="outline" className={`${variant.bg} ${variant.text}`}>
        {status === 'approved' ? '承認済み' : status === 'pending' ? '承認待ち' : '却下'}
      </Badge>
    );
  };

  const getFiscalYearColor = (year: number) => {
    const colors = [
      'bg-blue-100 text-blue-800',
      'bg-purple-100 text-purple-800',
      'bg-green-100 text-green-800',
      'bg-amber-100 text-amber-800',
      'bg-pink-100 text-pink-800'
    ];
    return colors[year % colors.length];
  };

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          有給休暇使用履歴
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Historial detallado de uso de yukyus con información LIFO
        </p>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filtros de Búsqueda
          </CardTitle>
          <CardDescription>
            Selecciona un empleado y período para ver el historial detallado
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="md:col-span-2">
              <Label>Empleado *</Label>
              <Select value={selectedEmployeeId} onValueChange={setSelectedEmployeeId}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona un empleado..." />
                </SelectTrigger>
                <SelectContent>
                  {employees?.map((emp: any) => (
                    <SelectItem key={emp.id} value={emp.id.toString()}>
                      {emp.full_name_kanji} ({emp.rirekisho_id})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Desde</Label>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div>
              <Label>Hasta</Label>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <Button onClick={handleSearch} disabled={!selectedEmployeeId} className="w-full">
                <Search className="mr-2 h-4 w-4" />
                Buscar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Employee Info Card */}
      {employeeInfo && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Empleado</p>
                  <p className="text-lg font-bold">{employeeInfo.employee_name}</p>
                </div>
                <User className="h-12 w-12 text-blue-600 opacity-20" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Disponible</p>
                  <p className="text-3xl font-bold text-green-600">{employeeInfo.total_available}</p>
                </div>
                <Calendar className="h-12 w-12 text-green-600 opacity-20" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Usado</p>
                  <p className="text-3xl font-bold text-blue-600">{employeeInfo.total_used}</p>
                </div>
                <TrendingDown className="h-12 w-12 text-blue-600 opacity-20" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Expirado</p>
                  <p className="text-3xl font-bold text-red-600">{employeeInfo.total_expired}</p>
                </div>
                <Clock className="h-12 w-12 text-red-600 opacity-20" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Usage History Table */}
      {selectedEmployeeId && (
        <Card>
          <CardHeader>
            <CardTitle>Historial Detallado de Uso</CardTitle>
            <CardDescription>
              Muestra de qué balance (año fiscal) se dedujo cada día usando lógica LIFO
            </CardDescription>
          </CardHeader>
          <CardContent>
            {historyLoading ? (
              <div className="text-center py-8">Cargando historial...</div>
            ) : usageHistory && usageHistory.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-3 font-medium">Fecha Uso</th>
                      <th className="text-left p-3 font-medium">Tipo</th>
                      <th className="text-right p-3 font-medium">Días</th>
                      <th className="text-center p-3 font-medium">Año Fiscal</th>
                      <th className="text-center p-3 font-medium">Estado</th>
                      <th className="text-left p-3 font-medium">Notas</th>
                    </tr>
                  </thead>
                  <tbody>
                    {usageHistory.map((usage: YukyuUsageDetail) => (
                      <tr key={usage.id} className="border-b hover:bg-gray-50 dark:hover:bg-gray-800">
                        <td className="p-3">
                          {new Date(usage.usage_date).toLocaleDateString('es-ES')}
                        </td>
                        <td className="p-3">{getRequestTypeLabel(usage.request_type)}</td>
                        <td className="p-3 text-right font-mono">{usage.days_deducted.toFixed(1)}</td>
                        <td className="p-3 text-center">
                          <Badge variant="outline" className={getFiscalYearColor(usage.fiscal_year)}>
                            {usage.fiscal_year}年度
                          </Badge>
                        </td>
                        <td className="p-3 text-center">
                          {getStatusBadge(usage.request_status)}
                        </td>
                        <td className="p-3 text-sm text-gray-600">{usage.notes || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <Alert>
                <FileText className="h-4 w-4" />
                <AlertDescription>
                  {selectedEmployeeId
                    ? 'No se encontraron registros de uso de yukyu para este empleado y período.'
                    : 'Selecciona un empleado y haz click en "Buscar" para ver el historial.'}
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* LIFO Explanation */}
      <Card className="mt-6 border-blue-200 dark:border-blue-800">
        <CardHeader>
          <CardTitle className="text-blue-900 dark:text-blue-100">
            ℹ️ Sobre la Lógica LIFO
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-blue-800 dark:text-blue-200">
          <p className="mb-2">
            El sistema utiliza <strong>LIFO (Last In, First Out)</strong> para deducir yukyus:
          </p>
          <ul className="list-disc list-inside space-y-1">
            <li>Los yukyus más recientes se usan primero</li>
            <li>Esto maximiza el uso antes de que expiren (2 años)</li>
            <li>Cada deducción se vincula al balance (año fiscal) específico</li>
            <li>Los colores indican de qué año fiscal se dedujo cada día</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
