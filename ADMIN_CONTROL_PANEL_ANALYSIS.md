# UNS-ClaudeJP 5.4 - Admin Control Panel Analysis

## Executive Summary

The admin control panel in UNS-ClaudeJP 5.4 consists of a comprehensive role-based access control (RBAC) system with two complementary approaches:

1. **Global Page Visibility** - Admin toggles to enable/disable entire pages for all users
2. **Role-Based Permissions** - Granular control over which pages each role can access
3. **Page Guards** - Frontend protection ensuring disabled pages redirect to construction page

---

## 1. FRONTEND STRUCTURE

### Admin Pages Location
```
frontend/app/(dashboard)/admin/
├── control-panel/
│   └── page.tsx              # Main admin control panel (30.5 KB)
└── yukyu-management/
    └── page.tsx              # Paid vacation management page (13.8 KB)
```

### Admin Page Components

#### 1.1 Control Panel Page (`control-panel/page.tsx`)
- **Purpose**: Master admin interface for managing all system-wide page visibility and role permissions
- **Route**: `/dashboard/admin/control-panel`
- **Status**: Fully dynamic (force-dynamic)
- **Features**:
  - Global statistics dashboard (total pages, enabled/disabled, recent changes)
  - Global page visibility controls (enable/disable all pages at once)
  - Per-role permission management with tabbed interface
  - Bulk operations (enable/disable multiple pages)
  - Permission search/filter
  - Export configuration to JSON
  - Initialize default permissions button
  - Role-specific statistics (total, enabled, disabled pages per role)

#### 1.2 Yukyu Management Page (`yukyu-management/page.tsx`)
- **Purpose**: Administrative management of paid vacation (有給休暇) records
- **Route**: `/dashboard/admin/yukyu-management`
- **Features**:
  - Manual yukyu calculation for specific employees
  - Force expiration of old yukyus (2+ years)
  - Scheduler status monitoring
  - Employee search and selection
  - Statistics dashboard

### Admin Support Components

#### Page Guard Component (`components/page-guard.tsx`)
```typescript
// Protects disabled pages by checking visibility
<PageGuard pageKey="timer-cards">
  <TimerCardsContent />
</PageGuard>
```
- **Type**: Client Component (`'use client'`)
- **Behavior**: 
  - Checks if page is enabled via `usePageVisibility()` hook
  - Redirects to `/dashboard/construction` if disabled
  - Shows loading spinner while checking
  - Transparent pass-through if enabled

#### Page Visibility Toggle Component (`components/page-visibility-toggle.tsx`)
```typescript
// Shows toggle for admin users only
<PageVisibilityToggle pageKey="candidates" pageName="Candidates" />
```
- **Purpose**: Individual page on/off toggle for admin users
- **Visibility**: Only shown to ADMIN/SUPER_ADMIN roles
- **Animations**: Framer motion for smooth state changes

#### Under Construction Page (`components/under-construction.tsx`)
- **Purpose**: Fallback UI for disabled pages
- **Features**:
  - Animated construction icons
  - Bilingual messaging (Spanish/Japanese)
  - Progress bar animation
  - Professional styling

#### Construction Route (`app/(dashboard)/construction/page.tsx`)
- **Purpose**: Main disabled page fallback
- **Route**: `/dashboard/construction`
- **Features**:
  - Animated background particles
  - Gradient orbs
  - Japanese "工事中" (Under Construction) messaging
  - Development progress indicator
  - Back to dashboard link

### Admin Hooks

#### `usePageVisibility()` Hook (`hooks/use-page-visibility.ts`)
```typescript
export function usePageVisibility(pageKey: string): UsePageVisibilityReturn {
  // Fetches single page visibility from API
  // Provides toggle functionality
}

export function useAllPagesVisibility() {
  // Fetches ALL page visibility settings
  // Used in control panel
}

export function useCurrentPageVisibility(): UsePageVisibilityReturn {
  // Auto-detects current page from URL
  // Maps URL segments to page keys
}
```

