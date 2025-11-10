export interface GoogleFont {
  family: string;
  variants: string[];
  category: string;
  displayName: string;
}

export interface FontCategory {
  name: string;
  fonts: GoogleFont[];
}

export const GOOGLE_FONTS: FontCategory[] = [
  {
    name: 'Sans Serif',
    fonts: [
      {
        family: 'Roboto',
        variants: ['100', '300', 'regular', '500', '700', '900'],
        category: 'sans-serif',
        displayName: 'Roboto',
      },
      {
        family: 'Inter',
        variants: ['100', '200', '300', 'regular', '500', '600', '700', '800', '900'],
        category: 'sans-serif',
        displayName: 'Inter',
      },
      {
        family: 'Noto Sans JP',
        variants: ['100', '200', '300', 'regular', '500', '600', '700', '800', '900'],
        category: 'sans-serif',
        displayName: 'Noto Sans JP',
      },
    ],
  },
  {
    name: 'Serif',
    fonts: [
      {
        family: 'Noto Serif JP',
        variants: ['200', '300', 'regular', '500', '600', '700', '900'],
        category: 'serif',
        displayName: 'Noto Serif JP',
      },
    ],
  },
];

export function getFontByFamily(family: string): GoogleFont | undefined {
  for (const category of GOOGLE_FONTS) {
    const font = category.fonts.find(f => f.family === family);
    if (font) return font;
  }
  return undefined;
}

export function getAllFontFamilies(): string[] {
  const families: string[] = [];
  for (const category of GOOGLE_FONTS) {
    for (const font of category.fonts) {
      families.push(font.family);
    }
  }
  return families;
}

export function buildGoogleFontsUrl(fonts: { family: string; variants?: string[] }[]): string {
  const fontFamilies = fonts.map(font => {
    const family = font.family.replace(/ /g, '+');
    const variants = font.variants && font.variants.length > 0 ? ':' + font.variants.join(',') : '';
    return `family=${family}${variants}`;
  });
  
  return `https://fonts.googleapis.com/css2?${fontFamilies.join('&')}&display=swap`;
}

export function getFontsByCategory(categoryName: string): GoogleFont[] {
  const category = GOOGLE_FONTS.find(cat => cat.name === categoryName);
  return category ? category.fonts : [];
}

export function loadGoogleFont(family: string): void {
  if (typeof window === 'undefined') return;
  const font = getFontByFamily(family);
  if (!font) return;
  
  const link = document.createElement('link');
  link.href = `https://fonts.googleapis.com/css2?family=${family.replace(/ /g, '+')}:wght@${font.variants.join(';&wght=')}&display=swap`;
  link.rel = 'stylesheet';
  document.head.appendChild(link);
}

export function isFontLoaded(family: string): boolean {
  if (typeof document === 'undefined') return false;
  return document.fonts.check(`1em ${family}`);
}
