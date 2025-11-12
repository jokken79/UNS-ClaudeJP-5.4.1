"use client";

import { useState } from "react";
import { Palette, Plus, Search, Star, Grid3x3, Download, Upload } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { themes as defaultThemes } from "@/lib/themes";
import { getCustomThemes, type CustomTheme } from "@/lib/custom-themes";
import { hslToRgb, parseHslString, getCategoryForTheme } from "@/lib/theme-utils";
import { useThemePreview } from "@/hooks/useThemePreview";

// Category metadata
const categoryMetadata = [
  { id: "all", emoji: "🎨", label: "All Themes" },
  { id: "corporate", emoji: "🏢", label: "Corporate" },
  { id: "minimal", emoji: "✨", label: "Minimal" },
  { id: "creative", emoji: "🎨", label: "Creative" },
  { id: "nature", emoji: "🌿", label: "Nature" },
  { id: "premium", emoji: "💎", label: "Premium" },
  { id: "vibrant", emoji: "🌈", label: "Vibrant" },
];

// Theme metadata with emojis and descriptions
const themeMetadata: Record<string, { emoji: string; label: string; description: string }> = {
  "uns-kikaku": { emoji: "🏢", label: "UNS Kikaku", description: "Tema corporativo oficial" },
  "default-light": { emoji: "☀️", label: "Light Default", description: "Classic light theme" },
  "default-dark": { emoji: "🌙", label: "Dark Default", description: "Classic dark theme" },
  "ocean-blue": { emoji: "🌊", label: "Ocean Blue", description: "Calming ocean waves" },
  "sunset": { emoji: "🌅", label: "Sunset", description: "Warm sunset colors" },
  "mint-green": { emoji: "🌿", label: "Mint Green", description: "Fresh mint vibes" },
  "royal-purple": { emoji: "👑", label: "Royal Purple", description: "Majestic purple tones" },
  "industrial": { emoji: "🏭", label: "Industrial", description: "Professional steel blue" },
  "vibrant-coral": { emoji: "🪸", label: "Vibrant Coral", description: "Energetic coral pink" },
  "forest-green": { emoji: "🌲", label: "Forest Green", description: "Natural forest tones" },
  "monochrome": { emoji: "⚫", label: "Monochrome", description: "Black and white elegance" },
  "espresso": { emoji: "☕", label: "Espresso", description: "Warm coffee tones" },
};

interface ThemeCardProps {
  theme: typeof defaultThemes[0] | CustomTheme;
  isActive: boolean;
  isFavorite: boolean;
  onSelect: () => void;
  onToggleFavorite: () => void;
  onPreviewStart: () => void;
  onPreviewEnd: () => void;
}

function ThemeCard({
  theme,
  isActive,
  isFavorite,
  onSelect,
  onToggleFavorite,
  onPreviewStart,
  onPreviewEnd,
}: ThemeCardProps) {
  const metadata = themeMetadata[theme.name] || {
    emoji: "🎨",
    label: theme.name,
    description: "Custom theme",
  };

  const primaryHsl = parseHslString(theme.colors["--primary"]) || [0, 0, 0];
  const bgHsl = parseHslString(theme.colors["--background"]) || [0, 0, 100];
  const cardHsl = parseHslString(theme.colors["--card"]) || [0, 0, 100];
  const accentHsl = parseHslString(theme.colors["--accent"]) || [0, 0, 50];

  const primaryRgb = hslToRgb(...primaryHsl);
  const bgRgb = hslToRgb(...bgHsl);
  const cardRgb = hslToRgb(...cardHsl);
  const accentRgb = hslToRgb(...accentHsl);

  const primaryColor = `rgb(${primaryRgb.join(",")})`;
  const bgColor = `rgb(${bgRgb.join(",")})`;
  const cardColor = `rgb(${cardRgb.join(",")})`;
  const accentColor = `rgb(${accentRgb.join(",")})`;

  return (
    <Card
      className={`group relative cursor-pointer transition-all duration-200 hover:scale-105 ${
        isActive ? "border-primary shadow-lg ring-2 ring-primary/20" : "hover:border-primary/50"
      }`}
      onClick={onSelect}
      onMouseEnter={onPreviewStart}
      onMouseLeave={onPreviewEnd}
    >
      <div className="relative">
        {/* Preview Background */}
        <div
          className="h-32 w-full rounded-t-lg"
          style={{
            background: `linear-gradient(135deg, ${bgColor} 0%, ${cardColor} 100%)`,
          }}
        >
          {/* Color Palette Preview */}
          <div className="absolute bottom-3 left-3 flex gap-1.5">
            <div
              className="h-8 w-8 rounded-full border-2 border-white shadow-md"
              style={{ backgroundColor: primaryColor }}
              title="Primary"
            />
            <div
              className="h-8 w-8 rounded-full border-2 border-white shadow-md"
              style={{ backgroundColor: accentColor }}
              title="Accent"
            />
            <div
              className="h-8 w-8 rounded-full border-2 border-white shadow-md"
              style={{ backgroundColor: cardColor }}
              title="Card"
            />
          </div>

          {/* Favorite Star */}
          <button
            className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={(e) => {
              e.stopPropagation();
              onToggleFavorite();
            }}
          >
            <Star
              className={`h-5 w-5 ${
                isFavorite ? "fill-yellow-400 text-yellow-400" : "text-white"
              }`}
            />
          </button>
        </div>

        <CardContent className="p-4">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{metadata.emoji}</span>
                <h3 className="text-base font-semibold truncate">{metadata.label}</h3>
              </div>
              <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                {metadata.description}
              </p>
            </div>
            {isActive && (
              <Badge variant="default" className="shrink-0">
                Active
              </Badge>
            )}
          </div>
        </CardContent>
      </div>
    </Card>
  );
}

