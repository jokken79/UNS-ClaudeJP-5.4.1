# BUILD SCRIPTS AND VALIDATION DETAILED ANALYSIS

## FRONTEND BUILD SCRIPTS (from package.json)

```json
"scripts": {
  "dev": "next dev",                                    // Development with Turbopack
  "build": "next build",                                // Production build
  "start": "next start",                                // Production server
  "lint": "eslint . --max-warnings 0 --format=json",  // Lint with JSON output
  "lint:fix": "eslint . --fix",                        // Auto-fix linting issues
  "format": "prettier ...",                             // Code formatting
  "format:check": "prettier --check ...",              // Check formatting
  "typecheck": "tsc --noEmit",                         // TypeScript validation
  "test": "vitest run",                                // Unit tests
  "test:watch": "vitest",                              // Watch mode tests
  "test:e2e": "playwright test",                       // E2E tests
  "test:e2e:ui": "playwright test --ui",              // E2E UI mode
  "test:e2e:headed": "playwright test --headed",      // E2E with browser visible
  "test:e2e:debug": "playwright test --debug",        // E2E debug mode
  "test:e2e:yukyu": "playwright test e2e/*yukyu*"    // Specific E2E tests
}
```

## BUILD FLOW ANALYSIS

### Current Flow (Development):
```
npm run dev
  → next dev
  → Turbopack bundler
  → Hot reload enabled
  → TypeScript errors NOT validated
  → NO linting
  → NO tests required
```

### Current Flow (Production Docker):
```
docker build (frontend)
  → FROM node:20-alpine
  → npm install --legacy-peer-deps
  → npm run build
    → next build
    → Bundles code with Turbopack
    → TypeScript: ignoreBuildErrors = true (SKIPS ALL ERRORS)
    → NO type checking step
    → NO linting step
    → NO tests
  → Creates .next/standalone
  → Final image runs: node server.js
```

## VALIDATION GAPS

### Missing Before Build:
```bash
npm run lint          # NOT run before build
npm run typecheck     # NOT run before build
npm run format:check  # NOT run before build
npm test              # NOT run before build
```

### Missing in Docker:
The Dockerfile.frontend does NOT include validation:
```dockerfile
# Missing:
RUN npm run typecheck
RUN npm run lint
RUN npm test

# Current (line 57):
RUN npm run build  # ← This ignores TypeScript errors!
```

## SPECIFIC BUILD ISSUES

### Issue 1: Framer-Motion Type Conflicts

**File:** frontend/next.config.ts (lines 60-63)
```typescript
// Temporary: ignore TypeScript errors during build (framer-motion conflicts)
typescript: {
  ignoreBuildErrors: true,
},
```

**Analysis:**
- framer-motion ^11.15.0 has type issues with React 19.0.0
- Instead of fixing, project ignores ALL TypeScript errors
- This is a band-aid solution, not a fix
- Comment says "Temporary" but has been permanent

**Impact:**
- Real type errors are hidden
- Production builds may contain broken code
- No way to distinguish framer-motion errors from actual code errors

**Solutions:**
1. Update framer-motion to latest version compatible with React 19
2. Use @ts-ignore comments for specific errors
3. Fork framer-motion and fix types locally
4. Remove framer-motion if not essential

### Issue 2: ESLint Report Generation

**File:** frontend/package.json (line 10)
```json
"lint": "eslint . --max-warnings 0 --format=json --output-file=eslint-report.json || true"
```

**Problems:**
- `|| true` means ESLint failures are ignored (always succeeds)
- JSON output written to eslint-report.json
- Only 2 files currently in report (config files only)
- 304+ TypeScript files not being linted

**Result:** ESLint report is generated but:
- Linting errors don't fail the build
- Most files not covered
- No integration with Next.js build

### Issue 3: TypeScript Check Not in Build Pipeline

**Current Behavior:**
- `npm run build` = `next build` (ignores TypeScript)
- `npm run typecheck` = `tsc --noEmit` (SEPARATE command)
- TypeScript validation is OPTIONAL

**Risk:**
- Developers may skip `npm run typecheck`
- Build succeeds with type errors
- CI/CD must explicitly run typecheck

### Issue 4: Vitest and Playwright Not in Build

**Test Scripts Present:**
- npm test (vitest)
- npm run test:e2e (playwright)

**But:**
- Not run before production build
- Not required for deployment
- Easy to skip during development

## BACKEND BUILD ANALYSIS

### Backend Build Flow (Docker):

```dockerfile
FROM python:3.11-slim
  → Install system dependencies (tesseract, opencv, etc.)
  → pip install -r requirements.txt
    → Uses BuildKit cache mount (optimized)
    → NO validation step
    → NO syntax checking
    → NO import checking
  → COPY app code
  → CMD ["uvicorn", "app.main:app", ...]
```

### Missing Backend Validations:

```bash
# NOT in Dockerfile:
python -m py_compile app/**/*.py      # Syntax check
python -m pytest tests/                # Run tests
mypy app/                              # Type checking
pylint app/                            # Code quality
flake8 app/                            # Style guide
bandit app/                            # Security scan
pip check                              # Dependency conflicts
```

### Backend pytest Configuration

