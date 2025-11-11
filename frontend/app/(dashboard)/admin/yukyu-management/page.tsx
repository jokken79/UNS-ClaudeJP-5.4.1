'use client';

// Disable static generation for this page (uses client-side hooks)
export const dynamic = 'force-dynamic';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import {
  Calendar,
  Users,
  Settings,
  AlertTriangle,
  CheckCircle,
  Clock,
  RefreshCw,
  TrendingUp
} from 'lucide-react';
import api from '@/lib/api';

interface Employee {
  id: number;
  full_name_kanji: string;
  rirekisho_id: string;
  yukyu_remaining?: number;
}

interface SchedulerJob {
  id?: string;
  name?: string;
  trigger?: string;
  next_run?: string;
}

interface SchedulerStatus {
  running: boolean;
  jobs?: SchedulerJob[];
}

interface YukyuCalculationResponse {
  employee_id: number;
  total_available: number;
  assignment_date: string;
  message: string;
}

interface ExpireResponse {
  message: string;
  expired_count: number;
}

export default function AdminYukyuManagementPage() {
  const queryClient = useQueryClient();
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string>('');
  const [expireDialogOpen, setExpireDialogOpen] = useState(false);

  // Fetch employees
  const { data: employees } = useQuery<Employee[]>({
    queryKey: ['employees'],
    queryFn: async () => {
      const res = await api.get('/employees');
      const data = res.data;
      return data.items || [];
    }
  });

  // Fetch scheduler status
  const { data: schedulerStatus, refetch: refetchScheduler } = useQuery<SchedulerStatus>({
    queryKey: ['scheduler-status'],
    queryFn: async () => {
      const res = await api.get('/yukyu/maintenance/scheduler-status');
      return res.data;
    }
  });

  // Calculate yukyu mutation
  const calculateMutation = useMutation<YukyuCalculationResponse, Error, number>({
    mutationFn: async (employeeId: number) => {
      const res = await api.post('/yukyu/balances/calculate', {
        employee_id: employeeId,
        calculation_date: new Date().toISOString().split('T')[0]
      });
      return res.data;
    },
    onSuccess: (data) => {
      toast.success(`Yukyus calculados: ${data.total_available} días disponibles`);
      queryClient.invalidateQueries({ queryKey: ['employees'] });
    },
    onError: (error: Error) => {
      toast.error(`Error: ${error.message}`);
    }
  });

  // Expire old yukyus mutation
  const expireMutation = useMutation<ExpireResponse, Error>({
    mutationFn: async () => {
      const res = await api.post('/yukyu/maintenance/expire-old-yukyus');
      return res.data;
    },
    onSuccess: (data) => {
      toast.success(`${data.message}`);
      setExpireDialogOpen(false);
      queryClient.invalidateQueries({ queryKey: ['employees'] });
    },
    onError: (error: Error) => {
      toast.error(`Error: ${error.message}`);
    }
  });

  const handleCalculate = () => {
    if (!selectedEmployeeId) {
      toast.error('Por favor selecciona un empleado');
      return;
    }
    calculateMutation.mutate(parseInt(selectedEmployeeId));
  };

  const handleExpire = () => {
    setExpireDialogOpen(true);
  };

  const confirmExpire = () => {
    expireMutation.mutate();
  };

  // Calcular estadísticas
  const stats = {
    totalEmployees: employees?.length || 0,
    totalAvailable: employees?.reduce((sum: number, e: Employee) => sum + (e.yukyu_remaining || 0), 0) || 0,
    totalUsed: 0, // TODO: calcular desde requests
    totalExpired: 0 // TODO: calcular desde balances
  };

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          有給休暇管理 (Admin)
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Gestión administrativa de yukyus - Cálculo, expiración y monitoreo
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Empleados</p>
                <p className="text-3xl font-bold">{stats.totalEmployees}</p>
              </div>
              <Users className="h-12 w-12 text-blue-600 opacity-20" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Días Disponibles</p>
                <p className="text-3xl font-bold text-green-600">{stats.totalAvailable}</p>
              </div>
              <TrendingUp className="h-12 w-12 text-green-600 opacity-20" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Días Usados</p>
                <p className="text-3xl font-bold text-blue-600">{stats.totalUsed}</p>
              </div>
              <CheckCircle className="h-12 w-12 text-blue-600 opacity-20" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Días Expirados</p>
                <p className="text-3xl font-bold text-red-600">{stats.totalExpired}</p>
              </div>
              <AlertTriangle className="h-12 w-12 text-red-600 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Calculate Yukyus */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Calcular Yukyus Manualmente
            </CardTitle>
            <CardDescription>
              Calcular y asignar yukyus para un empleado específico
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Seleccionar Empleado</Label>
              <Select value={selectedEmployeeId} onValueChange={setSelectedEmployeeId}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona un empleado..." />
                </SelectTrigger>
                <SelectContent>
                  {employees?.map((emp: Employee) => (
                    <SelectItem key={emp.id} value={emp.id.toString()}>
                      {emp.full_name_kanji} - {emp.rirekisho_id}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button
              onClick={handleCalculate}
              disabled={calculateMutation.isPending || !selectedEmployeeId}
              className="w-full"
            >
              {calculateMutation.isPending ? 'Calculando...' : 'Calcular Yukyus'}
            </Button>
          </CardContent>
        </Card>

        {/* Expire Old Yukyus */}
        <Card className="border-amber-200 dark:border-amber-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-900 dark:text-amber-400">
              <AlertTriangle className="h-5 w-5" />
              Expirar Yukyus Antiguos
            </CardTitle>
            <CardDescription>
              Forzar expiración de yukyus mayores de 2 años (時効)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Alert className="mb-4">
              <AlertDescription>
                Esta acción buscará y expirará automáticamente todos los yukyus con más de 2 años de antigüedad.
              </AlertDescription>
            </Alert>
            <Button
              onClick={handleExpire}
              disabled={expireMutation.isPending}
              variant="outline"
              className="w-full border-amber-500 text-amber-700 hover:bg-amber-50"
            >
              {expireMutation.isPending ? 'Expirando...' : 'Forzar Expiración'}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Scheduler Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Estado del Scheduler de Cron Jobs
          </CardTitle>
          <CardDescription>
            Monitoreo del sistema automático de expiración
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {schedulerStatus ? (
              <>
                <div className="flex items-center justify-between">
                  <span className="font-medium">Estado:</span>
                  <Badge variant={schedulerStatus.running ? "default" : "destructive"}>
                    {schedulerStatus.running ? 'Activo' : 'Detenido'}
                  </Badge>
                </div>
                {schedulerStatus.jobs && schedulerStatus.jobs.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Jobs Configurados:</h4>
                    <div className="space-y-2">
                      {schedulerStatus.jobs.map((job: SchedulerJob, index: number) => (
                        <div key={index} className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-medium">{job.name || job.id}</p>
                              {job.next_run && (
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                  Próxima ejecución: {new Date(job.next_run).toLocaleString('es-ES')}
                                </p>
                              )}
                            </div>
                            <Badge variant="outline">{job.trigger || 'Cron'}</Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <p className="text-gray-500">Cargando estado del scheduler...</p>
            )}
            <Button onClick={() => refetchScheduler()} variant="outline" size="sm" className="gap-2">
              <RefreshCw className="h-4 w-4" />
              Actualizar Estado
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Expire Confirmation Dialog */}
      <Dialog open={expireDialogOpen} onOpenChange={setExpireDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmar Expiración de Yukyus</DialogTitle>
            <DialogDescription>
              Esta acción expirará todos los yukyus con más de 2 años de antigüedad según la ley japonesa.
            </DialogDescription>
          </DialogHeader>
          <Alert className="border-amber-500">
            <AlertTriangle className="h-4 w-4 text-amber-600" />
            <AlertTitle>Advertencia</AlertTitle>
            <AlertDescription>
              Los yukyus expirados no se pueden recuperar. Esta acción es permanente.
            </AlertDescription>
          </Alert>
          <DialogFooter>
            <Button variant="outline" onClick={() => setExpireDialogOpen(false)}>
              Cancelar
            </Button>
            <Button
              onClick={confirmExpire}
              disabled={expireMutation.isPending}
              className="bg-amber-600 hover:bg-amber-700"
            >
              {expireMutation.isPending ? 'Expirando...' : 'Confirmar Expiración'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
