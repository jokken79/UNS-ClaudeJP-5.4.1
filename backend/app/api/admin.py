"""
Admin API - Panel de Control para gestionar módulos y configuraciones

CONSOLIDATED (2025-11-12):
- PageVisibility endpoints removed - use /api/pages/visibility instead
- SystemSettings endpoints kept for backward compatibility
- Maintenance mode, statistics, export/import endpoints kept (unique functionality)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import update, func
from typing import List, Optional
from datetime import datetime
import json

from app.core.database import get_db
from app.models.models import PageVisibility, SystemSettings, User
from app.api.deps import get_current_user, require_admin
from app.services.audit_service import AuditService
from pydantic import BaseModel

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP address from request"""
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0].strip()
    elif "x-real-ip" in request.headers:
        return request.headers["x-real-ip"]
    else:
        return request.client.host if request.client else None


def get_user_agent(request: Request) -> Optional[str]:
    """Extract user agent from request"""
    return request.headers.get("user-agent")


# ============================================
# SCHEMAS
# ============================================

class SystemSettingResponse(BaseModel):
    id: int
    key: str
    value: Optional[str]
    description: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True

class MaintenanceModeRequest(BaseModel):
    enabled: bool

# ============================================
# ENDPOINTS - PAGE VISIBILITY
# ============================================

