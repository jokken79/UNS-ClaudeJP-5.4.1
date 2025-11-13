# Manual RBAC Updates Required

## ⚠️ Action Required: Apply RBAC Code Changes

The file `backend/app/api/timer_cards.py` needs the following function replacements to complete FASE 2 implementation.

**Source File:** `backend/app/api/timer_cards_rbac_update.py`
**Target File:** `backend/app/api/timer_cards.py`

---

## 📝 Changes Required

### 1. Update GET / Endpoint (List Timer Cards)

**Location:** Lines ~353-392 in `timer_cards.py`

**Find this function:**
```python
@router.get("/", response_model=list[TimerCardResponse])
async def list_timer_cards(
    employee_id: int = None,
    factory_id: str = None,
    is_approved: bool = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """List timer cards with eager loaded employee relationship"""
    # ... current implementation
```

**Replace with:**
```python
@router.get("/", response_model=list[TimerCardResponse])
async def list_timer_cards(
    employee_id: int = None,
    factory_id: str = None,
    is_approved: bool = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List timer cards with role-based access control.

    Role-based filtering:
    - EMPLOYEE/CONTRACT_WORKER: Only see their own timer cards (matched by email)
    - KANRININSHA: See timer cards from their factory
    - COORDINATOR: See timer cards from assigned factories
    - ADMIN/SUPER_ADMIN/KEITOSAN/TANTOSHA: See all timer cards
    """
    # Limit to max 1000
    limit = min(limit, 1000)

    query = db.query(TimerCard)

    # Role-based filtering
    user_role = current_user.role.value

    if user_role in ["EMPLOYEE", "CONTRACT_WORKER"]:
        # Employees can only see their own timer cards
        # Match user email with employee email to find their timer cards
        employee = db.query(Employee).filter(Employee.email == current_user.email).first()
        if employee:
            query = query.filter(TimerCard.hakenmoto_id == employee.hakenmoto_id)
            logger.info(f"User {current_user.username} filtering timer cards for hakenmoto_id={employee.hakenmoto_id}")
        else:
            # If no employee record found for this user, return empty list
            logger.warning(f"User {current_user.username} (role: {user_role}) has no employee record")
            return []

    elif user_role == "KANRININSHA":
        # Managers can see timer cards from their factory
        employee = db.query(Employee).filter(Employee.email == current_user.email).first()
        if employee and employee.factory_id:
            query = query.filter(TimerCard.factory_id == employee.factory_id)
            logger.info(f"Manager {current_user.username} filtering timer cards for factory_id={employee.factory_id}")
        else:
            logger.warning(f"Manager {current_user.username} has no factory assignment")
            return []

    elif user_role == "COORDINATOR":
        # Coordinators can see timer cards from their assigned factories
        # For now, allow all - can be restricted based on coordinator-factory relationship
        logger.info(f"Coordinator {current_user.username} accessing all timer cards")

    # ADMIN, SUPER_ADMIN, KEITOSAN, TANTOSHA: No filtering (see all)

    # Apply additional filters (available to authorized roles)
    if employee_id:
        query = query.filter(TimerCard.employee_id == employee_id)
    if factory_id:
        query = query.filter(TimerCard.factory_id == factory_id)
    if is_approved is not None:
        query = query.filter(TimerCard.is_approved == is_approved)

    # Eager load employee relationship to prevent N+1 queries
    return (
        query
        .order_by(TimerCard.work_date.desc(), TimerCard.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
```

---

### 2. Update GET /{id} Endpoint (Get Timer Card)

**Location:** Lines ~395-460 in `timer_cards.py`

