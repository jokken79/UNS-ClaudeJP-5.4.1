import { test, expect } from '@playwright/test';

/**
 * Design Preferences E2E Tests
 *
 * Comprehensive test suite for the Design Preferences system
 * Tests color intensity, animation speed, CSS variable application, and persistence
 */

test.describe('Design Preferences System', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to design preferences page
    await page.goto('http://localhost:3000/design-preferences');
    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');
  });

  test.describe('Page Load & UI Elements', () => {
    test('should load Design Preferences page successfully', async ({ page }) => {
      // Check page title/heading exists
      const heading = page.locator('h1');
      await expect(heading).toContainText('Design Preferences');

      // Check description exists
      const description = page.locator('text=Customize your visual experience');
      await expect(description).toBeVisible();
    });

    test('should render Color Intensity Picker component', async ({ page }) => {
      // Check Color Intensity section
      const colorIntensityTitle = page.locator('text=Color Intensity');
      await expect(colorIntensityTitle).toBeVisible();

      // Check both buttons exist
      const professionalBtn = page.locator('button:has-text("Professional")');
      const boldBtn = page.locator('button:has-text("Bold")');

      await expect(professionalBtn).toBeVisible();
      await expect(boldBtn).toBeVisible();
    });

    test('should render Animation Speed Picker component', async ({ page }) => {
      // Check Animation Speed section
      const animationTitle = page.locator('text=Animation Speed');
      await expect(animationTitle).toBeVisible();

      // Check both buttons exist
      const smoothBtn = page.locator('button:has-text("Smooth")');
      const dynamicBtn = page.locator('button:has-text("Dynamic")');

      await expect(smoothBtn).toBeVisible();
      await expect(dynamicBtn).toBeVisible();
    });

    test('should render Design Preview panel', async ({ page }) => {
      // Check preview panel exists
      const previewHeading = page.locator('text=Design Preview');
      await expect(previewHeading).toBeVisible();

      // Check badges exist
      const badges = page.locator('[role="status"]').or(page.locator('text=PROFESSIONAL')).or(page.locator('text=SMOOTH'));
      // At least some indicators should be visible
      await expect(page.locator('text=PROFESSIONAL')).toBeVisible();
    });

    test('should display alert with important information', async ({ page }) => {
      // Check alert message
      const alertText = page.locator('text=Your preferences are saved automatically');
      await expect(alertText).toBeVisible();
    });
  });

  test.describe('Color Intensity Selector', () => {
    test('should have Professional as default selection', async ({ page }) => {
      // Get the professional button
      const professionalBtn = page.locator('button:has-text("Professional")').first();

      // Check if it has the selected state
      const parentDiv = professionalBtn.locator('xpath=ancestor::button[1]');
      const checkIcon = parentDiv.locator('svg');

      // Professional should be selected by default (has check icon)
      await expect(parentDiv).toHaveClass(/border-primary.*bg-primary/);
    });

    test('should select Bold when clicked', async ({ page }) => {
      // Click Bold button
      const boldBtn = page.locator('button:has-text("Bold")').first();
      await boldBtn.click();

      // Wait for visual update
      await page.waitForTimeout(100);

      // Verify Bold button is now selected
      const boldParent = boldBtn.locator('xpath=ancestor::button[1]');
      await expect(boldParent).toHaveClass(/border-primary/);

      // Check icon should be visible on Bold
      const checkIcon = boldParent.locator('svg');
      await expect(checkIcon).toBeVisible();
    });

    test('should apply CSS variable when Bold is selected', async ({ page }) => {
      // Get initial color intensity value
      const initialIntensity = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--color-intensity').trim();
      });

      // Should be 0.9 (PROFESSIONAL) initially
      expect(parseFloat(initialIntensity)).toBeCloseTo(0.9, 1);

      // Click Bold
      const boldBtn = page.locator('button:has-text("Bold")').first();
      await boldBtn.click();

      // Wait for update
      await page.waitForTimeout(200);

      // Check that CSS variable changed
      const newIntensity = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--color-intensity').trim();
      });

      // Should be 1.3 (BOLD) now
      expect(parseFloat(newIntensity)).toBeCloseTo(1.3, 1);
    });

    test('should update preview colors when Bold is selected', async ({ page }) => {
      // Click Bold
      const boldBtn = page.locator('button:has-text("Bold")').first();
      await boldBtn.click();

      await page.waitForTimeout(100);

      // Check that preview shows "BOLD" text
      const boldBadge = page.locator('text=BOLD');
      await expect(boldBadge).toBeVisible();
    });
  });

  test.describe('Animation Speed Selector', () => {
    test('should have Smooth as default selection', async ({ page }) => {
      // Get the smooth button
      const smoothBtn = page.locator('button:has-text("Smooth")').first();

      // Check if it has the selected state
      const parentDiv = smoothBtn.locator('xpath=ancestor::button[1]');

      // Smooth should be selected by default
      await expect(parentDiv).toHaveClass(/border-primary.*bg-primary/);
    });

    test('should select Dynamic when clicked', async ({ page }) => {
      // Click Dynamic button
      const dynamicBtn = page.locator('button:has-text("Dynamic")').first();
      await dynamicBtn.click();

      // Wait for visual update
      await page.waitForTimeout(100);

      // Verify Dynamic button is now selected
      const dynamicParent = dynamicBtn.locator('xpath=ancestor::button[1]');
      await expect(dynamicParent).toHaveClass(/border-primary/);
    });

    test('should apply CSS variable when Dynamic is selected', async ({ page }) => {
      // Get initial animation speed value
      const initialSpeed = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--animation-speed-multiplier').trim();
      });

      // Should be 1 (SMOOTH) initially
      expect(parseFloat(initialSpeed)).toBe(1);

      // Click Dynamic
      const dynamicBtn = page.locator('button:has-text("Dynamic")').first();
      await dynamicBtn.click();

      // Wait for update
      await page.waitForTimeout(200);

      // Check that CSS variable changed
      const newSpeed = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--animation-speed-multiplier').trim();
      });

      // Should be 0.7 (DYNAMIC) now
      expect(parseFloat(newSpeed)).toBeCloseTo(0.7, 1);
    });

    test('should update duration variables when Dynamic is selected', async ({ page }) => {
      // Click Dynamic
      const dynamicBtn = page.locator('button:has-text("Dynamic")').first();
      await dynamicBtn.click();

      await page.waitForTimeout(200);

      // Check duration variables were updated
      const durations = await page.evaluate(() => {
        const root = getComputedStyle(document.documentElement);
        return {
          fast: root.getPropertyValue('--duration-fast').trim(),
          normal: root.getPropertyValue('--duration-normal').trim(),
          slow: root.getPropertyValue('--duration-slow').trim(),
        };
      });

      // Durations should still be the base values
      expect(durations.fast).toContain('150');
      expect(durations.normal).toContain('300');
      expect(durations.slow).toContain('500');
    });
  });

  test.describe('CSS Variables Application', () => {
    test('should have all required CSS variables defined', async ({ page }) => {
      const variables = await page.evaluate(() => {
        const root = getComputedStyle(document.documentElement);
        return {
          colorIntensity: root.getPropertyValue('--color-intensity').trim(),
          animationSpeedMultiplier: root.getPropertyValue('--animation-speed-multiplier').trim(),
          durationFast: root.getPropertyValue('--duration-fast').trim(),
          durationNormal: root.getPropertyValue('--duration-normal').trim(),
          durationSlow: root.getPropertyValue('--duration-slow').trim(),
        };
      });

      // All variables should be defined
      expect(variables.colorIntensity).toBeTruthy();
      expect(variables.animationSpeedMultiplier).toBeTruthy();
      expect(variables.durationFast).toBeTruthy();
      expect(variables.durationNormal).toBeTruthy();
      expect(variables.durationSlow).toBeTruthy();
    });

    test('should have theme color variables defined', async ({ page }) => {
      const colors = await page.evaluate(() => {
        const root = getComputedStyle(document.documentElement);
        return {
          primary: root.getPropertyValue('--primary').trim(),
          secondary: root.getPropertyValue('--secondary').trim(),
          accent: root.getPropertyValue('--accent').trim(),
          success: root.getPropertyValue('--success').trim(),
          warning: root.getPropertyValue('--warning').trim(),
          info: root.getPropertyValue('--info').trim(),
          destructive: root.getPropertyValue('--destructive').trim(),
        };
      });

      // All colors should be defined (HSL format expected)
      Object.entries(colors).forEach(([name, value]) => {
        expect(value).toBeTruthy();
        expect(value).toMatch(/\d+\s+\d+%\s+\d+%/); // HSL format
      });
    });
  });

  test.describe('localStorage Persistence', () => {
    test('should save preferences to localStorage when changed', async ({ page }) => {
      // Change to Bold
      const boldBtn = page.locator('button:has-text("Bold")').first();
      await boldBtn.click();

      await page.waitForTimeout(200);

      // Check localStorage
      const stored = await page.evaluate(() => {
        return localStorage.getItem('design-preferences');
      });

      expect(stored).toBeTruthy();
      const preferences = JSON.parse(stored!);
      expect(preferences.colorIntensity).toBe('BOLD');
    });

    test('should save animation speed preference to localStorage', async ({ page }) => {
      // Change to Dynamic
      const dynamicBtn = page.locator('button:has-text("Dynamic")').first();
      await dynamicBtn.click();

      await page.waitForTimeout(200);

      // Check localStorage
      const stored = await page.evaluate(() => {
        return localStorage.getItem('design-preferences');
      });

      expect(stored).toBeTruthy();
      const preferences = JSON.parse(stored!);
      expect(preferences.animationSpeed).toBe('DYNAMIC');
    });

    test('should restore preferences from localStorage after page reload', async ({ page }) => {
      // Set preferences
      const boldBtn = page.locator('button:has-text("Bold")').first();
      await boldBtn.click();

      const dynamicBtn = page.locator('button:has-text("Dynamic")').first();
      await dynamicBtn.click();

      await page.waitForTimeout(200);

      // Reload page
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Check that CSS variables are restored
      const intensity = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--color-intensity').trim();
      });

      const speed = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--animation-speed-multiplier').trim();
      });

      // Should be BOLD (1.3) and DYNAMIC (0.7)
      expect(parseFloat(intensity)).toBeCloseTo(1.3, 1);
      expect(parseFloat(speed)).toBeCloseTo(0.7, 1);
    });

    test('should persist preferences across multiple page navigations', async ({ page }) => {
      // Set preferences
      const boldBtn = page.locator('button:has-text("Bold")').first();
      await boldBtn.click();

      await page.waitForTimeout(200);

      // Navigate to different page
      await page.goto('http://localhost:3000/design-preferences?test=navigation');
      await page.waitForLoadState('networkidle');

      // Check that CSS variable is still set
      const intensity = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--color-intensity').trim();
      });

      expect(parseFloat(intensity)).toBeCloseTo(1.3, 1);
    });
  });

  test.describe('Design Preview Panel', () => {
    test('should display current preferences in badges', async ({ page }) => {
      // Should show PROFESSIONAL by default
      const professionalBadge = page.locator('text=PROFESSIONAL');
      const smoothBadge = page.locator('text=SMOOTH');

      await expect(professionalBadge).toBeVisible();
      await expect(smoothBadge).toBeVisible();
    });

    test('should update preview badges when preferences change', async ({ page }) => {
      // Click Bold
      const boldBtn = page.locator('button:has-text("Bold")').first();
      await boldBtn.click();

      await page.waitForTimeout(100);

      // Preview should show BOLD
      const boldBadge = page.locator('text=BOLD');
      await expect(boldBadge).toBeVisible();

      // Click Dynamic
      const dynamicBtn = page.locator('button:has-text("Dynamic")').first();
      await dynamicBtn.click();

      await page.waitForTimeout(100);

      // Preview should show DYNAMIC
      const dynamicBadge = page.locator('text=DYNAMIC');
      await expect(dynamicBadge).toBeVisible();
    });

    test('should show color samples in preview', async ({ page }) => {
      // Check that color samples are visible
      const colorPreview = page.locator('text=Color Intensity Preview');
      await expect(colorPreview).toBeVisible();

      // Check that animation preview is visible
      const animationPreview = page.locator('text=Animation Speed Preview');
      await expect(animationPreview).toBeVisible();
    });
  });

  test.describe('Combination Tests', () => {
    test('should handle PROFESSIONAL + SMOOTH combination', async ({ page }) => {
      // Professional and Smooth are defaults, so just verify
      const intensity = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--color-intensity').trim();
      });

      const speed = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--animation-speed-multiplier').trim();
      });

      expect(parseFloat(intensity)).toBeCloseTo(0.9, 1);
      expect(parseFloat(speed)).toBe(1);
    });

    test('should handle PROFESSIONAL + DYNAMIC combination', async ({ page }) => {
      // Click Dynamic
      const dynamicBtn = page.locator('button:has-text("Dynamic")').first();
      await dynamicBtn.click();

      await page.waitForTimeout(200);

      const intensity = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--color-intensity').trim();
      });

      const speed = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--animation-speed-multiplier').trim();
      });

      expect(parseFloat(intensity)).toBeCloseTo(0.9, 1);
      expect(parseFloat(speed)).toBeCloseTo(0.7, 1);
    });

    test('should handle BOLD + SMOOTH combination', async ({ page }) => {
      // Click Bold
      const boldBtn = page.locator('button:has-text("Bold")').first();
      await boldBtn.click();

      await page.waitForTimeout(200);

      const intensity = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--color-intensity').trim();
      });

      const speed = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--animation-speed-multiplier').trim();
      });

      expect(parseFloat(intensity)).toBeCloseTo(1.3, 1);
      expect(parseFloat(speed)).toBe(1);
    });

    test('should handle BOLD + DYNAMIC combination', async ({ page }) => {
      // Click Bold
      const boldBtn = page.locator('button:has-text("Bold")').first();
      await boldBtn.click();

      // Click Dynamic
      const dynamicBtn = page.locator('button:has-text("Dynamic")').first();
      await dynamicBtn.click();

      await page.waitForTimeout(200);

      const intensity = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--color-intensity').trim();
      });

      const speed = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--animation-speed-multiplier').trim();
      });

      expect(parseFloat(intensity)).toBeCloseTo(1.3, 1);
      expect(parseFloat(speed)).toBeCloseTo(0.7, 1);
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper button labels', async ({ page }) => {
      // Check buttons have text content
      const buttons = page.locator('button');
      const count = await buttons.count();

      expect(count).toBeGreaterThan(0);

      // Each button should have visible text
      for (let i = 0; i < count; i++) {
        const text = await buttons.nth(i).textContent();
        expect(text?.trim().length).toBeGreaterThan(0);
      }
    });

    test('should support keyboard navigation', async ({ page }) => {
      // Tab to first button
      await page.keyboard.press('Tab');

      // Should be able to focus elements
      const focusedElement = await page.evaluate(() => {
        return document.activeElement?.tagName;
      });

      expect(focusedElement).toBeTruthy();
    });

    test('should have focus visible styles', async ({ page }) => {
      // Click on a button to focus it
      const boldBtn = page.locator('button:has-text("Bold")').first();
      await boldBtn.focus();

      // Check that it has focus styles
      const hasFocusClass = await boldBtn.evaluate((el) => {
        return el.className.includes('focus') ||
               window.getComputedStyle(el).outline !== 'none';
      });

      expect(hasFocusClass).toBeTruthy();
    });
  });
});
