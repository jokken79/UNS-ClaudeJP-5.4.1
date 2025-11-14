'use client';

import { create } from 'zustand';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface SettingsState {
  visibilityEnabled: boolean;
  isLoading: boolean;
  setVisibilityEnabled: (enabled: boolean) => void;
  fetchVisibilityToggle: () => Promise<void>;
  updateVisibilityToggle: (enabled: boolean) => Promise<void>;
}

export const useSettingsStore = create<SettingsState>()((set) => ({
  visibilityEnabled: true,
  isLoading: false,

  setVisibilityEnabled: (enabled) => set({ visibilityEnabled: enabled }),

  fetchVisibilityToggle: async () => {
    set({ isLoading: true });
    try {
      // Check if running on server-side
      if (typeof window === 'undefined') {
        console.warn('Cannot access localStorage on server-side');
        set({ isLoading: false });
        return;
      }

      const token = localStorage.getItem('auth-storage');
      const authData = token ? JSON.parse(token) : null;
      const accessToken = authData?.state?.token;

      const response = await fetch(`${API_BASE_URL}/settings/visibility`, {
        headers: {
          ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
        },
      });

      if (!response.ok) {
        // Endpoint might not exist - use default value
        console.warn('Visibility toggle endpoint not available, using default value');
        set({ visibilityEnabled: true, isLoading: false });
        return;
      }
      const data = await response.json();
      set({ visibilityEnabled: data.enabled, isLoading: false });
    } catch (error) {
      console.warn('Error fetching visibility toggle, using default value:', error);
      set({ visibilityEnabled: true, isLoading: false });
    }
  },

  updateVisibilityToggle: async (enabled: boolean) => {
    set({ isLoading: true });
    try {
      // Check if running on server-side
      if (typeof window === 'undefined') {
        console.warn('Cannot access localStorage on server-side');
        set({ isLoading: false });
        return;
      }

      const token = localStorage.getItem('auth-storage');
      const authData = token ? JSON.parse(token) : null;
      const accessToken = authData?.state?.token;

      const response = await fetch(`${API_BASE_URL}/settings/visibility`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
        },
        body: JSON.stringify({ enabled }),
      });

      if (!response.ok) {
        // Endpoint might not exist - gracefully handle
        console.warn('Visibility toggle update endpoint not available');
        set({ visibilityEnabled: enabled, isLoading: false });
        return;
      }

      const data = await response.json();
      set({ visibilityEnabled: data.enabled, isLoading: false });
    } catch (error) {
      console.warn('Error updating visibility toggle, setting local value:', error);
      // Set the value locally even if backend update fails
      set({ visibilityEnabled: enabled, isLoading: false });
    }
  },
}));
