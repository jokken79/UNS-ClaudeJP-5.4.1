import { test, expect } from '@playwright/test';

/**
 * E2E Tests for LolaAppJp
 *
 * Tests:
 * 1. Login flow
 * 2. Navigation to all pages
 * 3. Basic functionality of each module
 */

const BASE_URL = 'http://localhost:3000';
const API_URL = 'http://localhost:8000';

test.describe('Authentication Flow', () => {
  test('should show login page', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    // Check page title
    await expect(page.locator('h1')).toContainText('LolaAppJp');

    // Check form elements exist
    await expect(page.locator('input[type="text"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    // Fill login form
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');

    // Click login button
    await page.click('button[type="submit"]');

    // Wait for navigation
    await page.waitForURL(`${BASE_URL}/dashboard`);

    // Verify redirect to dashboard
    await expect(page).toHaveURL(`${BASE_URL}/dashboard`);
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    // Fill with invalid credentials
    await page.fill('input[type="text"]', 'invaliduser');
    await page.fill('input[type="password"]', 'wrongpassword');

    // Click login
    await page.click('button[type="submit"]');

    // Should show error message
    await expect(page.locator('.text-red-600')).toBeVisible();
  });
});

test.describe('Dashboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(`${BASE_URL}/dashboard`);
  });

  test('should load dashboard page', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('LolaAppJp');
    await expect(page.locator('text=HR Management System')).toBeVisible();
  });

  test('should navigate to candidates page', async ({ page }) => {
    await page.goto(`${BASE_URL}/candidates`);

    await expect(page.locator('h1')).toContainText('Candidate Management');
    await expect(page.locator('text=履歴書')).toBeVisible();
  });

  test('should navigate to employees page', async ({ page }) => {
    await page.goto(`${BASE_URL}/employees`);

    await expect(page.locator('h1')).toContainText('Employee Management');
    await expect(page.locator('text=派遣社員')).toBeVisible();
  });

  test('should navigate to companies page', async ({ page }) => {
    await page.goto(`${BASE_URL}/companies`);

    await expect(page.locator('h1')).toContainText('Client Companies');
    await expect(page.locator('text=派遣先企業')).toBeVisible();
  });

  test('should navigate to apartments page', async ({ page }) => {
    await page.goto(`${BASE_URL}/apartments`);

    await expect(page.locator('h1')).toContainText('Apartment Management');
    await expect(page.locator('text=社員寮')).toBeVisible();
  });

  test('should navigate to factories page', async ({ page }) => {
    await page.goto(`${BASE_URL}/factories`);

    await expect(page.locator('h1')).toContainText('Factory Management');
    await expect(page.locator('text=工場')).toBeVisible();
  });

  test('should navigate to yukyu page', async ({ page }) => {
    await page.goto(`${BASE_URL}/yukyu`);

    await expect(page.locator('h1')).toContainText('Yukyu Management');
    await expect(page.locator('text=有給休暇')).toBeVisible();
  });

  test('should navigate to timercards page', async ({ page }) => {
    await page.goto(`${BASE_URL}/timercards`);

    await expect(page.locator('h1')).toContainText('Timer Cards');
    await expect(page.locator('text=タイムカード')).toBeVisible();
  });

  test('should navigate to payroll page', async ({ page }) => {
    await page.goto(`${BASE_URL}/payroll`);

    await expect(page.locator('h1')).toContainText('Payroll Calculations');
    await expect(page.locator('text=給与')).toBeVisible();
  });

  test('should navigate to requests page', async ({ page }) => {
    await page.goto(`${BASE_URL}/requests`);

    await expect(page.locator('h1')).toContainText('Request Workflow');
    await expect(page.locator('text=申請管理')).toBeVisible();
  });

  test('should navigate to reports page', async ({ page }) => {
    await page.goto(`${BASE_URL}/reports`);

    await expect(page.locator('h1')).toContainText('Reports');
    await expect(page.locator('text=レポート')).toBeVisible();
  });
});

test.describe('Candidates Page Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(`${BASE_URL}/dashboard`);
    await page.goto(`${BASE_URL}/candidates`);
  });

  test('should have search functionality', async ({ page }) => {
    // Check search input exists
    const searchInput = page.locator('input[placeholder*="Search"]');
    await expect(searchInput).toBeVisible();
  });

  test('should have status filter', async ({ page }) => {
    // Check status filter exists
    const statusFilter = page.locator('select').first();
    await expect(statusFilter).toBeVisible();
  });

  test('should have refresh button', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Refresh")');
    await expect(refreshButton).toBeVisible();
  });

  test('should display table headers', async ({ page }) => {
    await expect(page.locator('th:has-text("履歴書 ID")')).toBeVisible();
    await expect(page.locator('th:has-text("Name (Kanji)")')).toBeVisible();
    await expect(page.locator('th:has-text("Status")')).toBeVisible();
  });
});

