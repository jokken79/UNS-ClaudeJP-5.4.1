"""
Service for managing admin audit logs
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import json
import csv
import io

from app.models.models import AdminAuditLog, User, AdminActionType, ResourceType
from app.schemas.audit import (
    AdminAuditLogCreate,
    AdminAuditLogResponse,
    AdminAuditLogFilters,
    AdminAuditLogStats,
    ExportFormat
)


class AuditService:
    """Service for admin audit log operations"""

    @staticmethod
    def _create_audit_log(
        db: Session,
        admin_id: int,
        action_type: AdminActionType,
        resource_type: ResourceType,
        resource_key: Optional[str],
        previous_value: Optional[str],
        new_value: Optional[str],
        description: str,
        ip_address: Optional[str],
        user_agent: Optional[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> AdminAuditLog:
        """Internal method to create an audit log entry"""
        audit_log = AdminAuditLog(
            admin_user_id=admin_id,
            action_type=action_type,
            resource_type=resource_type,
            resource_key=resource_key,
            previous_value=previous_value,
            new_value=new_value,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log

    @staticmethod
    def log_page_visibility_change(
        db: Session,
        admin_id: int,
        page_key: str,
        old_value: bool,
        new_value: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AdminAuditLog:
        """Log a page visibility change"""
        action = "enabled" if new_value else "disabled"
        description = f"Page '{page_key}' {action}"

        return AuditService._create_audit_log(
            db=db,
            admin_id=admin_id,
            action_type=AdminActionType.PAGE_VISIBILITY_CHANGE,
            resource_type=ResourceType.PAGE,
            resource_key=page_key,
            previous_value=str(old_value),
            new_value=str(new_value),
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def log_role_permission_change(
        db: Session,
        admin_id: int,
        role_key: str,
        page_key: str,
        old_value: bool,
        new_value: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AdminAuditLog:
        """Log a role permission change"""
        action = "granted" if new_value else "revoked"
        description = f"Role '{role_key}' permission {action} for page '{page_key}'"

        metadata = {
            "role": role_key,
            "page": page_key
        }

        return AuditService._create_audit_log(
            db=db,
            admin_id=admin_id,
            action_type=AdminActionType.ROLE_PERMISSION_CHANGE,
            resource_type=ResourceType.PERMISSION,
            resource_key=f"{role_key}:{page_key}",
            previous_value=str(old_value),
            new_value=str(new_value),
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata
        )

    @staticmethod
    def log_bulk_operation(
        db: Session,
        admin_id: int,
        operation_type: str,
        pages_affected: Optional[List[str]] = None,
        roles_affected: Optional[List[str]] = None,
        total_count: int = 0,
        success_count: int = 0,
        failed_count: int = 0,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AdminAuditLog:
        """Log a bulk operation"""
        description = f"Bulk operation: {operation_type} - {success_count}/{total_count} succeeded"

        metadata = {
            "operation_type": operation_type,
            "pages_affected": pages_affected or [],
            "roles_affected": roles_affected or [],
            "total_count": total_count,
            "success_count": success_count,
            "failed_count": failed_count
        }

        return AuditService._create_audit_log(
            db=db,
            admin_id=admin_id,
            action_type=AdminActionType.BULK_OPERATION,
            resource_type=ResourceType.SYSTEM,
            resource_key="bulk_operation",
            previous_value=None,
            new_value=json.dumps(metadata),
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata
        )

    @staticmethod
    def log_config_change(
        db: Session,
        admin_id: int,
        config_key: str,
        old_value: Any,
        new_value: Any,
        config_section: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AdminAuditLog:
        """Log a system configuration change"""
        description = f"System config '{config_key}' changed from '{old_value}' to '{new_value}'"

        metadata = {
            "config_key": config_key,
            "config_section": config_section
        }

        return AuditService._create_audit_log(
            db=db,
            admin_id=admin_id,
            action_type=AdminActionType.CONFIG_CHANGE,
            resource_type=ResourceType.SYSTEM,
            resource_key=config_key,
            previous_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata
        )

    @staticmethod
    def log_cache_clear(
        db: Session,
        admin_id: int,
        items_cleared: int = 0,
        cache_type: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AdminAuditLog:
        """Log a cache clear operation"""
        description = f"Cache cleared: {items_cleared} items"
        if cache_type:
            description += f" ({cache_type})"

        metadata = {
            "items_cleared": items_cleared,
            "cache_type": cache_type
        }

        return AuditService._create_audit_log(
            db=db,
            admin_id=admin_id,
            action_type=AdminActionType.CACHE_CLEAR,
            resource_type=ResourceType.SYSTEM,
            resource_key="cache",
            previous_value=None,
            new_value=str(items_cleared),
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata
        )

    @staticmethod
    def get_audit_logs(
        db: Session,
        filters: AdminAuditLogFilters
    ) -> Tuple[List[AdminAuditLog], int]:
        """Get audit logs with filters and pagination"""
        query = db.query(AdminAuditLog)

        # Apply filters
        if filters.action_type:
            query = query.filter(AdminAuditLog.action_type == filters.action_type)

        if filters.resource_type:
            query = query.filter(AdminAuditLog.resource_type == filters.resource_type)

        if filters.resource_key:
            query = query.filter(AdminAuditLog.resource_key == filters.resource_key)

        if filters.admin_id:
            query = query.filter(AdminAuditLog.admin_user_id == filters.admin_id)

        if filters.start_date:
            query = query.filter(AdminAuditLog.created_at >= filters.start_date)

        if filters.end_date:
            query = query.filter(AdminAuditLog.created_at <= filters.end_date)

        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    AdminAuditLog.description.ilike(search_term),
                    AdminAuditLog.resource_key.ilike(search_term)
                )
            )

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        sort_column = getattr(AdminAuditLog, filters.sort_by, AdminAuditLog.created_at)
        if filters.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Apply pagination
        logs = query.offset(filters.skip).limit(filters.limit).all()

        return logs, total

    @staticmethod
    def get_audit_log_by_id(db: Session, log_id: int) -> Optional[AdminAuditLog]:
        """Get a single audit log entry by ID"""
        return db.query(AdminAuditLog).filter(AdminAuditLog.id == log_id).first()

    @staticmethod
    def get_recent_logs(db: Session, limit: int = 10) -> List[AdminAuditLog]:
        """Get the most recent audit log entries"""
        return (
            db.query(AdminAuditLog)
            .order_by(desc(AdminAuditLog.created_at))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_audit_stats(db: Session) -> AdminAuditLogStats:
        """Get statistics about audit logs"""
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Count changes by time period
        total_24h = db.query(AdminAuditLog).filter(AdminAuditLog.created_at >= day_ago).count()
        total_7d = db.query(AdminAuditLog).filter(AdminAuditLog.created_at >= week_ago).count()
        total_30d = db.query(AdminAuditLog).filter(AdminAuditLog.created_at >= month_ago).count()
        total_all = db.query(AdminAuditLog).count()

        # Top admins
        top_admins_query = (
            db.query(
                User.id,
                User.username,
                User.full_name,
                func.count(AdminAuditLog.id).label('change_count')
            )
            .join(AdminAuditLog, User.id == AdminAuditLog.admin_user_id)
            .group_by(User.id, User.username, User.full_name)
            .order_by(desc('change_count'))
            .limit(10)
            .all()
        )
        top_admins = [
            {
                "user_id": row.id,
                "username": row.username,
                "full_name": row.full_name,
                "change_count": row.change_count
            }
            for row in top_admins_query
        ]

        # Most modified pages
        pages_query = (
            db.query(
                AdminAuditLog.resource_key,
                func.count(AdminAuditLog.id).label('change_count')
            )
            .filter(AdminAuditLog.resource_type == ResourceType.PAGE)
            .group_by(AdminAuditLog.resource_key)
            .order_by(desc('change_count'))
            .limit(10)
            .all()
        )
        most_modified_pages = [
            {"page_key": row.resource_key, "change_count": row.change_count}
            for row in pages_query
        ]

        # Most modified roles
        roles_query = (
            db.query(
                AdminAuditLog.resource_key,
                func.count(AdminAuditLog.id).label('change_count')
            )
            .filter(AdminAuditLog.resource_type == ResourceType.ROLE)
            .group_by(AdminAuditLog.resource_key)
            .order_by(desc('change_count'))
            .limit(10)
            .all()
        )
        most_modified_roles = [
            {"role_key": row.resource_key, "change_count": row.change_count}
            for row in roles_query
        ]

        # Changes by action type
        action_types_query = (
            db.query(
                AdminAuditLog.action_type,
                func.count(AdminAuditLog.id).label('count')
            )
            .group_by(AdminAuditLog.action_type)
            .all()
        )
        changes_by_action_type = {
            str(row.action_type.value): row.count
            for row in action_types_query
        }

        # Changes by resource type
        resource_types_query = (
            db.query(
                AdminAuditLog.resource_type,
                func.count(AdminAuditLog.id).label('count')
            )
            .group_by(AdminAuditLog.resource_type)
            .all()
        )
        changes_by_resource_type = {
            str(row.resource_type.value): row.count
            for row in resource_types_query
        }

        return AdminAuditLogStats(
            total_changes_24h=total_24h,
            total_changes_7d=total_7d,
            total_changes_30d=total_30d,
            total_changes_all=total_all,
            top_admins=top_admins,
            most_modified_pages=most_modified_pages,
            most_modified_roles=most_modified_roles,
            changes_by_action_type=changes_by_action_type,
            changes_by_resource_type=changes_by_resource_type
        )

    @staticmethod
    def export_audit_logs(
        db: Session,
        format: ExportFormat,
        filters: Optional[AdminAuditLogFilters] = None
    ) -> str:
        """Export audit logs to JSON or CSV format"""
        if filters is None:
            filters = AdminAuditLogFilters(skip=0, limit=10000)  # Default to large limit for export

        logs, _ = AuditService.get_audit_logs(db, filters)

        if format == ExportFormat.JSON:
            return AuditService._export_to_json(logs)
        elif format == ExportFormat.CSV:
            return AuditService._export_to_csv(logs)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    @staticmethod
    def _export_to_json(logs: List[AdminAuditLog]) -> str:
        """Export logs to JSON format"""
        data = []
        for log in logs:
            data.append({
                "id": log.id,
                "admin_user_id": log.admin_user_id,
                "admin_username": log.admin_user.username if log.admin_user else None,
                "action_type": log.action_type.value,
                "resource_type": log.resource_type.value,
                "resource_key": log.resource_key,
                "previous_value": log.previous_value,
                "new_value": log.new_value,
                "description": log.description,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "metadata": log.metadata,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
        return json.dumps(data, indent=2)

    @staticmethod
    def _export_to_csv(logs: List[AdminAuditLog]) -> str:
        """Export logs to CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "ID", "Admin User ID", "Admin Username", "Action Type", "Resource Type",
            "Resource Key", "Previous Value", "New Value", "Description",
            "IP Address", "Created At"
        ])

        # Write data
        for log in logs:
            writer.writerow([
                log.id,
                log.admin_user_id,
                log.admin_user.username if log.admin_user else "",
                log.action_type.value,
                log.resource_type.value,
                log.resource_key or "",
                log.previous_value or "",
                log.new_value or "",
                log.description or "",
                log.ip_address or "",
                log.created_at.isoformat() if log.created_at else ""
            ])

        return output.getvalue()

    @staticmethod
    def delete_audit_log(db: Session, log_id: int) -> bool:
        """Delete an audit log entry (SUPER_ADMIN only)"""
        log = AuditService.get_audit_log_by_id(db, log_id)
        if log:
            db.delete(log)
            db.commit()
            return True
        return False
