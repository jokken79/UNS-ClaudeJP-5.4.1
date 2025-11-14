'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface VisibilidadTemplate {
  id: string;
  name: string;
  description: string;
  colors: {
    primary: string;
    secondary: string;
    background: string;
    text: string;
    border: string;
  };
  sidebar: {
    width: string;
    backgroundColor: string;
    textColor: string;
    activeItemBg: string;
    activeItemText: string;
    activeItemBorder: string;
  };
  nav: {
    spacing: string;
    iconSize: string;
    fontSize: string;
    hoverEffect: boolean;
  };
}

interface VisibilidadStore {
  templates: VisibilidadTemplate[];
  activeTemplate: VisibilidadTemplate | null;
  addTemplate: (template: VisibilidadTemplate) => void;
  updateTemplate: (id: string, updates: Partial<VisibilidadTemplate>) => void;
  deleteTemplate: (id: string) => void;
  setActiveTemplate: (id: string) => void;
  getDefaultTemplate: () => VisibilidadTemplate;
}

const defaultTemplate: VisibilidadTemplate = {
  id: 'default-visibilidad-rrhh',
  name: 'Visibilidad RRHH Default',
  description: 'Plantilla por defecto del sistema de visibilidad para RRHH',
  colors: {
    primary: '#2563eb',
    secondary: '#1e40af',
    background: '#ffffff',
    text: '#1f2937',
    border: '#e5e7eb',
  },
  sidebar: {
    width: 'w-64',
    backgroundColor: 'bg-white',
    textColor: 'text-gray-600',
    activeItemBg: 'bg-blue-50',
    activeItemText: 'text-blue-700',
    activeItemBorder: 'border-blue-600',
  },
  nav: {
    spacing: 'space-y-1',
    iconSize: 'w-5 h-5',
    fontSize: 'text-sm',
    hoverEffect: true,
  },
};

export const useVisibilidadTemplateStore = create<VisibilidadStore>()(
  persist(
    (set, get) => ({
      templates: [defaultTemplate],
      activeTemplate: defaultTemplate,

      getDefaultTemplate: () => defaultTemplate,

      addTemplate: (template) =>
        set((state) => ({
          templates: [...state.templates, template],
        })),

      updateTemplate: (id, updates) =>
        set((state) => ({
          templates: state.templates.map((t) =>
            t.id === id ? { ...t, ...updates } : t
          ),
          activeTemplate:
            state.activeTemplate?.id === id
              ? { ...state.activeTemplate, ...updates }
              : state.activeTemplate,
        })),

      deleteTemplate: (id) =>
        set((state) => ({
          templates: state.templates.filter((t) => t.id !== id),
          activeTemplate:
            state.activeTemplate?.id === id ? null : state.activeTemplate,
        })),

      setActiveTemplate: (id) =>
        set((state) => ({
          activeTemplate:
            state.templates.find((t) => t.id === id) || state.activeTemplate,
        })),
    }),
    {
      name: 'visibilidad-template-store',
      version: 1,
    }
  )
);
