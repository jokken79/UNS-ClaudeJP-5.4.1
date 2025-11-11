# Yukyu E2E Tests with Playwright

This directory contains end-to-end tests for all Yukyu (休暇/vacation) pages using Playwright.

## 📋 Test Files

### Individual Page Tests
- `01-login-dashboard.spec.ts` - Login and dashboard tests
- `02-yukyu-main.spec.ts` - Yukyu main page (/yukyu)
- `03-yukyu-requests.spec.ts` - Yukyu requests page (/yukyu-requests)
- `04-yukyu-request-create.spec.ts` - Create request page (/yukyu-requests/create)
- `05-yukyu-reports.spec.ts` - Yukyu reports page (/yukyu-reports)
- `06-admin-yukyu.spec.ts` - Admin yukyu management (/admin/yukyu-management)
- `07-payroll-yukyu.spec.ts` - Payroll yukyu summary (/payroll/yukyu-summary)
- `08-yukyu-history.spec.ts` - Yukyu history page (/yukyu-history)

### Master Test Suite
- `yukyu-all.spec.ts` - Runs through all yukyu pages in one test

### Helpers
- `helpers/auth.ts` - Authentication helpers (login, logout, isLoggedIn)
- `helpers/common.ts` - Common test utilities (screenshots, navigation, verification)

## 🚀 Running Tests

### Prerequisites
```bash
# Make sure you're in the frontend directory
cd frontend

# Install dependencies (if not already done)
npm install
```

### Run All Tests
```bash
# Run all E2E tests
npm run test:e2e

# Run with UI mode (recommended for development)
npx playwright test --ui

# Run in headed mode (see browser)
npx playwright test --headed
```

### Run Specific Test Files
```bash
# Run only yukyu tests
npx playwright test yukyu

# Run specific test file
npx playwright test e2e/02-yukyu-main.spec.ts

# Run master suite only
npx playwright test e2e/yukyu-all.spec.ts
```

### Run with Debug Mode
```bash
# Debug mode (step through tests)
npx playwright test --debug

# Debug specific test
npx playwright test e2e/02-yukyu-main.spec.ts --debug
```

### View Test Results
```bash
# Show HTML report after tests
npx playwright show-report

# Run tests and open report automatically
npx playwright test --reporter=html
```

## 📸 Screenshots

Screenshots are automatically saved to `screenshots/` directory during test execution.

Each test captures screenshots at key points:
- Page load verification
- UI element verification
- Before/after interactions
- Error states (if any)

## 🔧 Configuration

Test configuration is in `playwright.config.ts` at the project root.

Key settings:
- **Base URL**: http://localhost:3000
- **Browser**: Chromium (Chrome)
- **Timeout**: 30 seconds for navigation, 10 seconds for actions
- **Screenshots**: On failure only
- **Video**: On retry
- **Traces**: On first retry

## 📝 Test Structure

Each test follows this pattern:

```typescript
test.describe('Page Name', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await login(page);
  });

  test('should verify page loads', async ({ page }) => {
    // Navigate to page
    await navigateAndWait(page, '/page-url');

    // Verify page loaded
    await verifyPageLoaded(page);

    // Take screenshot
    await takeScreenshot(page, 'test-name');

    // Assertions
    expect(page.url()).toContain('/page-url');
  });
});
```

## ✅ What's Tested

### For Each Yukyu Page:
1. ✅ Page loads without 404 errors
2. ✅ No JavaScript console errors
3. ✅ Page has expected UI elements
4. ✅ Navigation works correctly
5. ✅ Forms and inputs are present (where applicable)
6. ✅ Filter controls are present (where applicable)
7. ✅ Data tables/lists are displayed (where applicable)
8. ✅ Action buttons are available (where applicable)

## 🔐 Authentication

All tests use the admin credentials defined in `helpers/auth.ts`:
- Username: `admin`
- Password: `admin123`

The login helper automatically:
1. Navigates to login page
2. Fills in credentials
3. Submits form
4. Waits for successful navigation
5. Waits for page to be fully loaded

## 📊 Expected Test Results

When all tests pass, you should see output like:

```
✅ Login and Dashboard (4 tests)
✅ Yukyu Main Page (4 tests)
✅ Yukyu Requests Page (6 tests)
✅ Create Yukyu Request Page (7 tests)
✅ Yukyu Reports Page (7 tests)
✅ Admin Yukyu Management Page (8 tests)
✅ Payroll Yukyu Summary Page (9 tests)
✅ Yukyu History Page (10 tests)
✅ Yukyu System - Complete Flow (3 tests)

Total: 58 tests passed
```

## 🐛 Troubleshooting

### Tests Fail Due to Timeout
- Increase timeout in `playwright.config.ts`
- Check if dev server is running (`npm run dev`)
- Check if backend is running (`docker compose ps`)

### Tests Fail to Login
- Verify admin credentials in database
- Check backend logs: `docker compose logs backend`
- Verify login endpoint is working: http://localhost:8000/api/auth/login

### Page Not Found (404) Errors
- Verify the page exists in the frontend
- Check Next.js routing in `app/(dashboard)/` directory
- Review test URL paths

### Screenshots Not Saving
- Create `screenshots/` directory manually: `mkdir screenshots`
- Check file permissions
- Verify disk space

## 📚 Additional Resources

- [Playwright Documentation](https://playwright.dev)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright Test API](https://playwright.dev/docs/api/class-test)
- [Playwright Selectors](https://playwright.dev/docs/selectors)

## 🎯 Next Steps

After running these tests, you can:

1. **Add more detailed tests** for specific functionality
2. **Add visual regression tests** with Playwright screenshots
3. **Add accessibility tests** with @axe-core/playwright
4. **Add performance tests** with Playwright metrics
5. **Integrate with CI/CD** pipeline

## 💡 Tips

- Use `--ui` mode for debugging: `npx playwright test --ui`
- Use `--headed` to see the browser: `npx playwright test --headed`
- Use `--debug` for step-by-step execution: `npx playwright test --debug`
- Filter tests by name: `npx playwright test -g "should load"`
- Run tests in parallel: `npx playwright test --workers=4`

---

**Created**: 2025-11-11
**Last Updated**: 2025-11-11
**Test Coverage**: 8 Yukyu pages + 1 master flow test
