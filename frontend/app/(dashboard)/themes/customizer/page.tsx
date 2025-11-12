"use client";

import { useState, useEffect } from "react";
import { Palette, Save, Download, Upload, Eye, AlertCircle, CheckCircle2, X, Trash2 } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { themes as defaultThemes } from "@/lib/themes";
import {
  addCustomTheme,
  updateCustomTheme,
  clearThemeCache,
  getThemeCacheSize,
  type CustomTheme,
} from "@/lib/custom-themes";
import { validateContrast, parseHslString } from "@/lib/theme-utils";
import { exportAsJSON, exportAndDownload } from "@/lib/css-export";
import { ColorPicker } from "@/components/color-picker";

// Theme color tokens that users can customize
const COLOR_TOKENS = [
  { key: "--background", label: "Background", description: "Main background color" },
  { key: "--foreground", label: "Foreground", description: "Main text color" },
  { key: "--card", label: "Card", description: "Card background" },
  { key: "--card-foreground", label: "Card Text", description: "Text on cards" },
  { key: "--popover", label: "Popover", description: "Popover background" },
  { key: "--popover-foreground", label: "Popover Text", description: "Text in popovers" },
  { key: "--primary", label: "Primary", description: "Primary brand color" },
  { key: "--primary-foreground", label: "Primary Text", description: "Text on primary" },
  { key: "--secondary", label: "Secondary", description: "Secondary color" },
  { key: "--secondary-foreground", label: "Secondary Text", description: "Text on secondary" },
  { key: "--muted", label: "Muted", description: "Muted background" },
  { key: "--muted-foreground", label: "Muted Text", description: "Muted text" },
  { key: "--accent", label: "Accent", description: "Accent color" },
  { key: "--accent-foreground", label: "Accent Text", description: "Text on accent" },
  { key: "--destructive", label: "Destructive", description: "Error/danger color" },
  { key: "--destructive-foreground", label: "Destructive Text", description: "Text on destructive" },
  { key: "--border", label: "Border", description: "Border color" },
  { key: "--input", label: "Input", description: "Input border color" },
  { key: "--ring", label: "Ring", description: "Focus ring color" },
];

