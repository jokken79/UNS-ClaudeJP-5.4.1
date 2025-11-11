#!/usr/bin/env python3
"""
Script to synchronize candidate approval status based on employee assignments.

Rules:
- If a candidate has a corresponding employee (rirekisho_id match), status = "approved" (合格)
- If a candidate has no employee assignment, status = "pending" (審査中)
- This script runs AFTER import_data.py to ensure employee data is present
"""
import sys
from pathlib import Path

sys.path.insert(0, '/app')

from app.core.database import SessionLocal
from app.models.models import Candidate, Employee, ContractWorker, Staff
from sqlalchemy import func

def sync_candidate_employee_status():
    """Synchronize candidate status based on employee existence"""

    db = SessionLocal()
    try:
        # Get all candidates
        candidates = db.query(Candidate).all()

        updated = 0
        unchanged = 0

        print(f"""
╔════════════════════════════════════════════════════════════╗
║          SINCRONIZANDO ESTADOS CANDIDATO-EMPLEADO          ║
╚════════════════════════════════════════════════════════════╝
Total de candidatos a procesar: {len(candidates)}
        """)

        for candidate in candidates:
            # Check if this candidate has a corresponding employee in ANY of the 3 tables
            # 1. Try Employee table
            employee = db.query(Employee).filter(
                Employee.rirekisho_id == candidate.rirekisho_id
            ).first()

            # 2. Try ContractWorker table if not found
            if not employee:
                employee = db.query(ContractWorker).filter(
                    ContractWorker.rirekisho_id == candidate.rirekisho_id
                ).first()

            # 3. Try Staff table if still not found
            if not employee:
                employee = db.query(Staff).filter(
                    Staff.rirekisho_id == candidate.rirekisho_id
                ).first()

            if employee:
                # Candidate has an employee assignment → status should be "hired" (採用)
                if candidate.status != "hired":
                    candidate.status = "hired"
                    db.commit()
                    updated += 1
                else:
                    unchanged += 1
            else:
                # No employee assignment → keep "pending" (審査中)
                if candidate.status != "pending":
                    candidate.status = "pending"
                    db.commit()
                    updated += 1
                else:
                    unchanged += 1

        print(f"""
╔════════════════════════════════════════════════════════════╗
║          SINCRONIZACIÓN COMPLETADA                         ║
╚════════════════════════════════════════════════════════════╝
✓ Actualizados: {updated}
━ Sin cambios:  {unchanged}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)

        # Show summary of status distribution
        status_counts = db.query(
            Candidate.status,
            func.count(Candidate.id).label('count')
        ).group_by(Candidate.status).all()

        print("\n📊 Distribución de estados:")
        for status, count in status_counts:
            status_label = {
                "pending": "审查中 (Pendientes)",
                "approved": "合格 (Aprobados)",
                "rejected": "不合格 (Rechazados)",
                "hired": "採用 (Contratados)"
            }.get(status, status)
            print(f"   {status_label}: {count}")

        return True

    except Exception as e:
        print(f"❌ Error al sincronizar: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == '__main__':
    success = sync_candidate_employee_status()
    sys.exit(0 if success else 1)
