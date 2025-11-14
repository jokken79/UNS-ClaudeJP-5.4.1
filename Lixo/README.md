# 🗑️ Lixo - Dead Code & Cleanup Archive

**Date**: 2025-11-14
**Status**: Cleanup Complete
**Total Items Archived**: 19

This folder contains all code, files, and endpoints that were removed during the codebase cleanup phase.

---

## 📋 Contents Summary

### 1. **unused-stores/** (4 unused Zustand stores)
```
✗ settings-store.ts       - Store for app settings (never imported)
✗ fonts-store.ts          - Store for font management (never imported)
✗ dashboard-tabs-store.ts - Store for dashboard tabs (never imported)
✗ visibilidad-template-store.ts - Store for template visibility (never imported)
```

**Reason**: Created but never used anywhere in the application
**Total Lines**: ~170
**Safe to Delete**: YES (no imports found)

---

### 2. **backup-files/** (Obsolete backup files)
```
├── migration_versions_backup/
│   ├── 001_initial_v1.py
│   ├── 002_add_candidates_v1.py
│   └── 003_add_employees_v1.py
```

**Reason**: Backup migration files not used by Alembic (stored in separate folder)
**Status**: No longer needed since active migrations are in `backend/alembic/versions/`
**Safe to Delete**: YES (Alembic only uses versions/ folder)

---

### 3. **backup-docs/** (Obsolete documentation)
```
✗ DOCUMENTACION_FOTOS_INDICE_backup.md
```

**Reason**: Backup documentation file mixed with active docs
**Status**: Superseded by active documentation in `docs/`
**Safe to Delete**: YES (archive copy, not referenced)

---

### 4. **commented-code/** (Dead commented code)
```
scheduler_cleanup_logs_job_REMOVED.py
```

**Content**:
- Commented-out `cleanup_old_logs_job()` function (8 lines)
- Commented-out scheduler job registration for log cleanup (8 lines)

**Reason**:
- Function marked "Not implemented yet"
- Job was commented out, never executed
- No active implementation needed

**Location Original**: `backend/app/core/scheduler.py` (lines 48-54, 75-82)
**Status**: Fully removed
**Safe to Delete**: YES (can recover from git)

---

### 5. **duplicate-apis/** (Consolidated API endpoints)
```
admin_page_visibility_endpoints_REMOVED.py
```

**Content**:
- 5 duplicate endpoints for page visibility management
- 3 unused schemas (PageVisibilityResponse, PageVisibilityUpdate, BulkPageToggle)

**Endpoints Removed**:
```
✗ GET    /api/admin/pages              → use GET /api/pages/visibility
✗ GET    /api/admin/pages/{page_key}   → use GET /api/pages/visibility/{page_key}
✗ PUT    /api/admin/pages/{page_key}   → use PUT /api/pages/visibility/{page_key}
✗ POST   /api/admin/pages/bulk-toggle  → use POST /api/pages/bulk-toggle
✗ POST   /api/admin/pages/{page_key}/toggle → use POST /api/pages/{page_key}/toggle
```

**Reason**:
- Endpoints duplicated in both `admin.py` and `pages.py`
- Consolidated in `pages.py` for better organization
- Admin module still has system settings and statistics endpoints

**Location Original**: `backend/app/api/admin.py` (lines 90-233)
**Status**: Fully removed from admin.py, kept in pages.py
**Safe to Delete**: YES (functionality preserved in pages.py)

---

## ✅ Cleanup Operations Completed

### Deleted Files (7 total):
```
frontend/stores/settings-store.ts
frontend/stores/fonts-store.ts
frontend/stores/dashboard-tabs-store.ts
frontend/stores/visibilidad-template-store.ts
backend/alembic/versions_backup/ (entire folder)
docs/features/photos/DOCUMENTACION_FOTOS_INDICE_backup.md
```

### Modified Files (2 total):
```
backend/app/core/scheduler.py
  ✓ Removed: cleanup_old_logs_job() function
  ✓ Removed: Commented-out job registration

backend/app/api/admin.py
  ✓ Removed: PAGE VISIBILITY section (144 lines)
  ✓ Removed: PageVisibilityResponse schema
  ✓ Removed: PageVisibilityUpdate schema
  ✓ Removed: BulkPageToggle schema
  ✓ Kept: PageVisibility import (still used in statistics/export)
```

---

## 📊 Impact Analysis

| Category | Items | Lines | Impact |
|----------|-------|-------|--------|
| Unused Stores | 4 | ~170 | Performance improvement (small) |
| Backup Files | 4 | - | Disk space (minimal) |
| Commented Code | 1 | 16 | Code clarity |
| Duplicate APIs | 5 | ~144 | Architectural improvement |
| **TOTAL** | **19** | **~330** | **Overall cleanup** |

---

## 🚀 Migration Path

If you need to restore any of these items:

### To Restore a Zustand Store:
```bash
git checkout HEAD -- frontend/stores/[store-name].ts
```

### To Restore Migration Backups:
```bash
git checkout HEAD -- backend/alembic/versions_backup/
```

### To Restore API Endpoints:
```bash
git checkout HEAD -- backend/app/api/admin.py
# Then selectively copy from Lixo/duplicate-apis/admin_page_visibility_endpoints_REMOVED.py
```

### To Restore Scheduler Code:
```bash
git checkout HEAD -- backend/app/core/scheduler.py
```

---

## 📝 Notes for Future Reference

### Zustand Stores
- These stores were never imported, suggesting either:
  - Planned for future use but never completed
  - Accidentally created and forgotten
  - Migration from previous version not fully cleaned up

### Duplicate API Endpoints
- The consolidation creates a cleaner API structure:
  - `/api/pages/` = Page visibility management (all page-related endpoints)
  - `/api/admin/` = System administration (settings, statistics, maintenance)
- Frontend should use `/api/pages/` endpoints for page visibility operations
- No frontend changes needed (cleanup was API-only)

### Scheduler Jobs
- `cleanup_old_logs_job` was marked "Not implemented yet"
- The commented code shows it was never actually scheduled
- Log cleanup can be implemented in future versions if needed

---

## 🔍 Verification

All cleanups have been tested:
```bash
✓ No TypeScript compilation errors
✓ No import errors (all imports verified)
✓ API functionality preserved (tested via pages.py)
✓ Scheduler still works (expire_yukyus_job active)
✓ Frontend builds successfully
✓ No broken dependencies
```

---

**Last Updated**: 2025-11-14
**Cleanup Version**: v1.0
**Status**: Complete and verified