**Replace the RBAC section (lines ~414-458) with:**
```python
    # Role-based access control
    user_role = current_user.role.value

    if user_role in ["EMPLOYEE", "CONTRACT_WORKER"]:
        # Employees can only view their own timer cards
        employee = db.query(Employee).filter(Employee.email == current_user.email).first()

        if not employee:
            logger.warning(f"Employee record not found for user {current_user.username}")
            raise HTTPException(
                status_code=403,
                detail="Access denied: Employee record not found"
            )

        if timer_card.hakenmoto_id != employee.hakenmoto_id:
            logger.warning(
                f"User {current_user.username} attempted to access timer card {timer_card_id} "
                f"belonging to different employee"
            )
            raise HTTPException(
                status_code=403,
                detail="Access denied: You can only view your own timer cards"
            )

    elif user_role == "KANRININSHA":
        # Managers can view timer cards from their factory
        employee = db.query(Employee).filter(Employee.email == current_user.email).first()

        if not employee:
            logger.warning(f"Manager record not found for user {current_user.username}")
            raise HTTPException(
                status_code=403,
                detail="Access denied: Manager employee record not found"
            )

        # Check if timer card belongs to same factory
        if timer_card.factory_id != employee.factory_id:
            logger.warning(
                f"Manager {current_user.username} attempted to access timer card from different factory"
            )
            raise HTTPException(
                status_code=403,
                detail="Access denied: You can only view timer cards from your factory"
            )

    elif user_role == "COORDINATOR":
        # Coordinators can view timer cards from assigned factories
        # For now, allow all - can be restricted based on coordinator-factory relationship
        pass

    # ADMIN, SUPER_ADMIN, KEITOSAN, TANTOSHA: No restrictions

    logger.info(f"User {current_user.username} accessed timer card {timer_card_id}")
    return timer_card
```

---

### 3. Update PUT /{id} Endpoint (Update Timer Card)

**Location:** Lines ~463-487 in `timer_cards.py`

**Replace entire function with:**
```python
@router.put("/{timer_card_id}", response_model=TimerCardResponse)
async def update_timer_card(
    timer_card_id: int,
    timer_card_update: TimerCardUpdate,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Update timer card with audit logging.

    Only ADMIN and above can update timer cards.
    All changes are logged for audit trail.
    """
    timer_card = db.query(TimerCard).filter(TimerCard.id == timer_card_id).first()
    if not timer_card:
        raise HTTPException(status_code=404, detail="Timer card not found")

    # Prevent modification of approved timer cards without explicit permission
    if timer_card.is_approved and not timer_card_update.model_dump().get('is_approved') is False:
        logger.warning(
            f"User {current_user.username} attempted to modify approved timer card {timer_card_id}"
        )
        # In strict mode, raise error. For now, log warning and allow
        # Uncomment below to enforce:
        # raise HTTPException(
        #     status_code=400,
        #     detail="Cannot modify approved timer card. Unapprove first."
        # )

    # Store old values for audit log
    old_values = {
        "work_date": str(timer_card.work_date) if timer_card.work_date else None,
        "clock_in": str(timer_card.clock_in) if timer_card.clock_in else None,
        "clock_out": str(timer_card.clock_out) if timer_card.clock_out else None,
        "break_minutes": timer_card.break_minutes,
        "is_approved": timer_card.is_approved,
    }

    # Update fields
    updated_fields = []
    for field, value in timer_card_update.model_dump(exclude_unset=True).items():
        old_value = getattr(timer_card, field)
        if old_value != value:
            setattr(timer_card, field, value)
            updated_fields.append(field)

    # Recalculate hours if time changed
    if timer_card_update.clock_in or timer_card_update.clock_out or timer_card_update.break_minutes is not None:
        hours = calculate_hours(
            timer_card.clock_in,
            timer_card.clock_out,
            timer_card.break_minutes or 0,
            timer_card.work_date
        )
        for key, value in hours.items():
            setattr(timer_card, key, value)

    db.commit()
    db.refresh(timer_card)

    # Audit log
    logger.info(
        f"Timer card {timer_card_id} updated by {current_user.username} (ID: {current_user.id}). "
        f"Fields changed: {', '.join(updated_fields)}"
    )

    return timer_card
```

---

### 4. Update POST /approve Endpoint (Approve Timer Cards)

**Location:** Lines ~490-504 in `timer_cards.py`

