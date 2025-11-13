"use client";

import { useState, useEffect } from "react";
import { Palette, Monitor, Moon, Sun, Sparkles } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { themes as defaultThemes } from "@/lib/themes";
import { getCustomThemes } from "@/lib/custom-themes";

export default function AppearanceSettingsPage() {
  const { theme, setTheme, systemTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [customThemes, setCustomThemes] = useState<any[]>([]);
  const [themeMode, setThemeMode] = useState<"light" | "dark" | "system">("system");
  const [animationSpeed, setAnimationSpeed] = useState<"disable" | "smooth" | "normal" | "energetic">("normal");
  const [compactMode, setCompactMode] = useState(false);

  useEffect(() => {
    setMounted(true);
    setCustomThemes(getCustomThemes());

    // Load preferences from localStorage
    try {
      const animSpeed = localStorage.getItem("animation-speed") as "disable" | "smooth" | "normal" | "energetic" | null;
      if (animSpeed !== null) {
        setAnimationSpeed(animSpeed);
      }

      const compact = localStorage.getItem("compact-mode");
      if (compact !== null) {
        setCompactMode(compact === "true");
      }
    } catch (error) {
      console.error("Error loading preferences:", error);
    }
  }, []);

  useEffect(() => {
    if (theme === "default-light") {
      setThemeMode("light");
    } else if (theme === "default-dark") {
      setThemeMode("dark");
    } else if (theme === "system") {
      setThemeMode("system");
    }
  }, [theme]);

  const handleThemeModeChange = (mode: "light" | "dark" | "system") => {
    setThemeMode(mode);
    if (mode === "light") {
      setTheme("default-light");
    } else if (mode === "dark") {
      setTheme("default-dark");
    } else {
      setTheme("system");
    }
  };

  const handleAnimationSpeedChange = (speed: "disable" | "smooth" | "normal" | "energetic") => {
    setAnimationSpeed(speed);
    localStorage.setItem("animation-speed", speed);

    // Remove all animation classes first
    document.documentElement.classList.remove("no-animations", "animations-smooth", "animations-energetic");

    // Apply the selected animation class
    if (speed === "disable") {
      document.documentElement.classList.add("no-animations");
    } else if (speed === "smooth") {
      document.documentElement.classList.add("animations-smooth");
    } else if (speed === "energetic") {
      document.documentElement.classList.add("animations-energetic");
    }
    // "normal" doesn't need a class - it's the default
  };

  const handleCompactModeChange = (enabled: boolean) => {
    setCompactMode(enabled);
    localStorage.setItem("compact-mode", String(enabled));

    // Apply compact mode to document
    if (enabled) {
      document.documentElement.classList.add("compact-mode");
    } else {
      document.documentElement.classList.remove("compact-mode");
    }
  };

  if (!mounted) {
    return null;
  }

  const allThemes = [...defaultThemes, ...customThemes];
  const currentThemeObj = allThemes.find((t) => t.name === theme);

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Palette className="h-8 w-8" />
          Appearance Settings
        </h1>
        <p className="text-muted-foreground mt-2">
          Customize the look and feel of your application interface.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Settings */}
        <div className="lg:col-span-2 space-y-6">
          {/* Theme Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Theme</CardTitle>
              <CardDescription>
                Select your preferred theme or create a custom one
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Mode Selection */}
              <div className="space-y-3">
                <Label>Color Mode</Label>
                <RadioGroup
                  value={themeMode}
                  onValueChange={(value: any) => handleThemeModeChange(value)}
                  className="grid grid-cols-3 gap-4"
                >
                  <div>
                    <RadioGroupItem
                      value="light"
                      id="light"
                      className="peer sr-only"
                    />
                    <Label
                      htmlFor="light"
                      className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                    >
                      <Sun className="mb-3 h-6 w-6" />
                      <span className="text-sm font-medium">Light</span>
                    </Label>
                  </div>
                  <div>
                    <RadioGroupItem
                      value="dark"
                      id="dark"
                      className="peer sr-only"
                    />
                    <Label
                      htmlFor="dark"
                      className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                    >
                      <Moon className="mb-3 h-6 w-6" />
                      <span className="text-sm font-medium">Dark</span>
                    </Label>
                  </div>
                  <div>
                    <RadioGroupItem
                      value="system"
                      id="system"
                      className="peer sr-only"
                    />
                    <Label
                      htmlFor="system"
                      className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                    >
                      <Monitor className="mb-3 h-6 w-6" />
                      <span className="text-sm font-medium">System</span>
                    </Label>
                  </div>
                </RadioGroup>
              </div>

              <Separator />

              {/* Quick Theme Access */}
              <div className="space-y-3">
                <Label>Quick Theme Access</Label>
                <div className="flex gap-2 flex-wrap">
                  <Button
                    variant="outline"
                    onClick={() => (window.location.href = "/themes")}
                  >
                    <Palette className="h-4 w-4 mr-2" />
                    Browse Themes
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => (window.location.href = "/themes/customizer")}
                  >
                    <Sparkles className="h-4 w-4 mr-2" />
                    Create Custom Theme
                  </Button>
                </div>
              </div>

              {currentThemeObj && (
                <>
                  <Separator />
                  <div className="space-y-2">
                    <Label>Current Theme</Label>
                    <div className="p-3 border rounded-md bg-muted/50">
                      <p className="font-medium">{currentThemeObj.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {defaultThemes.some((t) => t.id === currentThemeObj.id)
                          ? "Predefined theme"
                          : "Custom theme"}
                      </p>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Interface Preferences */}
          <Card>
            <CardHeader>
              <CardTitle>Interface Preferences</CardTitle>
              <CardDescription>
                Customize how the interface behaves and appears
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-3">
                <div>
                  <Label>Animation Speed</Label>
                  <p className="text-sm text-muted-foreground">
                    Control how fast animations and transitions appear
                  </p>
                </div>
                <RadioGroup
                  value={animationSpeed}
                  onValueChange={(value: any) => handleAnimationSpeedChange(value)}
                  className="grid grid-cols-2 gap-3"
                >
                  <div>
                    <RadioGroupItem
                      value="disable"
                      id="disable"
                      className="peer sr-only"
                    />
                    <Label
                      htmlFor="disable"
                      className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-3 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                    >
                      <span className="text-sm font-medium">Disable</span>
                      <span className="text-xs text-muted-foreground mt-1">No animations</span>
                    </Label>
                  </div>
                  <div>
                    <RadioGroupItem
                      value="smooth"
                      id="smooth"
                      className="peer sr-only"
                    />
                    <Label
                      htmlFor="smooth"
                      className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-3 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                    >
                      <span className="text-sm font-medium">Smooth</span>
                      <span className="text-xs text-muted-foreground mt-1">Relaxed pace</span>
                    </Label>
                  </div>
                  <div>
                    <RadioGroupItem
                      value="normal"
                      id="normal"
                      className="peer sr-only"
                    />
                    <Label
                      htmlFor="normal"
                      className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-3 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                    >
                      <span className="text-sm font-medium">Normal</span>
                      <span className="text-xs text-muted-foreground mt-1">Balanced</span>
                    </Label>
                  </div>
                  <div>
                    <RadioGroupItem
                      value="energetic"
                      id="energetic"
                      className="peer sr-only"
                    />
                    <Label
                      htmlFor="energetic"
                      className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-3 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                    >
                      <span className="text-sm font-medium">Energetic</span>
                      <span className="text-xs text-muted-foreground mt-1">Fast & snappy</span>
                    </Label>
                  </div>
                </RadioGroup>
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="compact">Compact Mode</Label>
                  <p className="text-sm text-muted-foreground">
                    Reduce spacing for a more compact interface
                  </p>
                </div>
                <Switch
                  id="compact"
                  checked={compactMode}
                  onCheckedChange={handleCompactModeChange}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Info Panel */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Theme Statistics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Predefined Themes</span>
                <span className="font-semibold">{defaultThemes.length}</span>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Custom Themes</span>
                <span className="font-semibold">{customThemes.length}</span>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Total Available</span>
                <span className="font-semibold">{allThemes.length}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Tips</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <p>
                • Browse the theme gallery to find the perfect look for your workspace
              </p>
              <p>
                • Create custom themes with the theme customizer
              </p>
              <p>
                • Export your custom themes as JSON to share with others
              </p>
              <p>
                • All themes are validated for WCAG contrast requirements
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