test.describe('Employees Page Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(`${BASE_URL}/dashboard`);
    await page.goto(`${BASE_URL}/employees`);
  });

  test('should display employee statistics', async ({ page }) => {
    // Wait for data to load
    await page.waitForTimeout(1000);

    // Check summary section exists
    await expect(page.locator('text=Summary')).toBeVisible();
  });

  test('should have filter controls', async ({ page }) => {
    await expect(page.locator('input[placeholder*="Search"]')).toBeVisible();
    await expect(page.locator('select')).toBeVisible();
  });
});

test.describe('Yukyu Page Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(`${BASE_URL}/dashboard`);
    await page.goto(`${BASE_URL}/yukyu`);
  });

  test('should have employee ID search', async ({ page }) => {
    const employeeInput = page.locator('input[placeholder*="Employee ID"]');
    await expect(employeeInput).toBeVisible();
  });

  test('should have search button', async ({ page }) => {
    const searchButton = page.locator('button:has-text("Search")');
    await expect(searchButton).toBeVisible();
  });

  test('should show LIFO information', async ({ page }) => {
    await expect(page.locator('text=LIFO')).toBeVisible();
  });
});

test.describe('Timercards Page Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(`${BASE_URL}/dashboard`);
    await page.goto(`${BASE_URL}/timercards`);
  });

  test('should have period selectors', async ({ page }) => {
    // Check for year and month selectors
    const yearSelect = page.locator('select').first();
    const monthSelect = page.locator('select').nth(1);

    await expect(yearSelect).toBeVisible();
    await expect(monthSelect).toBeVisible();
  });

  test('should show hour categories', async ({ page }) => {
    await expect(page.locator('text=Regular Hours')).toBeVisible();
    await expect(page.locator('text=Overtime Hours')).toBeVisible();
    await expect(page.locator('text=Night Hours')).toBeVisible();
    await expect(page.locator('text=Holiday Hours')).toBeVisible();
  });
});

test.describe('Payroll Page Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(`${BASE_URL}/dashboard`);
    await page.goto(`${BASE_URL}/payroll`);
  });

  test('should have calculation form', async ({ page }) => {
    await expect(page.locator('input[placeholder*="Employee ID"]')).toBeVisible();
    await expect(page.locator('button:has-text("Calculate")')).toBeVisible();
  });

  test('should show Japanese terms', async ({ page }) => {
    await expect(page.locator('text=給与')).toBeVisible();
  });
});

test.describe('Requests Page Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(`${BASE_URL}/dashboard`);
    await page.goto(`${BASE_URL}/requests`);
  });

  test('should have request type filter', async ({ page }) => {
    const typeFilter = page.locator('select').first();
    await expect(typeFilter).toBeVisible();

    // Check for NYUSHA option
    await expect(typeFilter).toContainText('入社連絡票');
  });

  test('should have status filter', async ({ page }) => {
    const statusFilter = page.locator('select').nth(1);
    await expect(statusFilter).toBeVisible();
  });

  test('should show summary cards', async ({ page }) => {
    await expect(page.locator('text=DRAFT')).toBeVisible();
    await expect(page.locator('text=PENDING')).toBeVisible();
    await expect(page.locator('text=APPROVED')).toBeVisible();
    await expect(page.locator('text=REJECTED')).toBeVisible();
  });
});

test.describe('Reports Page Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(`${BASE_URL}/dashboard`);
    await page.goto(`${BASE_URL}/reports`);
  });

  test('should display report types', async ({ page }) => {
    await expect(page.locator('text=Employee Summary Report')).toBeVisible();
    await expect(page.locator('text=Payroll Summary Report')).toBeVisible();
    await expect(page.locator('text=Attendance Summary')).toBeVisible();
  });

  test('should have report options', async ({ page }) => {
    await expect(page.locator('text=Year')).toBeVisible();
    await expect(page.locator('text=Month')).toBeVisible();
    await expect(page.locator('text=Format')).toBeVisible();
  });

  test('should have generate button', async ({ page }) => {
    const generateButton = page.locator('button:has-text("Generate Report")');
    await expect(generateButton).toBeVisible();
  });
});

test.describe('Dark Mode Support', () => {
  test('should support dark mode classes', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    // Check for dark mode classes
    const html = await page.locator('html').innerHTML();
    expect(html).toContain('dark:');
  });
});

test.describe('Responsive Design', () => {
  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/login`);

    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('input[type="text"]')).toBeVisible();
  });

  test('should be responsive on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(`${BASE_URL}/login`);

    await expect(page.locator('h1')).toBeVisible();
  });
});
