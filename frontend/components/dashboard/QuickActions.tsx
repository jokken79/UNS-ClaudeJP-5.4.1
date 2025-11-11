'use client';

import React from 'react';
import Link from 'next/link';
import {
  UserPlusIcon,
  DocumentPlusIcon,
  BuildingOfficeIcon,
  CalendarIcon,
  BanknotesIcon,
  ClockIcon,
  UserGroupIcon,
  ChartBarIcon,
  DocumentTextIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

export interface QuickAction {
  id: string;
  label: string;
  description: string;
  href: string;
  icon: React.ElementType;
  color: 'blue' | 'green' | 'purple' | 'orange' | 'indigo' | 'pink' | 'red' | 'yellow';
  badge?: string | number;
}

export interface QuickActionsProps {
  actions?: QuickAction[];
  title?: string;
  columns?: 2 | 3 | 4;
  loading?: boolean;
}

const colorClasses = {
  blue: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    icon: 'bg-blue-500',
    text: 'text-blue-700',
    hover: 'hover:bg-blue-100'
  },
  green: {
    bg: 'bg-green-50',
    border: 'border-green-200',
    icon: 'bg-green-500',
    text: 'text-green-700',
    hover: 'hover:bg-green-100'
  },
  purple: {
    bg: 'bg-purple-50',
    border: 'border-purple-200',
    icon: 'bg-purple-500',
    text: 'text-purple-700',
    hover: 'hover:bg-purple-100'
  },
  orange: {
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    icon: 'bg-orange-500',
    text: 'text-orange-700',
    hover: 'hover:bg-orange-100'
  },
  indigo: {
    bg: 'bg-indigo-50',
    border: 'border-indigo-200',
    icon: 'bg-indigo-500',
    text: 'text-indigo-700',
    hover: 'hover:bg-indigo-100'
  },
  pink: {
    bg: 'bg-pink-50',
    border: 'border-pink-200',
    icon: 'bg-pink-500',
    text: 'text-pink-700',
    hover: 'hover:bg-pink-100'
  },
  red: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    icon: 'bg-red-500',
    text: 'text-red-700',
    hover: 'hover:bg-red-100'
  },
  yellow: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    icon: 'bg-yellow-500',
    text: 'text-yellow-700',
    hover: 'hover:bg-yellow-100'
  }
};

// Default quick actions
const defaultActions: QuickAction[] = [
  {
    id: 'add-candidate',
    label: 'Add Candidate',
    description: 'Register new candidate',
    href: '/dashboard/candidates/new',
    icon: UserPlusIcon,
    color: 'blue'
  },
  {
    id: 'add-employee',
    label: 'Add Employee',
    description: 'Register new employee',
    href: '/dashboard/employees/new',
    icon: UserGroupIcon,
    color: 'green'
  },
  {
    id: 'create-payroll',
    label: 'Create Payroll',
    description: 'Start new payroll run',
    href: '/dashboard/payroll/new',
    icon: BanknotesIcon,
    color: 'purple'
  },
  {
    id: 'add-timer-card',
    label: 'Timer Card',
    description: 'Record attendance',
    href: '/dashboard/timercards/new',
    icon: ClockIcon,
    color: 'orange'
  },
  {
    id: 'apartment-assignment',
    label: 'Assign Apartment',
    description: 'Assign employee to apartment',
    href: '/dashboard/apartments/assignments/new',
    icon: BuildingOfficeIcon,
    color: 'indigo'
  },
  {
    id: 'create-request',
    label: 'New Request',
    description: 'Submit employee request',
    href: '/dashboard/requests/new',
    icon: DocumentPlusIcon,
    color: 'pink'
  },
  {
    id: 'view-reports',
    label: 'View Reports',
    description: 'Access system reports',
    href: '/dashboard/reports',
    icon: ChartBarIcon,
    color: 'yellow'
  },
  {
    id: 'settings',
    label: 'Settings',
    description: 'System configuration',
    href: '/dashboard/settings',
    icon: Cog6ToothIcon,
    color: 'red'
  }
];

/**
 * QuickActions - Dashboard Quick Actions Component
 *
 * Displays a grid of quick action buttons for common tasks:
 * - Customizable action list
 * - Icon and color variants
 * - Badge support for notifications
 * - Responsive grid layout (2, 3, or 4 columns)
 * - Loading state with skeleton
 */
export function QuickActions({
  actions = defaultActions,
  title = 'Quick Actions',
  columns = 4,
  loading = false
}: QuickActionsProps) {
  const gridCols = {
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-4'
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-6"></div>
        <div className={`grid ${gridCols[columns]} gap-4`}>
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-24 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-500 mt-1">Frequently used actions</p>
      </div>

      {/* Actions Grid */}
      <div className={`grid ${gridCols[columns]} gap-4`}>
        {actions.map((action) => {
          const Icon = action.icon;
          const colors = colorClasses[action.color];

          return (
            <Link
              key={action.id}
              href={action.href}
              className={`
                relative block p-4 rounded-lg border transition-all
                ${colors.bg} ${colors.border} ${colors.hover}
                hover:shadow-md
              `}
            >
              {/* Badge */}
              {action.badge && (
                <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full h-6 w-6 flex items-center justify-center">
                  {action.badge}
                </div>
              )}

              {/* Icon */}
              <div className={`${colors.icon} rounded-full p-2 inline-block mb-3`}>
                <Icon className="h-6 w-6 text-white" />
              </div>

              {/* Label and Description */}
              <div>
                <p className={`font-medium ${colors.text} mb-1`}>{action.label}</p>
                <p className="text-xs text-gray-600">{action.description}</p>
              </div>
            </Link>
          );
        })}
      </div>

      {/* Footer Note */}
      {actions.length === 0 && (
        <div className="text-center py-8 text-gray-400">
          <DocumentTextIcon className="h-12 w-12 mx-auto mb-2" />
          <p className="text-sm">No quick actions configured</p>
        </div>
      )}
    </div>
  );
}