**File:** backend/pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts =
    -v                    # Verbose
    --strict-markers      # Enforce marker definition
    --tb=short           # Short traceback
    --disable-warnings   # Suppress warnings
    -p no:cacheprovider  # No cache

markers =
    slow: marks tests as slow
    integration: marks tests as integration
    unit: marks tests as unit
    api: marks tests as API
    service: marks tests as service
    db: marks tests that require database
    asyncio: marks tests as async
```

**Status:**
- ✓ Proper test structure
- ✓ Markers defined
- ✗ NO coverage thresholds
- ✗ NO fail-on-warning
- ✗ NOT run in Docker build

## TURBOPACK-SPECIFIC ISSUES

### Next.js 16 with Turbopack:

**Configuration:**
```typescript
turbopack: {}  // Uses Turbopack in dev mode
```

**Implications:**
- Development: Fast hot reload with Turbopack
- Production: Uses Turbopack for bundling
- Different from Webpack (used in Next.js 12-15)

**Potential Issues:**
- Some Webpack plugins don't work with Turbopack
- CSS-in-JS libraries may have different behavior
- critters (CSS inlining) may not work optimally

**No Testing:**
- No validation that Turbopack bundles correctly
- No check for bundle size
- No check for missing dependencies

## LEGACY PEER DEPS ISSUE

### Problem:

**Dockerfile.frontend:**
```dockerfile
RUN npm install --legacy-peer-deps  # Line 17, 43
```

**Reason:** Dependency conflicts exist

**Packages Involved:**
- critters (^0.0.25) - CSS inlining
- @radix-ui/* - UI primitives
- Other Radix UI packages

**Risk:**
- Older versions of peer dependencies accepted
- May cause runtime errors
- Security vulnerabilities possible
- Not discoverable until runtime

**Better Solution:**
- Update critters package
- Investigate and fix peer dependencies
- Use `npm audit` to find issues

## NODE MODULES STATUS

### Current State:

**Verification:**
```bash
npm ls @types/node
# Result: `-- (empty)`  # Not installed
```

**Issue:**
- node_modules directory is empty or not present
- @types/node is required by tsconfig.json
- npm install has not been run (or node_modules cleared)

**TypeScript Type Check Failure:**
```
error TS2688: Cannot find type definition file for '@types/node'.
```

**Resolution:**
```bash
npm install  # Must be run before typecheck
```

## MISSING CI/CD VALIDATION

### Recommended GitHub Actions / CI Pipeline:

```yaml
# Build Pipeline Stages (Currently Missing)

# Stage 1: Install & Validate
- npm ci                              # ← NOT in Docker
- npm run format:check                # ← NOT in Docker

# Stage 2: Type Safety
- npm run typecheck                   # ← NOT in Docker
- npm run lint                        # ← NOT in Docker (fails silently)

# Stage 3: Testing
- npm test                            # ← NOT in Docker
- npm run test:e2e                    # ← NOT in Docker (long running)

# Stage 4: Build
- npm run build                       # ← Done, but errors ignored

# Stage 5: Backend
- pip install -r requirements.txt     # ← No validation
- python -m pytest tests/             # ← NOT in Docker
- mypy app/                           # ← NOT configured
```

## SUMMARY TABLE

| Step | Frontend | Backend | Status |
|------|----------|---------|--------|
| Install | ✓ Works | ✓ Works | ✓ OK |
| Type Check | ⚠️ Errors ignored | ❌ Not configured | ❌ RISKY |
| Lint | ⚠️ Not required | ❌ Not configured | ❌ RISKY |
| Unit Tests | ⚠️ Not required | ⚠️ Not required | ⚠️ OPTIONAL |
| Build | ⚠️ Errors ignored | ✓ Compiles | ⚠️ RISKY |
| Validation | ✗ None | ✗ None | ❌ CRITICAL |

## ACTIONABLE RECOMMENDATIONS

### TIER 1: Critical (Do First)

1. **Enable TypeScript Validation in Docker**
   ```dockerfile
   RUN npm run typecheck || exit 1  # Fail if type errors
   RUN npm run build                 # Then build
   ```

2. **Fix ignoreBuildErrors**
   ```typescript
   // next.config.ts
   typescript: {
     ignoreBuildErrors: false,  // Change from true
   },
   ```

3. **Investigate framer-motion types**
   ```bash
   npm update framer-motion
   npm run typecheck  # Check if issue persists
   ```

### TIER 2: High Priority

4. **Add Linting to Build**
   ```dockerfile
   RUN npm run lint  # Before build
   ```

5. **Enable Stricter TypeScript**
   ```json
   // tsconfig.json
   "strict": true,
   "noImplicitAny": true,
   "skipLibCheck": false
   ```

6. **Add Backend Type Checking**
   - Install: `pip install mypy`
   - Configure: mypy.ini
   - Run: `mypy app/`

### TIER 3: Best Practices

7. **Add Required Tests Before Build**
   - Critical path E2E tests
   - Unit tests for core modules
   - Integration tests for APIs

8. **Remove Legacy Peer Deps**
   - Update critters
   - Fix Radix UI versions
   - Document why if needed

9. **Document Build Process**
   - Create BUILD.md
   - Document known issues
   - Add troubleshooting guide
