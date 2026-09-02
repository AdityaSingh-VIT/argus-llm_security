"""
routes/report.py — PDF report endpoints.

POST /report             → generate a PDF report for a scan
GET  /report/{scan_id}   → download the generated PDF
"""

import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from database.connection import get_db
from database import crud
from models.schemas import ReportRequest, ReportOut, UserOut
from services import report_generator

router = APIRouter()


@router.post(
    "",
    response_model=ReportOut,
    summary="Generate a PDF security report for a scan",
)
async def generate_report(
    body: ReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    scan = await crud.get_scan_by_id(db, body.scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    attacks = await crud.get_attacks_by_scan(db, body.scan_id)
    file_path = await report_generator.generate_pdf(scan=scan, attacks=attacks)

    rpt = await crud.save_report(db, scan_id=body.scan_id, file_path=file_path)
    return ReportOut(
        scan_id=rpt.scan_id,
        file_path=rpt.file_path,
        created_at=rpt.created_at,
    )


@router.get(
    "/{scan_id}",
    summary="Download the PDF report for a scan",
)
async def download_report(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    rpt = await crud.get_report_by_scan(db, scan_id)
    if not rpt:
        raise HTTPException(
            status_code=404, detail="Report not generated yet. POST /report first."
        )
    if not os.path.exists(rpt.file_path):
        raise HTTPException(status_code=404, detail="Report file missing on disk")
    return FileResponse(
        path=rpt.file_path,
        media_type="application/pdf",
        filename=f"argus_report_{scan_id[:8]}.pdf",
    )
