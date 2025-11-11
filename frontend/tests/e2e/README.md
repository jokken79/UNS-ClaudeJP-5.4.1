# E2E Tests - UNS-ClaudeJP 5.4.1

## Overview

This directory contains Playwright E2E (End-to-End) tests for the UNS-ClaudeJP application. These tests validate critical user workflows from the frontend perspective.

## Test Files

### 1. `apartments.spec.ts` - Apartment Assignment Workflow
Tests the complete apartment assignment flow:
- ✅ View apartments list
- ✅ View apartment assignments
- ✅ Navigate to create assignment form
- ✅ View apartment statistics
- ✅ Handle pagination

### 2. `payroll.spec.ts` - Payroll Run Workflow
Tests the complete payroll processing flow:
- ✅ View payroll runs list
- ✅ Display payroll run statuses
- ✅ Navigate to create payroll run form
- ✅ View payroll summary statistics
- ✅ Filter payroll runs by status
- ✅ View payroll run details page
- ✅ Handle approval workflow

### 3. `candidates.spec.ts` - Candidate Registration Workflow
Tests the complete candidate management flow:
- ✅ View candidates list
- ✅ Display candidate status badges
- ✅ Navigate to create candidate form
- ✅ Search candidates
- ✅ Filter candidates by status
- ✅ View candidate details page
- ✅ Handle OCR upload
- ✅ Display candidate statistics
- ✅ Paginate through candidates list

## Prerequisites

1. **Docker Services Running**
   ```bash
   cd scripts
   START.bat  # Windows
   ```

2. **Frontend Server Running**
   ```bash
   npm run dev  # Should be running at http://localhost:3000
   ```

3. **Backend API Running**
   ```bash
   # Backend should be running at http://localhost:8000
   ```

4. **Test User Exists**
   - Username: `admin`
   - Password: `admin123`

## Running Tests

### Run All E2E Tests
```bash
npm run test:e2e
```

### Run Specific Test File
```bash
npx playwright test apartments.spec.ts
npx playwright test payroll.spec.ts
npx playwright test candidates.spec.ts
```

### Run Tests in UI Mode (Interactive)
```bash
npx playwright test --ui
```

### Run Tests in Headed Mode (See Browser)
```bash
npx playwright test --headed
```

### Run Tests with Debug Mode
```bash
npx playwright test --debug
```

### Run Specific Test by Name
```bash
npx playwright test -g "should view apartments list"
```

## Test Reports

After running tests, view the HTML report:
```bash
npx playwright show-report
```

## Configuration

Tests are configured in `playwright.config.ts`:
- **Base URL**: http://localhost:3000
- **Timeout**: 30 seconds per test
- **Retries**: 2 on CI, 0 locally
- **Browsers**: Chromium (default)
- **Screenshots**: Only on failure
- **Videos**: Retained on failure
- **Traces**: On first retry

## Writing New Tests

When adding new E2E tests:

1. **Follow existing patterns**
   - Use `test.beforeEach()` for login
   - Wait for elements with timeouts
   - Use descriptive test names

2. **Use proper selectors**
   ```typescript
   // Good - role-based or data attributes
   await page.getByRole('button', { name: 'Submit' });
   await page.locator('[data-testid="candidate-form"]');

   // Avoid - fragile class or ID selectors
   await page.locator('#btn-123');
   await page.locator('.some-dynamic-class');
   ```

3. **Handle async operations**
   ```typescript
   // Wait for navigation
   await page.waitForURL('/dashboard');

   // Wait for element
   await page.waitForSelector('h1', { timeout: 5000 });

   // Wait for network idle
   await page.waitForLoadState('networkidle');
   ```

4. **Add assertions**
   ```typescript
   expect(page.url()).toContain('/candidates');
   expect(await element.textContent()).toMatch(/expected text/i);
   ```

## Troubleshooting

### Tests Failing with Timeout

**Issue**: Tests timeout waiting for elements

**Solutions**:
1. Increase timeout in test:
   ```typescript
   test.setTimeout(60000); // 60 seconds
   ```

2. Wait for page to load:
   ```typescript
   await page.waitForLoadState('networkidle');
   ```

3. Check if element exists before interacting:
   ```typescript
   const element = await page.locator('button').count();
   if (element > 0) {
     await page.locator('button').click();
   }
   ```

### Tests Failing on Login

**Issue**: Cannot login as admin

**Solutions**:
1. Verify admin user exists:
   ```bash
   docker exec uns-claudejp-backend python scripts/create_admin_user.py
   ```

2. Check credentials in test match database

### Tests Failing with "Element not found"

**Issue**: Elements not found on page

**Solutions**:
1. Add wait before interaction:
   ```typescript
   await page.waitForTimeout(2000);
   ```

2. Use more flexible selectors:
   ```typescript
   await page.locator('button, a').filter({ hasText: /create/i });
   ```

3. Check if page is fully loaded

### Browser Doesn't Close

**Issue**: Browser windows left open after tests

**Solutions**:
1. Make sure tests complete properly
2. Run: `npx playwright test --headed` to see what's happening
3. Close manually if needed

## Best Practices

1. **Keep tests independent** - Each test should be able to run alone
2. **Use realistic data** - Test with data that mimics production
3. **Test happy paths first** - Core workflows should pass
4. **Add error scenarios** - Test validation and error handling
5. **Keep tests fast** - Use `test.setTimeout()` sparingly
6. **Clean up after tests** - Delete test data if created
7. **Use page objects** - For complex pages, create page object models

## CI/CD Integration

To run E2E tests in CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Install Playwright
  run: npx playwright install --with-deps

- name: Run E2E Tests
  run: npm run test:e2e

- name: Upload Test Results
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: playwright-report
    path: playwright-report/
```

## Next Steps

To improve E2E test coverage:

1. **Add more workflows**
   - Employee management
   - Factory CRUD
   - Timer card entry
   - Request submission

2. **Add error scenarios**
   - Invalid form data
   - Unauthorized access
   - Network failures

3. **Add visual regression**
   ```typescript
   await expect(page).toHaveScreenshot();
   ```

4. **Add API mocking**
   ```typescript
   await page.route('**/api/candidates', route => {
     route.fulfill({ json: mockData });
   });
   ```

---

**Last Updated**: 2025-11-11
**Version**: 5.4.1
**By**: Claude AI Agent