#### `usePagePermission()` Hook (`hooks/use-page-permission.ts`)
```typescript
export function usePagePermission(pageKey: string) {
  // Checks if current user's role has access to page
  // Calls: GET /role-permissions/check/{role}/{page_key}
  // Default: deny on error (safe fallback)
}
```

#### Alternative Hook (`lib/hooks/use-page-visibility.ts`)
```typescript
export function usePageVisibility() {
  // Fetches from: GET /pages/visibility
  // Returns list of all pages with visibility status
}
```

---

## 2. BACKEND API STRUCTURE

### Admin API Routes

#### Location: `backend/app/api/admin.py`
- **Router Prefix**: `/api/admin`
- **Tag**: `"admin"`
- **Access Control**: `require_admin` dependency (ADMIN/SUPER_ADMIN only)

**Endpoints**:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/admin/pages` | Get all page visibility settings |
| GET | `/admin/pages/{page_key}` | Get specific page visibility |
| PUT | `/admin/pages/{page_key}` | Update page visibility |
| POST | `/admin/pages/bulk-toggle` | Toggle multiple pages at once |
| POST | `/admin/pages/{page_key}/toggle` | Toggle single page (toggle state) |
| GET | `/admin/settings` | Get all system settings |
| GET | `/admin/settings/{setting_key}` | Get specific setting |
| PUT | `/admin/settings/{setting_key}` | Update system setting |
| POST | `/admin/maintenance-mode` | Toggle maintenance mode |
| GET | `/admin/statistics` | Get admin dashboard statistics |
| GET | `/admin/export-config` | Export all admin configuration as JSON |
| POST | `/admin/import-config` | Import admin configuration from JSON |

### Page Visibility API

#### Location: `backend/app/api/pages.py`
- **Router Prefix**: `/api/pages`
- **Tag**: `"pages"`
- **Access Control**: All authenticated users can GET, only ADMIN/SUPER_ADMIN can PUT

**Endpoints**:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/pages/visibility` | Get all page visibility |
| GET | `/pages/visibility/{page_key}` | Get single page visibility |
| PUT | `/pages/visibility/{page_key}` | Toggle page visibility |
| POST | `/pages/visibility/init` | Initialize default pages (SUPER_ADMIN only) |

### Role Permissions API

#### Location: `backend/app/api/role_permissions.py`
- **Router Prefix**: `/api/role-permissions`
- **Tag**: `"role-permissions"`

**Key Features**:
- 54 available pages (main modules + sub-features)
- 8 user roles (including legacy roles)
- Default permissions matrix per role
- Per-role bulk update functionality

**Available Roles** (from AVAILABLE_ROLES constant):
```python
{
  "SUPER_ADMIN": "Full system control",
  "ADMIN": "Administrative access",
  "COORDINATOR": "Coordination tasks",
  "KANRININSHA": "Manager role",
  "EMPLOYEE": "Employee access",
  "CONTRACT_WORKER": "Contract worker",
  "KEITOSAN": "Finance Manager (legacy)",
  "TANTOSHA": "Representative (legacy)"
}
```

**Available Pages** (54 total):
- **Main Modules** (15): dashboard, candidates, employees, factories, apartments, timer_cards, salary, requests, reports, design_system, forms, support, help, terms, privacy
- **Candidates** (3): create, edit, upload
- **Employees** (3): create, edit, bulk_operations
- **Factories** (2): create, edit
- **Apartments** (2): create, edit
- **Salary** (3): calculations, history, export
- **Requests** (2): create, approval
- **Reports** (3): attendance, payroll, export
- **Settings** (8): appearance, profile, language, notifications, security, integrations, backup
- **Admin** (5): users, roles, system, audit, database
- **Other** (8): notifications, import_export, themes, monitoring, health, performance, etc.

**Default Permissions Matrix**:
- **SUPER_ADMIN**: All 54 pages
- **ADMIN**: All except database management (53 pages)
- **COORDINATOR**: 30 pages (basic + HR + reporting)
- **KANRININSHA**: 35+ pages (basic + HR + finance)
- **EMPLOYEE**: 20+ pages (basic + self-service)
- **CONTRACT_WORKER**: 12 pages (minimal set)
- **KEITOSAN**: Finance + selected pages (legacy)
- **TANTOSHA**: HR + selected pages (legacy)

