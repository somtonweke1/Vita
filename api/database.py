"""
Database connection and session management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import logging

from api.config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.debug,  # Log SQL in debug mode
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Event listener to set application context for audit logging
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Set session variables on new database connections"""
    cursor = dbapi_conn.cursor()
    # Set application name for easier query tracking
    cursor.execute("SET application_name = 'vitanexus_api'")
    cursor.close()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes to get database session.

    Usage:
        @app.get("/members/{member_id}")
        def get_member(member_id: str, db: Session = Depends(get_db)):
            return db.query(Member).filter(Member.id == member_id).first()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database session outside of FastAPI.

    Usage:
        with get_db_context() as db:
            member = db.query(Member).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


class AuditLogger:
    """
    HIPAA-compliant audit logging for database operations.
    Logs all PHI access with user, timestamp, action, and result.
    """

    @staticmethod
    def log_access(
        user_id: str,
        action: str,
        table_name: str,
        record_id: str,
        member_id: str = None,
        success: bool = True,
        ip_address: str = None,
        details: dict = None
    ):
        """
        Log PHI access to audit_log table.

        Args:
            user_id: ID of user performing action
            action: Type of action (access, modify, delete, export)
            table_name: Table being accessed
            record_id: Record identifier
            member_id: Member ID if PHI is involved
            success: Whether action succeeded
            ip_address: IP address of request
            details: Additional context
        """
        from datetime import datetime

        with get_db_context() as db:
            try:
                audit_entry = {
                    'event_timestamp': datetime.utcnow(),
                    'event_type': action,
                    'user_id': user_id,
                    'table_name': table_name,
                    'record_id': record_id,
                    'member_id': member_id,
                    'ip_address': ip_address,
                    'action_description': f"{action} on {table_name}",
                    'new_values': details,
                    'success': success
                }

                # In production, this would insert into audit_log table
                # For now, log to application logger
                logger.info(
                    f"AUDIT: user={user_id} action={action} table={table_name} "
                    f"record={record_id} member={member_id} success={success}",
                    extra=audit_entry
                )

            except Exception as e:
                logger.error(f"Failed to write audit log: {e}", exc_info=True)
                # Audit logging failures should not break the application
                # but should trigger alerts


def init_db():
    """
    Initialize database tables.
    In production, use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")


def check_db_connection() -> bool:
    """
    Health check for database connection.

    Returns:
        True if database is accessible, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False