export default function ThemesPage() {
  const { theme, setTheme } = useTheme();
  const [customThemes, setCustomThemes] = useState<CustomTheme[]>(getCustomThemes());
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [favorites, setFavorites] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem("theme-favorites");
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  const { startPreview, cancelPreview } = useThemePreview();

  const toggleFavorite = (themeName: string) => {
    const newFavorites = favorites.includes(themeName)
      ? favorites.filter((f) => f !== themeName)
      : [...favorites, themeName];

    setFavorites(newFavorites);
    localStorage.setItem("theme-favorites", JSON.stringify(newFavorites));
  };

  const allThemes = [...defaultThemes, ...customThemes];

  // Filter themes
  const filteredThemes = allThemes.filter((t) => {
    const matchesSearch =
      t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      themeMetadata[t.name]?.label?.toLowerCase().includes(searchQuery.toLowerCase());

    const category = getCategoryForTheme(t.name);
    const matchesCategory = selectedCategory === "all" || category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  // Sort: favorites first, then alphabetically
  const sortedThemes = [...filteredThemes].sort((a, b) => {
    const aIsFav = favorites.includes(a.name);
    const bIsFav = favorites.includes(b.name);

    if (aIsFav && !bIsFav) return -1;
    if (!aIsFav && bIsFav) return 1;

    return a.name.localeCompare(b.name);
  });

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Palette className="h-8 w-8" />
            Theme Gallery
          </h1>
          <p className="text-muted-foreground mt-2">
            Browse, preview, and apply themes. Click to apply, hover to preview, star to favorite.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => (window.location.href = "/themes/customizer")}>
            <Plus className="h-4 w-4 mr-2" />
            Create Theme
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Total Themes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{allThemes.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Predefined</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{defaultThemes.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Custom</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{customThemes.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Favorites</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{favorites.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filter */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search themes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        {/* Category Tabs */}
        <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="w-full">
          <TabsList className="w-full justify-start overflow-x-auto">
            {categoryMetadata.map((cat) => (
              <TabsTrigger key={cat.id} value={cat.id} className="gap-1.5">
                <span>{cat.emoji}</span>
                <span>{cat.label}</span>
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </div>

      {/* Theme Grid */}
      {sortedThemes.length === 0 ? (
        <Card className="p-12">
          <div className="flex flex-col items-center justify-center text-center">
            <Grid3x3 className="h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No themes found</h3>
            <p className="text-sm text-muted-foreground">
              Try adjusting your search or filter criteria
            </p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {sortedThemes.map((themeOption) => (
            <ThemeCard
              key={themeOption.name}
              theme={themeOption}
              isActive={theme === themeOption.name}
              isFavorite={favorites.includes(themeOption.name)}
              onSelect={() => {
                setTheme(themeOption.name);
                cancelPreview();
              }}
              onToggleFavorite={() => toggleFavorite(themeOption.name)}
              onPreviewStart={() => startPreview(themeOption, 500)}
              onPreviewEnd={cancelPreview}
            />
          ))}
        </div>
      )}
    </div>
  );
}
