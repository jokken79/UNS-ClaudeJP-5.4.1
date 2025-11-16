'use client';

import { useAuthStore } from '@/stores/auth-store';
import { useSettingsStore } from '@/stores/settings-store';
import { UnderConstruction } from './under-construction';

interface VisibilityGuardProps {
  children: React.ReactNode;
}

export function VisibilityGuard({ children }: VisibilityGuardProps) {
  const { user } = useAuthStore();
  const { underConstructionPages, isPageUnderConstruction } = useSettingsStore();

  // Check if user should see construction page
  // Only ADMIN and KANRINSHA are affected by the toggle
  const isAffectedRole = user?.role === 'ADMIN' || user?.role === 'KANRINSHA';

  // Check if current page is marked as under construction
  // For now, we'll use a simple check - you can expand this logic later
  const shouldShowConstruction = isAffectedRole && underConstructionPages.length > 0;

  if (shouldShowConstruction) {
    return <UnderConstruction />;
  }

  return <>{children}</>;
}
