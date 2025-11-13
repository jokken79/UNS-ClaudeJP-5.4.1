# Admin Panel: Side-by-Side Code Comparison

## Issue #1: Field Name Mismatch

### WRONG - What's Currently in admin.py (Lines 58-71)

```python
class PageVisibilityResponse(BaseModel):
    page_key: str
    is_visible: bool              # ❌ WRONG
    updated_at: datetime

    class Config:
        from_attributes = True


class PageVisibilityUpdate(BaseModel):
    is_visible: bool              # ❌ WRONG


class BulkPageToggle(BaseModel):
    page_keys: List[str]
    is_visible: bool              # ❌ WRONG
```

### CORRECT - What's in page_visibility.py (Lines 6-42)

```python
class PageVisibilityBase(BaseModel):
    """Base schema for PageVisibility (ページ表示設定)"""
    page_key: str = Field(..., min_length=1, max_length=100)
    page_name: str = Field(..., min_length=1, max_length=100)
    page_name_en: Optional[str] = Field(None, max_length=100)
    is_enabled: bool = Field(default=True)  # ✅ CORRECT
    path: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    disabled_message: Optional[str] = Field(None, max_length=255)


class PageVisibilityUpdate(BaseModel):
    """Schema for updating page visibility (all fields optional)"""
    page_name: Optional[str] = Field(None, max_length=100)
    page_name_en: Optional[str] = Field(None, max_length=100)
    is_enabled: Optional[bool] = None  # ✅ CORRECT
    path: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    disabled_message: Optional[str] = Field(None, max_length=255)  # ✅ HAS FIELD


class PageVisibilityResponse(PageVisibilityBase):
    """Schema for page visibility response"""
    id: int
    last_toggled_by: Optional[int] = None
    last_toggled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

## Issue #2: AttributeError in Endpoints

### WRONG - Current Code (Line 136)

```python
@router.put("/pages/{page_key}", response_model=PageVisibilityResponse)
async def update_page_visibility(
    page_key: str,
    page_data: PageVisibilityUpdate,  # This schema only has 'is_visible'
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    page = db.query(PageVisibility).filter(PageVisibility.page_key == page_key).first()
    
    old_value = page.is_enabled
    
    # ❌ ERROR HERE - page_data doesn't have is_enabled attribute
    page.is_enabled = page_data.is_enabled  # AttributeError!
    
    if page_data.disabled_message is not None:  # ✅ This one exists
        page.disabled_message = page_data.disabled_message
```

### CORRECT - Should Be

```python
# 1. Import the correct schema
from app.schemas.page_visibility import PageVisibilityUpdate, PageVisibilityResponse

# 2. Use imported schema in endpoint
@router.put("/pages/{page_key}", response_model=PageVisibilityResponse)
async def update_page_visibility(
    page_key: str,
    page_data: PageVisibilityUpdate,  # Now has is_enabled ✅
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    page = db.query(PageVisibility).filter(PageVisibility.page_key == page_key).first()
    
    old_value = page.is_enabled
    
    # ✅ NOW THIS WORKS - page_data has is_enabled
    page.is_enabled = page_data.is_enabled
    
    if page_data.disabled_message is not None:
        page.disabled_message = page_data.disabled_message
```

---

## Issue #3: Bulk Toggle AttributeError (Line 177)

### WRONG - Current Code

```python
class BulkPageToggle(BaseModel):
    page_keys: List[str]
    is_visible: bool  # ❌ WRONG FIELD NAME

@router.post("/pages/bulk-toggle")
async def bulk_toggle_pages(
    bulk_data: BulkPageToggle,  # Has 'is_visible', not 'is_enabled'
    ...
):
    stmt = (
        update(PageVisibility)
        .where(PageVisibility.page_key.in_(bulk_data.page_keys))
        .values(
            is_enabled=bulk_data.is_enabled,  # ❌ AttributeError - no such attribute
            disabled_message=bulk_data.disabled_message,  # ❌ Field missing
            ...
        )
    )
```

### CORRECT - Should Be

```python
# Option 1: Use same schema as PageVisibilityUpdate
from app.schemas.page_visibility import PageVisibilityUpdate

# Update to:
@router.post("/pages/bulk-toggle")
async def bulk_toggle_pages(
    bulk_data: PageVisibilityUpdate,  # ✅ Has is_enabled and disabled_message
    ...
):
    stmt = (
        update(PageVisibility)
        .where(PageVisibility.page_key.in_(bulk_data.page_keys))
        .values(
            is_enabled=bulk_data.is_enabled,  # ✅ Now exists
            disabled_message=bulk_data.disabled_message,  # ✅ Now exists
            ...
        )
    )

# Option 2: Or define BulkPageToggle properly
class BulkPageToggle(BaseModel):
    page_keys: List[str]
    is_enabled: bool  # ✅ CORRECT
    disabled_message: Optional[str] = None  # ✅ Include if needed
```

---

## Issue #4: Frontend Duplicate Interfaces

### WRONG - Current Code (Lines 737-781)

```typescript
// FIRST DEFINITION (lines 737-747)
export interface AuditLogEntry {
  id: number;
  admin_username: string;
  action_type: 'enable' | 'disable' | 'bulk_enable' | 'bulk_disable' | 'update';
  target_type: 'page' | 'role_permission' | 'global';
  target_name: string;
  role_key?: string;
  details?: string;
  timestamp: string;
  created_at: string;
}

export interface RoleStatsResponse {
  role_key: string;
  role_name: string;
  total_pages: number;
  enabled_pages: number;
  disabled_pages: number;
  percentage: number;
}

// ... 14 lines of other code ...

// SECOND DEFINITION - EXACT DUPLICATE (lines 762-772) ❌
export interface AuditLogEntry {
  id: number;
  admin_username: string;
  action_type: 'enable' | 'disable' | 'bulk_enable' | 'bulk_disable' | 'update';
  target_type: 'page' | 'role_permission' | 'global';
  target_name: string;
  role_key?: string;
  details?: string;
  timestamp: string;
  created_at: string;
}

export interface RoleStatsResponse {
  role_key: string;
  role_name: string;
  total_pages: number;
  enabled_pages: number;
  disabled_pages: number;
  percentage: number;
}
```

### CORRECT - Should Be

Keep the first definitions (lines 737-756) and DELETE lines 762-781 completely.

---

## Issue #5: AdminStatistics Interface

### WRONG - Current Frontend Interface (Lines 949-958)

```typescript
export interface AdminStatistics {
  total_users: number;
  active_users: number;
  total_candidates: number;
  total_employees: number;
  total_factories: number;
  maintenance_mode: boolean;
  database_size?: string;
  uptime?: string;
  // ❌ Missing: pages, system, recent_changes_24h
}
```

### CORRECT - Backend Actually Returns (Lines 385-405)

```python
return {
    "pages": {  # ❌ MISSING FROM FRONTEND INTERFACE
        "total": total_pages,
        "enabled": enabled_pages,
        "disabled": disabled_pages,
        "percentage_enabled": round((enabled_pages / total_pages * 100), 2)
    },
    "system": {  # ❌ MISSING FROM FRONTEND INTERFACE
        "maintenance_mode": maintenance_enabled,
        "recent_changes_24h": recent_changes
    },
    # These match the interface ✅
    "total_users": total_users,
    "active_users": active_users,
    "total_candidates": total_candidates,
    "total_employees": total_employees,
    "total_factories": total_factories,
    "maintenance_mode": maintenance_enabled,
    "database_size": None,
    "uptime": None
}
```

### CORRECTED - Frontend Interface Should Be

```typescript
export interface AdminStatistics {
  // Flat fields (as before)
  total_users: number;
  active_users: number;
  total_candidates: number;
  total_employees: number;
  total_factories: number;
  maintenance_mode: boolean;
  database_size?: string;
  uptime?: string;
  
  // ✅ ADD THESE NESTED OBJECTS
  pages?: {
    total: number;
    enabled: number;
    disabled: number;
    percentage_enabled: number;
  };
  
  system?: {
    maintenance_mode: boolean;
    recent_changes_24h: number;
  };
}
```

---

## Side-by-Side: Database vs Pydantic vs Frontend

### Field: `is_visible` vs `is_enabled`

| Component | Field Name | Status |
|-----------|-----------|--------|
| Database Model (`PageVisibility`) | `is_enabled` | ✅ Correct |
| Correct Schema (`page_visibility.py`) | `is_enabled` | ✅ Correct |
| Admin API Schema (current) | `is_visible` | ❌ Wrong |
| Frontend Type (needs update) | — | ❌ Missing |

---

## Complete Fix Locations

### Backend (admin.py)

```diff
- class PageVisibilityResponse(BaseModel):
-     page_key: str
-     is_visible: bool
-     updated_at: datetime
- 
- class PageVisibilityUpdate(BaseModel):
-     is_visible: bool
- 
- class BulkPageToggle(BaseModel):
-     page_keys: List[str]
-     is_visible: bool

+ from app.schemas.page_visibility import (
+     PageVisibilityUpdate,
+     PageVisibilityResponse,
+     PageVisibilityBase
+ )

  # Lines 136, 152, 177, 187 now work correctly
  page.is_enabled = page_data.is_enabled  # ✅ Works now
```

### Frontend (lib/api.ts)

```diff
  // Lines 737-756: Keep these ✅
  export interface AuditLogEntry { ... }
  export interface RoleStatsResponse { ... }
  
- // Lines 762-781: DELETE THESE DUPLICATES ❌
- export interface AuditLogEntry { ... }
- export interface RoleStatsResponse { ... }

  // Update AdminStatistics interface
  export interface AdminStatistics {
    total_users: number;
    active_users: number;
    total_candidates: number;
    total_employees: number;
    total_factories: number;
    maintenance_mode: boolean;
    database_size?: string;
    uptime?: string;
+   pages?: {
+     total: number;
+     enabled: number;
+     disabled: number;
+     percentage_enabled: number;
+   };
+   system?: {
+     maintenance_mode: boolean;
+     recent_changes_24h: number;
+   };
  }
```

