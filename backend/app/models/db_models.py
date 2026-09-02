"""
models/db_models.py — SQLAlchemy ORM table definitions.

Tables:
  users          — registered Argus users
  scan_jobs      — each security scan run
  attack_results — individual attack prompt/response pairs per scan
  reports        — generated PDF report metadata
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(256), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    scans: Mapped[list["ScanJob"]] = relationship("ScanJob", back_populates="user")


class ScanJob(Base):
    __tablename__ = "scan_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    project_name: Mapped[str] = mapped_column(String(256))
    target_url: Mapped[str] = mapped_column(String(2048))
    # Status values: pending | running | completed | failed
    status: Mapped[str] = mapped_column(String(32))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship("User", back_populates="scans")
    attacks: Mapped[list["AttackResult"]] = relationship(
        "AttackResult", back_populates="scan"
    )
    report: Mapped[Optional["Report"]] = relationship(
        "Report", back_populates="scan", uselist=False
    )


class AttackResult(Base):
    __tablename__ = "attack_results"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    scan_id: Mapped[str] = mapped_column(
        String, ForeignKey("scan_jobs.id"), index=True
    )
    prompt: Mapped[str] = mapped_column(Text)
    response: Mapped[str] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Float)           # 0–100
    category: Mapped[str] = mapped_column(String(128))   # e.g. "Prompt Injection"
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    scan: Mapped["ScanJob"] = relationship("ScanJob", back_populates="attacks")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    scan_id: Mapped[str] = mapped_column(
        String, ForeignKey("scan_jobs.id"), unique=True
    )
    file_path: Mapped[str] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    scan: Mapped["ScanJob"] = relationship("ScanJob", back_populates="report")