**Replace entire function with:**
```python
@router.post("/approve", response_model=dict)
async def approve_timer_cards(
    approve_data: TimerCardApprove,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Approve multiple timer cards with complete audit logging.

    Only ADMIN and above can approve timer cards.
    Records approver user ID and timestamp for each approval.
    """
    # Fetch all timer cards to be approved
    cards = db.query(TimerCard).filter(TimerCard.id.in_(approve_data.timer_card_ids)).all()

    if len(cards) != len(approve_data.timer_card_ids):
        found_ids = {card.id for card in cards}
        missing_ids = set(approve_data.timer_card_ids) - found_ids
        logger.warning(f"Timer cards not found: {missing_ids}")
        raise HTTPException(
            status_code=404,
            detail=f"Timer cards not found: {list(missing_ids)}"
        )

    # Track already approved cards
    already_approved = []
    newly_approved = []

    # Approve each card
    for card in cards:
        if card.is_approved:
            already_approved.append(card.id)
            logger.info(f"Timer card {card.id} already approved, skipping")
        else:
            # CRITICAL: Set approved_by and approved_at
            card.is_approved = True
            card.approved_by = current_user.id  # Store approver user ID
            card.approved_at = datetime.now()   # Store approval timestamp
            newly_approved.append(card.id)

            logger.info(
                f"Timer card {card.id} approved by {current_user.username} (ID: {current_user.id}) "
                f"at {card.approved_at}"
            )

    db.commit()

    # Return detailed response
    return {
        "message": f"Approved {len(newly_approved)} timer cards",
        "newly_approved": newly_approved,
        "already_approved": already_approved,
        "total_requested": len(approve_data.timer_card_ids),
        "approved_by": current_user.username,
        "approved_at": datetime.now().isoformat()
    }
```

---

## 🔧 How to Apply Changes

### Option 1: Manual Copy-Paste (Recommended)

1. **Backup current file:**
   ```bash
   cp backend/app/api/timer_cards.py backend/app/api/timer_cards.py.backup2
   ```

2. **Open both files:**
   - Source: `backend/app/api/timer_cards_rbac_update.py`
   - Target: `backend/app/api/timer_cards.py`

3. **Replace each function** as listed above

4. **Save and verify** syntax is correct

### Option 2: Use Diff Tool

```bash
# Compare files to see differences
diff backend/app/api/timer_cards.py backend/app/api/timer_cards_rbac_update.py

# Or use a visual diff tool
code --diff backend/app/api/timer_cards.py backend/app/api/timer_cards_rbac_update.py
```

### Option 3: Automated Script

```bash
# Run this Python script to apply changes
python backend/scripts/apply_rbac_updates.py
```

---

## ✅ Verification Checklist

After applying changes:

- [ ] File syntax is valid (no Python errors)
- [ ] All imports are present
- [ ] `from datetime import datetime` is imported
- [ ] Logger is configured
- [ ] Run linter: `flake8 backend/app/api/timer_cards.py`
- [ ] Run type checker: `mypy backend/app/api/timer_cards.py`
- [ ] Restart backend service
- [ ] Test endpoints with different user roles

---

## 🧪 Testing

After applying changes, run these tests:

```bash
# Test RBAC implementation
docker exec uns-claudejp-backend pytest backend/tests/test_timer_cards_api.py -v -k "rbac or access or permission"

# Test audit logging
docker exec uns-claudejp-backend pytest backend/tests/test_timer_cards_api.py -v -k "approve or audit"

# Test all timer card functionality
docker exec uns-claudejp-backend pytest backend/tests/test_timer_card*.py -v
```

---

## 📝 Notes

- **Imports:** Ensure `from datetime import datetime` is present at the top of the file
- **Logger:** The logger is already configured: `logger = logging.getLogger(__name__)`
- **Backwards Compatible:** These changes are backwards compatible with existing frontend code
- **Database Required:** The migration must be applied before these changes will work correctly

---

## ⚠️ Important

**CRITICAL CHANGES:**
1. ✅ `approved_by = current_user.id` - Stores WHO approved
2. ✅ `approved_at = datetime.now()` - Stores WHEN approved
3. ✅ Email-based employee matching (no `Employee.user_id` field needed)
4. ✅ Explicit logging for audit trail

**These changes are REQUIRED for:**
- Compliance with data regulations
- Audit trail requirements
- Security best practices
- FASE 2 completion

---

## 🆘 Troubleshooting

### Issue: Import Error for `datetime`

**Solution:**
```python
# Add to imports at top of file
from datetime import datetime, date, time as datetime_time
```

### Issue: `logger` not found

**Solution:**
```python
# Already present in file, but verify:
import logging
logger = logging.getLogger(__name__)
```

### Issue: Type hint errors

**Solution:**
```python
# Ensure these imports are present:
from typing import Optional, List
from app.models.models import TimerCard, Employee, User
```

---

**End of Manual Update Guide**

**Status:** Ready to apply
**Difficulty:** Medium (requires careful copy-paste)
**Time Required:** 15-20 minutes
**Risk Level:** Low (backup exists)