**Endpoints**:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/role-permissions/roles` | List all available roles |
| GET | `/role-permissions/pages` | List all available pages |
| GET | `/role-permissions/{role_key}` | Get permissions for role |
| PUT | `/role-permissions/{role_key}/{page_key}` | Update single permission |
| POST | `/role-permissions/bulk-update/{role_key}` | Bulk update permissions for role |
| GET | `/role-permissions/check/{role_key}/{page_key}` | Check if role has access |
| GET | `/role-permissions/user/{user_id}/permissions` | Get current user's permissions |
| POST | `/role-permissions/reset/{role_key}` | Reset role to defaults |
| POST | `/role-permissions/initialize-defaults` | Initialize all role defaults |

---

## 3. DATABASE MODELS

### Database Schema Location
`backend/app/models/models.py`

#### PageVisibility Model
```python
class PageVisibility(Base):
    __tablename__ = "page_visibility"
    
    id: Integer (PK)
    page_key: String(100) - Unique key (e.g., 'timer-cards')
    page_name: String(100) - Japanese display name
    page_name_en: String(100) - English display name
    is_enabled: Boolean - Default: True (visible)
    path: String(255) - Route path
    description: Text - Admin notes
    disabled_message: String(255) - Custom message when disabled
    last_toggled_by: Integer (FK to users.id)
    last_toggled_at: DateTime
    updated_at: DateTime - Last update timestamp
    created_at: DateTime - Creation timestamp
```

#### RolePagePermission Model
```python
class RolePagePermission(Base):
    __tablename__ = "role_page_permissions"
    
    id: Integer (PK)
    role_key: String(50) - Role identifier (ADMIN, EMPLOYEE, etc.)
    page_key: String(100) - Page identifier
    is_enabled: Boolean - Default: True (can access)
    created_at: DateTime
    updated_at: DateTime
```

#### SystemSettings Model
```python
class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    id: Integer (PK)
    key: String(100) - Unique setting key (e.g., 'maintenance_mode')
    value: String(255) - Setting value
    description: Text
    updated_at: DateTime
    created_at: DateTime
```

#### User Model (Excerpt)
```python
class User(Base):
    __tablename__ = "users"
    
    role: SQLEnum(UserRole)  # SUPER_ADMIN, ADMIN, COORDINATOR, etc.
    # ... other fields
```

#### UserRole Enum
```python
class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    KEITOSAN = "KEITOSAN"
    TANTOSHA = "TANTOSHA"
    COORDINATOR = "COORDINATOR"
    KANRININSHA = "KANRININSHA"
    EMPLOYEE = "EMPLOYEE"
    CONTRACT_WORKER = "CONTRACT_WORKER"
