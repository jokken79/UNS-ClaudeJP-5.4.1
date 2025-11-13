'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Check, ChevronsUpDown, Search, Building2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Badge } from '@/components/ui/badge';
import type { ApartmentWithStats } from '@/types/apartments-v2';
import axios from 'axios';

interface ApartmentSelectorProps {
  value: number | string;
  onChange: (apartmentId: number) => void;
  onlyAvailable?: boolean;
  required?: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export function ApartmentSelectorEnhanced({
  value,
  onChange,
  onlyAvailable = false,
  required = false,
  disabled = false,
  placeholder = 'Seleccionar apartamento...',
}: ApartmentSelectorProps) {
  const [open, setOpen] = useState(false);
  const [apartments, setApartments] = useState<ApartmentWithStats[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const fetchApartments = async () => {
      try {
        setLoading(true);
        setError(null);

        const token = localStorage.getItem('access_token');
        const response = await axios.get<ApartmentWithStats[]>(
          'http://localhost:8000/api/apartments-v2/apartments',
          {
            headers: { Authorization: `Bearer ${token}` },
            params: {
              available_only: onlyAvailable,
              limit: 500,
              status: 'active',
            },
          }
        );

        setApartments(response.data || []);
      } catch (err: any) {
        console.error('Error fetching apartments:', err);
        setError('アパートの読み込みに失敗しました');
      } finally {
        setLoading(false);
      }
    };

    fetchApartments();
  }, [onlyAvailable]);

  // Filter apartments based on search query
  const filteredApartments = useMemo(() => {
    if (!searchQuery) return apartments;

    const query = searchQuery.toLowerCase();
    return apartments.filter((apt) => {
      const searchableText = [
        apt.name,
        apt.building_name,
        apt.room_number,
        apt.prefecture,
        apt.city,
        apt.address_line1,
        apt.full_address,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();

      return searchableText.includes(query);
    });
  }, [apartments, searchQuery]);

  const selectedApartment = apartments.find(
    (apt) => apt.id === Number(value)
  );

  const getAvailabilityColor = (apartment: ApartmentWithStats) => {
    if (!apartment.is_available) return 'destructive';
    if (apartment.occupancy_rate === 0) return 'default';
    return 'secondary';
  };

  const getAvailabilityLabel = (apartment: ApartmentWithStats) => {
    if (!apartment.is_available) return 'Lleno';
    if (apartment.occupancy_rate === 0) return 'Disponible';
    return 'Parcial';
  };

  if (loading) {
    return (
      <div className="w-full px-4 py-2.5 border rounded-xl bg-muted animate-pulse">
        <span className="text-muted-foreground">Cargando apartamentos...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full px-4 py-2.5 border border-destructive rounded-xl bg-destructive/10">
        <span className="text-destructive text-sm">{error}</span>
      </div>
    );
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          aria-required={required}
          disabled={disabled}
          className="w-full justify-between"
        >
          {selectedApartment ? (
            <div className="flex items-center gap-2 overflow-hidden">
              <Building2 className="h-4 w-4 shrink-0" />
              <span className="truncate">
                {selectedApartment.name || selectedApartment.building_name}
              </span>
              <Badge variant={getAvailabilityColor(selectedApartment)} className="ml-auto shrink-0">
                {getAvailabilityLabel(selectedApartment)}
              </Badge>
            </div>
          ) : (
            <span className="text-muted-foreground">{placeholder}</span>
          )}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[400px] p-0" align="start">
        <Command>
          <CommandInput
            placeholder="Buscar por nombre, dirección..."
            value={searchQuery}
            onValueChange={setSearchQuery}
          />
          <CommandEmpty>No se encontraron apartamentos.</CommandEmpty>
          <CommandGroup className="max-h-[300px] overflow-auto">
            {filteredApartments.map((apartment) => (
              <CommandItem
                key={apartment.id}
                value={apartment.id.toString()}
                onSelect={() => {
                  onChange(apartment.id);
                  setOpen(false);
                }}
                className="flex items-start gap-2 py-3"
              >
                <Check
                  className={cn(
                    'mt-1 h-4 w-4 shrink-0',
                    value === apartment.id ? 'opacity-100' : 'opacity-0'
                  )}
                />
                <div className="flex-1 space-y-1 overflow-hidden">
                  <div className="flex items-center gap-2">
                    <span className="font-medium truncate">
                      {apartment.name || apartment.building_name}
                    </span>
                    <Badge
                      variant={getAvailabilityColor(apartment)}
                      className="shrink-0"
                    >
                      {getAvailabilityLabel(apartment)}
                    </Badge>
                  </div>
                  {apartment.building_name && apartment.room_number && (
                    <div className="text-xs text-muted-foreground truncate">
                      {apartment.building_name} {apartment.room_number}
                    </div>
                  )}
                  <div className="text-xs text-muted-foreground truncate">
                    {apartment.full_address ||
                      [apartment.prefecture, apartment.city, apartment.address_line1]
                        .filter(Boolean)
                        .join(', ')}
                  </div>
                  <div className="flex items-center gap-4 text-xs">
                    <span className="text-muted-foreground">
                      Renta: ¥{apartment.base_rent.toLocaleString()}
                    </span>
                    <span className="text-muted-foreground">
                      Ocupación: {apartment.current_occupancy}/{apartment.max_occupancy}
                      ({apartment.occupancy_rate.toFixed(0)}%)
                    </span>
                  </div>
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

export default ApartmentSelectorEnhanced;
