"""
Admin API - Panel de Control para gestionar módulos y configuraciones

CONSOLIDATED (2025-11-12):
- PageVisibility endpoints removed - use /api/pages/visibility instead
- SystemSettings endpoints kept for backward compatibility
- Maintenance mode, statistics, export/import endpoints kept (unique functionality)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import update, func
from typing import List, Optional
from datetime import datetime
import json

from app.core.database import get_db
from app.models.models import PageVisibility, SystemSettings, User
from app.api.deps import get_current_user, require_admin
from pydantic import BaseModel

router = APIRouter(prefix="/api/admin", tags=["admin"])

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
