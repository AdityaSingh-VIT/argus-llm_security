"""
routes/history.py — History endpoints.

GET /history                         → all scans for current user
GET /history/{scan_id}/attacks       → attack results for a scan
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from database.connection import get_db
from database import crud
from models.schemas import ScanJobOut, AttackResultOut, UserOut

router = APIRouter()


@router.get(
    "",
    response_model=List[ScanJobOut],
    summary="List all past scans",
)
async def list_scans(
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    """Returns all scans run by the current user, newest first."""
    return await crud.get_scans(db, current_user.id)


@router.get(
    "/{scan_id}/attacks",
    response_model=List[AttackResultOut],
    summary="Get attack results for a scan",
)
async def get_attack_history(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    """Returns all attack prompt/response pairs logged for a specific scan."""
    return await crud.get_attacks_by_scan(db, scan_id)