export default function ThemeCustomizerPage() {
  const { theme: currentTheme, setTheme } = useTheme();
  const [themeName, setThemeName] = useState("");
  const [themeColors, setThemeColors] = useState<Record<string, string>>({});
  const [validationResults, setValidationResults] = useState<Record<string, boolean>>({});
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [showClearCacheDialog, setShowClearCacheDialog] = useState(false);
  const [importJson, setImportJson] = useState("");
  const [importError, setImportError] = useState("");
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [cacheCleared, setCacheCleared] = useState(false);
  const [cacheSize, setCacheSize] = useState(0);

  // Initialize with default theme
  useEffect(() => {
    const defaultTheme = defaultThemes[0];
    setThemeColors(defaultTheme.colors);
    setThemeName("My Custom Theme");
  }, []);

  // Calculate cache size on mount and when cache is cleared
  useEffect(() => {
    const size = getThemeCacheSize();
    setCacheSize(size);
  }, [cacheCleared]);

  // Validate contrast when colors change
  useEffect(() => {
    const results: Record<string, boolean> = {};

    // Validate text/background pairs
    const pairs = [
      ["--background", "--foreground"],
      ["--card", "--card-foreground"],
      ["--popover", "--popover-foreground"],
      ["--primary", "--primary-foreground"],
      ["--secondary", "--secondary-foreground"],
      ["--muted", "--muted-foreground"],
      ["--accent", "--accent-foreground"],
      ["--destructive", "--destructive-foreground"],
    ];

    pairs.forEach(([bg, fg]) => {
      const bgColor = themeColors[bg];
      const fgColor = themeColors[fg];
      if (bgColor && fgColor) {
        results[`${bg}-${fg}`] = validateContrast(bgColor, fgColor, "AA", false);
      }
    });

    setValidationResults(results);
  }, [themeColors]);

  const handleColorChange = (key: string, value: string) => {
    setThemeColors((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    const newTheme: CustomTheme = {
      id: `custom-${Date.now()}`,
      name: themeName,
      colors: themeColors,
    };

    addCustomTheme(newTheme);
    setShowSaveDialog(false);
    setSaveSuccess(true);

    // Auto-hide success message after 3s
    setTimeout(() => setSaveSuccess(false), 3000);

    // Apply the new theme
    setTheme(newTheme.name);
  };

  const handleExportJSON = () => {
    const themeData = {
      name: themeName,
      colors: themeColors,
    };
    exportAndDownload({ colors: themeColors }, "json", `${themeName.toLowerCase().replace(/\s+/g, "-")}.json`);
  };

  const handleExportCSS = () => {
    const themeData = {
      colors: themeColors,
    };
    exportAndDownload(themeData, "css", `${themeName.toLowerCase().replace(/\s+/g, "-")}.css`);
  };

  const handleImport = () => {
    setImportError("");
    try {
      const parsed = JSON.parse(importJson);

      // Validate structure
      if (!parsed.colors || typeof parsed.colors !== "object") {
        setImportError("Invalid theme format: missing or invalid 'colors' object");
        return;
      }

      // Check if all required color tokens are present
      const requiredKeys = COLOR_TOKENS.map((t) => t.key);
      const missingKeys = requiredKeys.filter((key) => !(key in parsed.colors));

      if (missingKeys.length > 0) {
        setImportError(
          `Missing color tokens: ${missingKeys.join(", ")}`
        );
        return;
      }

      // Import successful
      setThemeColors(parsed.colors);
      if (parsed.name) {
        setThemeName(parsed.name);
      }
      setShowImportDialog(false);
      setImportJson("");
    } catch (error) {
      setImportError("Invalid JSON format");
    }
  };

  const handleLoadPreset = (presetId: string) => {
    const preset = defaultThemes.find((t) => t.id === presetId);
    if (preset) {
      setThemeColors(preset.colors);
      setThemeName(`${preset.name} (Custom)`);
    }
  };

  const handleClearCache = () => {
    try {
      clearThemeCache();
      setCacheCleared(true);
      setShowClearCacheDialog(false);

      // Auto-hide success message after 3s
      setTimeout(() => setCacheCleared(false), 3000);

      // Reset to default theme
      setTheme("default-light");
    } catch (error) {
      console.error("Failed to clear cache:", error);
    }
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
  };

  const hasContrastIssues = Object.values(validationResults).some((v) => !v);

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Palette className="h-8 w-8" />
            Theme Customizer
          </h1>
          <p className="text-muted-foreground mt-2">
            Create and customize your own themes with live preview and WCAG validation.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowImportDialog(true)}>
            <Upload className="h-4 w-4 mr-2" />
            Import JSON
          </Button>
          <Button variant="outline" onClick={handleExportJSON}>
            <Download className="h-4 w-4 mr-2" />
            Export JSON
          </Button>
          <Button variant="outline" onClick={handleExportCSS}>
            <Download className="h-4 w-4 mr-2" />
            Export CSS
          </Button>
          <Button
            variant="outline"
            onClick={() => setShowClearCacheDialog(true)}
            title={`Cache size: ${formatBytes(cacheSize)}`}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Clear Cache
          </Button>
          <Button onClick={() => setShowSaveDialog(true)}>
            <Save className="h-4 w-4 mr-2" />
            Save Theme
          </Button>
        </div>
      </div>

      {/* Success Alert */}
      {saveSuccess && (
        <Alert className="border-green-500 bg-green-50 dark:bg-green-950">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-600">
            Theme saved successfully! You can now use it from the theme gallery.
          </AlertDescription>
        </Alert>
      )}

      {/* Cache Cleared Alert */}
      {cacheCleared && (
        <Alert className="border-blue-500 bg-blue-50 dark:bg-blue-950">
          <CheckCircle2 className="h-4 w-4 text-blue-600" />
          <AlertDescription className="text-blue-600">
            Theme cache cleared successfully! All custom themes and favorites have been removed.
          </AlertDescription>
        </Alert>
      )}

      {/* Contrast Validation Warning */}
      {hasContrastIssues && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Some color combinations do not meet WCAG AA contrast requirements. Please review the
            validation indicators below.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Editor Panel */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Theme Details</CardTitle>
              <CardDescription>
                Give your theme a unique name and customize the colors
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="theme-name">Theme Name</Label>
                <Input
                  id="theme-name"
                  value={themeName}
                  onChange={(e) => setThemeName(e.target.value)}
                  placeholder="My Awesome Theme"
                />
              </div>

              <div>
                <Label className="mb-3 block">Load from Preset</Label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {defaultThemes.slice(0, 6).map((preset) => (
                    <Button
                      key={preset.id}
                      variant="outline"
                      size="sm"
                      onClick={() => handleLoadPreset(preset.id)}
                    >
                      {preset.name}
                    </Button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Color Tokens</CardTitle>
              <CardDescription>
                Customize each color token. Values should be in HSL format (e.g., "200 50% 50%")
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="base">
                <TabsList className="mb-4">
                  <TabsTrigger value="base">Base</TabsTrigger>
                  <TabsTrigger value="components">Components</TabsTrigger>
                  <TabsTrigger value="states">States</TabsTrigger>
                </TabsList>

                <TabsContent value="base" className="space-y-6">
                  {COLOR_TOKENS.filter((t) =>
                    ["--background", "--foreground", "--primary", "--primary-foreground"].includes(
                      t.key
                    )
                  ).map((token) => (
                    <ColorPicker
                      key={token.key}
                      label={token.label}
                      description={token.description}
                      value={themeColors[token.key] || "0 0% 100%"}
                      onChange={(value) => handleColorChange(token.key, value)}
                    />
                  ))}
                </TabsContent>

                <TabsContent value="components" className="space-y-6">
                  {COLOR_TOKENS.filter((t) =>
                    [
                      "--card",
                      "--card-foreground",
                      "--popover",
                      "--popover-foreground",
                      "--border",
                      "--input",
                      "--ring",
                    ].includes(t.key)
                  ).map((token) => (
                    <ColorPicker
                      key={token.key}
                      label={token.label}
                      description={token.description}
                      value={themeColors[token.key] || "0 0% 100%"}
                      onChange={(value) => handleColorChange(token.key, value)}
                    />
                  ))}
                </TabsContent>

                <TabsContent value="states" className="space-y-6">
                  {COLOR_TOKENS.filter((t) =>
                    [
                      "--secondary",
                      "--secondary-foreground",
                      "--muted",
                      "--muted-foreground",
                      "--accent",
                      "--accent-foreground",
                      "--destructive",
                      "--destructive-foreground",
                    ].includes(t.key)
                  ).map((token) => (
                    <ColorPicker
                      key={token.key}
                      label={token.label}
                      description={token.description}
                      value={themeColors[token.key] || "0 0% 100%"}
                      onChange={(value) => handleColorChange(token.key, value)}
                    />
                  ))}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* Preview Panel */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Live Preview
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 rounded-lg border-2" style={{
                backgroundColor: `hsl(${themeColors["--background"]})`,
                color: `hsl(${themeColors["--foreground"]})`,
              }}>
                <h3 className="font-semibold mb-2">Sample Content</h3>
                <p className="text-sm mb-3">This is how your theme will look.</p>
                <button
                  className="px-4 py-2 rounded-md text-sm font-medium"
                  style={{
                    backgroundColor: `hsl(${themeColors["--primary"]})`,
                    color: `hsl(${themeColors["--primary-foreground"]})`,
                  }}
                >
                  Primary Button
                </button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>WCAG Validation</CardTitle>
              <CardDescription>Contrast ratio checks (AA level)</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(validationResults).map(([pair, passes]) => {
                const [bg, fg] = pair.split("-");
                const bgLabel = COLOR_TOKENS.find((t) => t.key === bg)?.label || bg;
                const fgLabel = COLOR_TOKENS.find((t) => t.key === fg)?.label || fg;

                return (
                  <div
                    key={pair}
                    className="flex items-center justify-between p-2 rounded border"
                  >
                    <span className="text-sm">
                      {bgLabel} / {fgLabel}
                    </span>
                    {passes ? (
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-destructive" />
                    )}
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Save Dialog */}
      <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Save Custom Theme</DialogTitle>
            <DialogDescription>
              Your theme will be saved to local storage and available in the theme gallery.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Theme Name</Label>
              <Input
                value={themeName}
                onChange={(e) => setThemeName(e.target.value)}
                placeholder="My Awesome Theme"
              />
            </div>
            {hasContrastIssues && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  This theme has contrast issues. It may not be accessible to all users.
                </AlertDescription>
              </Alert>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSaveDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave}>Save Theme</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Import Dialog */}
      <Dialog open={showImportDialog} onOpenChange={setShowImportDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Import Theme from JSON</DialogTitle>
            <DialogDescription>
              Paste your theme JSON below. The format should match the exported theme structure.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="import-json">Theme JSON</Label>
              <textarea
                id="import-json"
                value={importJson}
                onChange={(e) => setImportJson(e.target.value)}
                className="w-full h-64 p-3 border rounded-md font-mono text-sm"
                placeholder='{\n  "name": "My Theme",\n  "colors": {\n    "--background": "0 0% 100%",\n    ...\n  }\n}'
              />
            </div>
            {importError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{importError}</AlertDescription>
              </Alert>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setShowImportDialog(false);
              setImportJson("");
              setImportError("");
            }}>
              Cancel
            </Button>
            <Button onClick={handleImport}>Import</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Clear Cache Dialog */}
      <Dialog open={showClearCacheDialog} onOpenChange={setShowClearCacheDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Clear Theme Cache</DialogTitle>
            <DialogDescription>
              This will remove all custom themes, favorites, and reset to the default theme.
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Current cache size: <strong>{formatBytes(cacheSize)}</strong>
              </AlertDescription>
            </Alert>
            <p className="text-sm text-muted-foreground">
              All your custom themes and preferences will be permanently deleted.
              You can create new themes after clearing the cache.
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowClearCacheDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleClearCache}>
              <Trash2 className="h-4 w-4 mr-2" />
              Clear Cache
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
