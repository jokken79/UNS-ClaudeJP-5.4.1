import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type FontVariant = 
  | 'inter'
  | 'manrope'
  | 'poppins'
  | 'work-sans'
  | 'ibm-plex-sans'
  | 'open-sans'
  | 'roboto'
  | 'lato'
  | 'sora'
  | 'montserrat'
  | 'noto-sans-jp'
  | 'ibm-plex-sans-jp';

export type FontType = 'body' | 'heading' | 'ui' | 'japanese';

interface FontStore {
  // Current selected fonts
  fontBody: FontVariant;
  fontHeading: FontVariant;
  fontUI: FontVariant;
  fontJapanese: FontVariant;

  // Font size settings
  baseFontSize: number; // in px (default: 16)
  headingScale: number; // multiplier (default: 1)

  // Setters
  setFontBody: (font: FontVariant) => void;
  setFontHeading: (font: FontVariant) => void;
  setFontUI: (font: FontVariant) => void;
  setFontJapanese: (font: FontVariant) => void;
  setBaseFontSize: (size: number) => void;
  setHeadingScale: (scale: number) => void;

  // Apply fonts to DOM
  applyFonts: () => void;
  
  // Reset to defaults
  reset: () => void;
}

const FONT_CSS_VARS: Record<FontVariant, string> = {
  'inter': '--font-inter',
  'manrope': '--font-manrope',
  'poppins': '--font-poppins',
  'work-sans': '--font-work-sans',
  'ibm-plex-sans': '--font-ibm-plex-sans',
  'open-sans': '--font-open-sans',
  'roboto': '--font-roboto',
  'lato': '--font-lato',
  'sora': '--font-sora',
  'montserrat': '--font-montserrat',
  'noto-sans-jp': '--font-noto-sans-jp',
  'ibm-plex-sans-jp': '--font-ibm-plex-sans-jp',
};

const FONT_CATEGORIES: Record<FontVariant, FontType> = {
  'inter': 'body',
  'manrope': 'body',
  'poppins': 'body',
  'work-sans': 'ui',
  'ibm-plex-sans': 'body',
  'open-sans': 'body',
  'roboto': 'body',
  'lato': 'body',
  'sora': 'ui',
  'montserrat': 'heading',
  'noto-sans-jp': 'japanese',
  'ibm-plex-sans-jp': 'japanese',
};

export const useFontsStore = create<FontStore>()(
  persist(
    (set, get) => ({
      // Default values
      fontBody: 'manrope',
      fontHeading: 'poppins',
      fontUI: 'work-sans',
      fontJapanese: 'noto-sans-jp',
      baseFontSize: 16,
      headingScale: 1,

      // Setters
      setFontBody: (font: FontVariant) => {
        set({ fontBody: font });
        get().applyFonts();
      },
      setFontHeading: (font: FontVariant) => {
        set({ fontHeading: font });
        get().applyFonts();
      },
      setFontUI: (font: FontVariant) => {
        set({ fontUI: font });
        get().applyFonts();
      },
      setFontJapanese: (font: FontVariant) => {
        set({ fontJapanese: font });
        get().applyFonts();
      },
      setBaseFontSize: (size: number) => {
        set({ baseFontSize: Math.max(12, Math.min(24, size)) });
        get().applyFonts();
      },
      setHeadingScale: (scale: number) => {
        set({ headingScale: Math.max(0.8, Math.min(1.5, scale)) });
        get().applyFonts();
      },

      // Apply fonts to DOM
      applyFonts: () => {
        const state = get();
        const root = document.documentElement;

        // Apply font family CSS variables
        root.style.setProperty('--layout-font-body', `var(${FONT_CSS_VARS[state.fontBody]})`);
        root.style.setProperty('--layout-font-heading', `var(${FONT_CSS_VARS[state.fontHeading]})`);
        root.style.setProperty('--layout-font-ui', `var(${FONT_CSS_VARS[state.fontUI]})`);
        root.style.setProperty('--layout-font-japanese', `var(${FONT_CSS_VARS[state.fontJapanese]})`);

        // Apply font sizes
        root.style.setProperty('--base-font-size', `${state.baseFontSize}px`);
        root.style.setProperty('--heading-scale', `${state.headingScale}`);

        // Apply base font size to body
        document.body.style.fontSize = `${state.baseFontSize}px`;
      },

      // Reset to defaults
      reset: () => {
        set({
          fontBody: 'manrope',
          fontHeading: 'poppins',
          fontUI: 'work-sans',
          fontJapanese: 'noto-sans-jp',
          baseFontSize: 16,
          headingScale: 1,
        });
        get().applyFonts();
      },
    }),
    {
      name: 'fonts-store',
      version: 1,
    }
  )
);

// Helper hook to get all available fonts by category
export const getAvailableFonts = (category: FontType): FontVariant[] => {
  return Object.entries(FONT_CATEGORIES)
    .filter(([_, cat]) => cat === category)
    .map(([font]) => font as FontVariant);
};

// Get font display name
export const getFontDisplayName = (font: FontVariant): string => {
  const names: Record<FontVariant, string> = {
    'inter': 'Inter',
    'manrope': 'Manrope',
    'poppins': 'Poppins',
    'work-sans': 'Work Sans',
    'ibm-plex-sans': 'IBM Plex Sans',
    'open-sans': 'Open Sans',
    'roboto': 'Roboto',
    'lato': 'Lato',
    'sora': 'Sora',
    'montserrat': 'Montserrat',
    'noto-sans-jp': 'Noto Sans JP 🇯🇵',
    'ibm-plex-sans-jp': 'IBM Plex Sans JP 🇯🇵',
  };
  return names[font];
};
