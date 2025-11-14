# REMOVED FROM: backend/app/api/admin.py (Lines 90-233)
# These endpoints were duplicated - consolidated in backend/app/api/pages.py
# Kept here for reference. Use /api/pages/ endpoints instead.

# ============================================
# ENDPOINTS - PAGE VISIBILITY [REMOVED - DUPLICATED IN pages.py]
# ============================================

@router.get("/pages", response_model=List[PageVisibilityResponse])
async def get_page_visibility(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Obtener configuración de visibilidad de todas las páginas
    REMOVED: Use GET /api/pages/visibility instead
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
    REMOVED: Use GET /api/pages/visibility/{page_key} instead
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
    REMOVED: Use PUT /api/pages/visibility/{page_key} instead
    """
    page = db.query(PageVisibility).filter(PageVisibility.page_key == page_key).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página no encontrada")
    # ... implementation ...

@router.post("/pages/bulk-toggle")
async def bulk_toggle_pages(
    bulk_data: BulkPageToggle,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Habilitar/deshabilitar múltiples páginas simultáneamente
    REMOVED: Use POST /api/pages/bulk-toggle instead
    """
    # ... implementation ...

@router.post("/pages/{page_key}/toggle")
async def toggle_page_visibility(
    page_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Alternar visibilidad de una página (enable <-> disable)
    REMOVED: Use POST /api/pages/{page_key}/toggle instead
    """
    # ... implementation ...


# ============================================
# SCHEMAS - REMOVED (No longer needed)
# ============================================

class PageVisibilityResponse(BaseModel):
    page_key: str
    is_enabled: bool
    disabled_message: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class PageVisibilityUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    disabled_message: Optional[str] = None

class BulkPageToggle(BaseModel):
    page_keys: List[str]
    is_enabled: bool
    disabled_message: Optional[str] = None