@router.get("/pages", response_model=List[PageVisibilityResponse])
async def get_page_visibility(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Obtener configuración de visibilidad de todas las páginas
    """
    pages = db.query(PageVisibility).order_by(PageVisibility.page_key).all()
    return pages

@router.get("/pages/{page_key}", response_model=PageVisibilityResponse)
async def get_page_visibility_by_key(
    page_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Obtener configuración de visibilidad de una página específica
    """
    page = db.query(PageVisibility).filter(PageVisibility.page_key == page_key).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página no encontrada")

    return page

@router.put("/pages/{page_key}", response_model=PageVisibilityResponse)
async def update_page_visibility(
    page_key: str,
    page_data: PageVisibilityUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Actualizar configuración de visibilidad de una página
    """
    page = db.query(PageVisibility).filter(PageVisibility.page_key == page_key).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página no encontrada")

    # Store old value for audit log
    old_value = page.is_enabled

    # Update page
    page.is_enabled = page_data.is_enabled
    if page_data.disabled_message is not None:
        page.disabled_message = page_data.disabled_message
    page.last_toggled_by = current_user.id
    page.last_toggled_at = datetime.utcnow()
    page.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(page)

    # Log the change in audit log
    AuditService.log_page_visibility_change(
        db=db,
        admin_id=current_user.id,
        page_key=page_key,
        old_value=old_value,
        new_value=page_data.is_enabled,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return page

@router.post("/pages/bulk-toggle")
async def bulk_toggle_pages(
    bulk_data: BulkPageToggle,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Habilitar/deshabilitar múltiples páginas simultáneamente
    """
    # Count successful updates
    pages_count = len(bulk_data.page_keys)

    # Update all pages in bulk
    stmt = (
        update(PageVisibility)
        .where(PageVisibility.page_key.in_(bulk_data.page_keys))
        .values(
            is_enabled=bulk_data.is_enabled,
            last_toggled_by=current_user.id,
            last_toggled_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    )
    result = db.execute(stmt)
    db.commit()

    # Log the bulk operation in audit log
    operation_type = "bulk_enable" if bulk_data.is_enabled else "bulk_disable"
    AuditService.log_bulk_operation(
        db=db,
        admin_id=current_user.id,
        operation_type=operation_type,
        pages_affected=bulk_data.page_keys,
        total_count=pages_count,
        success_count=result.rowcount,
        failed_count=pages_count - result.rowcount,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return {
        "message": f"{len(bulk_data.page_keys)} páginas actualizadas",
        "updated_count": len(bulk_data.page_keys)
    }

@router.post("/pages/{page_key}/toggle")
async def toggle_page_visibility(
    page_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Alternar visibilidad de una página (enable <-> disable)
    """
    page = db.query(PageVisibility).filter(PageVisibility.page_key == page_key).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página no encontrada")

    page.is_enabled = not page.is_enabled
    page.last_toggled_by = current_user.id
    page.last_toggled_at = datetime.utcnow()
    page.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(page)

    return {
        "page_key": page_key,
        "is_enabled": page.is_enabled,
        "message": f"Página {'habilitada' if page.is_enabled else 'deshabilitada'}"
    }

# ============================================
# ENDPOINTS - SYSTEM SETTINGS
# ============================================

@router.get("/settings", response_model=List[SystemSettingResponse])
async def get_system_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Obtener todas las configuraciones del sistema
    """
    settings = db.query(SystemSettings).order_by(SystemSettings.key).all()
    return settings

@router.get("/settings/{setting_key}", response_model=SystemSettingResponse)
async def get_system_setting(
    setting_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Obtener una configuración específica del sistema
    """
    setting = db.query(SystemSettings).filter(SystemSettings.key == setting_key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")

    return setting

@router.put("/settings/{setting_key}", response_model=SystemSettingResponse)
async def update_system_setting(
    setting_key: str,
    value: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Actualizar una configuración del sistema
    """
    setting = db.query(SystemSettings).filter(SystemSettings.key == setting_key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")

    setting.value = value
    setting.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(setting)

    return setting

@router.post("/maintenance-mode")
async def toggle_maintenance_mode(
    maintenance_data: MaintenanceModeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Activar/desactivar modo mantenimiento

    When enabling maintenance mode, all pages are disabled.
    """
    # Update maintenance mode setting
    setting = db.query(SystemSettings).filter(SystemSettings.key == "maintenance_mode").first()
    if not setting:
        # Create if doesn't exist
        setting = SystemSettings(
            key="maintenance_mode",
            value="false" if not maintenance_data.enabled else "true",
            description="Global maintenance mode toggle"
        )
        db.add(setting)
    else:
        setting.value = "true" if maintenance_data.enabled else "false"
        setting.updated_at = datetime.utcnow()

    # If enabling maintenance mode, disable all pages
    if maintenance_data.enabled:
        stmt = (
            update(PageVisibility)
            .values(
                is_enabled=False,
                last_toggled_by=current_user.id,
                last_toggled_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        db.execute(stmt)

    db.commit()

    action = "activado" if maintenance_data.enabled else "desactivado"
    return {
        "message": f"Modo mantenimiento {action}",
        "maintenance_mode": maintenance_data.enabled
    }

# ============================================
# ENDPOINTS - STATISTICS
# ============================================

@router.get("/statistics")
async def get_admin_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Obtener estadísticas del panel de administración
    """
    # Count pages
    total_pages = db.query(func.count(PageVisibility.id)).scalar()
    enabled_pages = db.query(func.count(PageVisibility.id)).filter(PageVisibility.is_enabled == True).scalar()
    disabled_pages = total_pages - enabled_pages

    # Get settings
    maintenance_mode = db.query(SystemSettings).filter(SystemSettings.key == "maintenance_mode").first()
    maintenance_enabled = maintenance_mode.value == "true" if maintenance_mode else False

    # Recent changes (last 24 hours)
    from datetime import timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_changes = (
        db.query(PageVisibility)
        .filter(PageVisibility.last_toggled_at >= yesterday)
        .count()
    ) if db.query(PageVisibility).first() else 0

    return {
        "pages": {
            "total": total_pages,
            "enabled": enabled_pages,
            "disabled": disabled_pages,
            "percentage_enabled": round((enabled_pages / total_pages * 100), 2) if total_pages > 0 else 0
        },
        "system": {
            "maintenance_mode": maintenance_enabled,
            "recent_changes_24h": recent_changes
        }
    }

# ============================================
# ENDPOINTS - EXPORT/IMPORT
# ============================================

@router.get("/export-config")
async def export_configuration(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Exportar toda la configuración del panel

    Includes both PageVisibility and SystemSettings configurations.
    """
    pages = db.query(PageVisibility).order_by(PageVisibility.page_key).all()
    settings = db.query(SystemSettings).order_by(SystemSettings.key).all()

    export_data = {
        "exported_at": datetime.utcnow().isoformat(),
        "exported_by": current_user.username,
        "pages": [
            {
                "page_key": p.page_key,
                "page_name": p.page_name,
                "is_enabled": p.is_enabled,
                "disabled_message": p.disabled_message
            }
            for p in pages
        ],
        "settings": [
            {
                "key": s.key,
                "value": s.value
            }
            for s in settings
        ]
    }

    return export_data

@router.post("/import-config")
async def import_configuration(
    config_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Importar configuración del panel

    Imports both PageVisibility and SystemSettings configurations.
    """
    imported_pages = 0
    imported_settings = 0

    # Import pages
    if "pages" in config_data:
        for page_data in config_data["pages"]:
            page = db.query(PageVisibility).filter(PageVisibility.page_key == page_data["page_key"]).first()
            if page:
                page.is_enabled = page_data["is_enabled"]
                page.disabled_message = page_data.get("disabled_message")
                page.last_toggled_by = current_user.id
                page.last_toggled_at = datetime.utcnow()
                page.updated_at = datetime.utcnow()
                imported_pages += 1

    # Import settings
    if "settings" in config_data:
        for setting_data in config_data["settings"]:
            setting = db.query(SystemSettings).filter(SystemSettings.key == setting_data["key"]).first()
            if setting:
                setting.value = setting_data["value"]
                setting.updated_at = datetime.utcnow()
                imported_settings += 1

    db.commit()

    return {
        "message": "Configuración importada exitosamente",
        "imported_at": datetime.utcnow().isoformat(),
        "imported_pages": imported_pages,
        "imported_settings": imported_settings
    }

# ============================================
# NOTE: PageVisibility CRUD endpoints removed
# Use /api/pages/visibility/* endpoints instead
# See app/api/pages.py for PageVisibility management
# ============================================
