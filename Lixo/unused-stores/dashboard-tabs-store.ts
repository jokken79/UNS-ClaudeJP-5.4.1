import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type DashboardTab = 'overview' | 'employees' | 'yukyus' | 'apartments' | 'financials' | 'reports'

interface DashboardTabsStore {
  // State
  activeTab: DashboardTab

  // Actions
  setActiveTab: (tab: DashboardTab) => void
}

/**
 * Zustand store for managing dashboard tab state
 * - Persists selected tab to localStorage
 * - Default tab: 'overview'
 * - Storage key: 'dashboard-tabs-store'
 */
export const useDashboardTabsStore = create<DashboardTabsStore>()(
  persist(
    (set) => ({
      activeTab: 'overview',

      setActiveTab: (tab: DashboardTab) => set({ activeTab: tab }),
    }),
    {
      name: 'dashboard-tabs-store', // localStorage key
    }
  )
)