```

---

## 4. ROLE-BASED ACCESS CONTROL (RBAC) IMPLEMENTATION

### How RBAC Works

#### Step 1: User Authentication
- User logs in with username/password
- JWT token issued with user role embedded
- Role stored in `User.role` field

#### Step 2: Page Access Check (Backend)
```python
# In deps.py
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ["SUPER_ADMIN", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

#### Step 3: Page Access Check (Frontend)
```typescript
// Option 1: Page Guard (blocks unauthorized access)
<PageGuard pageKey="admin_roles">
  <AdminRolesContent />
</PageGuard>

// Option 2: Permission Hook (for conditional rendering)
const { hasPermission } = usePagePermission(pageKey)
if (!hasPermission) return <UnauthorizedPage />
```

#### Step 4: Role Permission Resolution
1. Frontend sends: `GET /role-permissions/check/{role}/{page_key}`
2. Backend queries `RolePagePermission` table
3. Returns `{ has_access: true/false }`
4. Frontend allows/blocks page access

### Two-Level Protection System

#### Level 1: Page Visibility (Global)
- **What it controls**: Is this page visible to ANY user?
- **Managed by**: ADMIN in control panel
- **Fallback**: If disabled, ALL users see "Under Construction"
- **Database**: `page_visibility` table

#### Level 2: Role Permissions (Per-Role)
- **What it controls**: Can THIS role access this page?
- **Managed by**: ADMIN via role tabs in control panel
- **Granularity**: Per role, per page
- **Database**: `role_page_permissions` table
- **Default Behavior**: Follows `get_default_permissions_matrix()`

### Authorization Flow

```
User Request
    ↓
JWT Token Validation (AuthService)
    ↓
User Role Extraction
    ↓
[Frontend: usePageGuard]
    ├─ Query PageVisibility
    └─ If disabled → Redirect to /construction
    ↓
[Backend: require_admin]
    ├─ Check User.role in ["SUPER_ADMIN", "ADMIN"]
    └─ If denied → 403 Forbidden
    ↓
[Optional: usePagePermission]
    ├─ Query RolePagePermission
    └─ If no access → Hide/Block element
    ↓
Allowed Access ✓
```

---

## 5. CURRENT ADMIN PAGES & FEATURES

### Admin Control Panel (`/dashboard/admin/control-panel`)

**Key Sections**:

1. **Statistics Dashboard**
   - Total pages: Shows all managed pages
   - Enabled pages: Count + percentage
   - Disabled pages: Count in red
   - Recent changes: Last 24 hours

2. **Global Page Controls Tab**
   - Bulk actions: Enable/Disable all pages
   - Individual page toggles with status badges
   - Each page shows: name (Japanese), English name, path, description

3. **Role-Based Permission Tabs** (8 tabs)
   - One tab per role (SUPER_ADMIN, ADMIN, COORDINATOR, etc.)
   - Per-role statistics (total, enabled, disabled)
   - Bulk actions: Enable/Disable all for role
   - Search/filter pages by name
   - Individual permission toggles with timestamps
   - Color-coded access status (green: can access, red: denied)

4. **Configuration Management**
   - Initialize Defaults button: Reset to default permissions matrix
   - Export Config: Download JSON with all settings
   - Settings export/import (planned)

5. **System Information**
   - Configured roles count
   - Available pages count
   - Maintenance mode status

### Admin Yukyu Management (`/dashboard/admin/yukyu-management`)

**Key Sections**:

1. **Statistics Dashboard**
   - Total employees
   - Days available
   - Days used
   - Days expired

2. **Manual Calculation**
   - Search employees by: Employee Number (社員№), ID, Name
   - Select employee dropdown
   - Calculate button: Triggers manual yukyu calculation

3. **Expiration Management**
   - Force expiration of 2+ year old yukyus
   - Confirmation dialog with warning
   - One-click expiration of expired yukyus

4. **Scheduler Monitoring**
   - Check if automatic scheduler is running
   - View scheduled jobs
   - Next execution times for each job
   - Refresh status button

---

## 6. API DEPENDENCY INJECTION

### Authorization Dependencies (`backend/app/api/deps.py`)

```python
def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get authenticated user from JWT token"""
    return auth_service.get_current_active_user(db, token)

def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require SUPER_ADMIN or ADMIN role"""
    if current_user.role not in ["SUPER_ADMIN", "ADMIN"]:
        raise HTTPException(403, "Admin access required")
    return current_user

def get_page_visibility(
    page_key: str,
    db: Session = Depends(get_db)
) -> Optional[PageVisibility]:
    """Get page visibility configuration"""
    return db.query(PageVisibility).filter(...).first()
```

### Usage in Admin Routes
```python
@router.get("/admin/pages")
async def get_page_visibility(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # ← Enforced here
):
    # Only admins can reach this code
    pages = db.query(PageVisibility).all()
    return pages
```

---

## 7. GAPS & MISSING FEATURES

### Current Gaps

1. **No User-Level Overrides**
   - Can't grant specific users extra pages beyond their role
   - Can only grant at role level

2. **No Page Dependencies**
   - Can't set "parent page must be enabled for child page"
   - E.g., can't force "salary" enabled if "salary_calculations" is disabled

3. **No Audit Trail Details**
   - `last_toggled_by` and `last_toggled_at` recorded, but no detailed audit log
   - No change history or rollback capability

4. **No Time-Based Scheduling**
   - Can't schedule page enabling/disabling for future times
   - No "maintenance window" scheduling

5. **No Conditional Visibility**
   - Can't show pages based on system state (e.g., during month-end)
   - Can't conditionally show based on department/location

6. **Limited Feedback on Permission Changes**
   - No email notifications to admins of permission changes
   - No approval workflow for permission requests

7. **No Permission Caching**
   - Frontend re-queries permissions on each page load
   - Could cache permissions in localStorage with TTL

8. **Missing Documentation Pages**
   - Some pages in API constants not created in frontend
   - E.g., `monitoring`, `monitoring_health`, `monitoring_performance`

### Potential Enhancements

1. **Permission Request Workflow**
   - Users request access to disabled pages
   - Admin reviews and approves/denies

2. **Role Hierarchy**
   - Parent role inherits from child role
   - E.g., ADMIN inherits all EMPLOYEE permissions

3. **Page Groups**
   - Group pages and toggle entire groups together
   - E.g., "Finance" group: salary, payroll reports, salary export

4. **A/B Testing Framework**
   - Show pages to percentage of users
   - Measure feature adoption

5. **Permission Analytics**
   - Which pages are most used by role
   - Which permissions are rarely used
   - Suggest cleanup

---

## 8. SECURITY CONSIDERATIONS

### Current Security Measures

1. **JWT Token Validation**
   - All endpoints require valid Bearer token
   - Token contains user role

2. **Admin-Only Routes**
   - Control panel requires ADMIN/SUPER_ADMIN role
   - Enforced at dependency level

3. **Role Validation**
   - Roles validated against enum
   - Invalid roles rejected

4. **Page Key Validation**
   - All page_keys validated against AVAILABLE_PAGES
   - Invalid keys return 404

### Potential Security Issues

1. **Frontend Bypass Risk**
   - PageGuard can be bypassed if user manipulates URL directly
   - Backend should also check role permissions on sensitive operations

2. **No Rate Limiting on Admin Changes**
   - No limit on bulk toggle operations
   - Could cause performance issues

3. **No Audit Trail Retention**
   - Audit fields exist but no archival/retention policy
   - Could grow indefinitely

4. **Default Permissions Hardcoded**
   - Default matrix in Python code, not database
   - Requires code change to modify defaults

---

## 9. CONFIGURATION & SETTINGS

### Default Settings Key (System Settings)
- `maintenance_mode`: Boolean (true/false) - Disables all pages when enabled

### Environment Variables
- None specific to admin panel (inherits from FastAPI config)

### Frontend Configuration
- Page keys must match between frontend and backend
- Default fallback path: `/dashboard/construction`

---

## 10. TESTING REFERENCES

### E2E Tests
- `e2e/06-admin-yukyu.spec.ts` - Tests for admin yukyu management page

### Manual Test Scenarios
1. Disable all pages, verify all redirect to construction
2. Grant EMPLOYEE role access to admin_users page, verify they can't access
3. Export config, modify JSON, import back
4. Initialize defaults, verify all roles get permissions
5. Test bulk operations on 50+ pages

---

## SUMMARY TABLE

| Aspect | Status | Implementation |
|--------|--------|-----------------|
| **Global Page Visibility** | ✓ Complete | `PageVisibility` model + admin.py API + control panel |
| **Role-Based Permissions** | ✓ Complete | `RolePagePermission` model + role_permissions.py API + tabs |
| **Frontend Page Guards** | ✓ Complete | PageGuard component + usePageVisibility hook |
| **Admin Control Panel** | ✓ Complete | `/admin/control-panel` page with full functionality |
| **Audit Trail** | ✓ Basic | Fields exist, no detailed tracking |
| **Permission Caching** | ✗ Missing | Re-queries on each load |
| **Time-Based Scheduling** | ✗ Missing | Not implemented |
| **User-Level Overrides** | ✗ Missing | Only role-level |
| **Page Dependencies** | ✗ Missing | No validation |
| **Permission Approval Workflow** | ✗ Missing | Not implemented |

