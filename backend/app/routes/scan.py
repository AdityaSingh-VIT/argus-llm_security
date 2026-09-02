"""
routes/scan.py — Scan endpoints.

POST /scan          → trigger a scan (returns immediately; runs in background)
GET  /scan/{id}     → poll scan status
"""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from database.connection import get_db
from database import crud
from models.schemas import ScanRequest, ScanJobOut, UserOut
from services import attack_engine, graph_engine

logger = logging.getLogger("argus.scan")
router = APIRouter()


async def _run_scan(scan_id: str, target_url: str, num_attacks: int) -> None:
    """
    Background coroutine:
      1. Update digital-twin graph with target info
      2. Generate attack prompts via LLM
      3. Execute each prompt against the target chatbot
      4. Store results in the database
    """
    from database.connection import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            await crud.update_scan_status(db, scan_id, "running")

            # 1. Push target into the digital twin graph
            logger.info("[scan:%s] Updating digital twin for %s", scan_id, target_url)
            await graph_engine.build_graph({
                "chatbot": target_url,
                "attacker": "External Attacker",
                "prompt_injection": "Automated red-team injection",
                "tool": "Argus Attack Engine",
            })

            # 2. Generate attack prompts
            logger.info("[scan:%s] Generating %d attack prompts", scan_id, num_attacks)
            prompts = await attack_engine.generate_attacks(
                context=f"LLM-based chatbot at {target_url}",
                n=num_attacks,
            )

            # 3. Execute and log each attack
            for prompt in prompts:
                logger.info("[scan:%s] Executing: %.80s...", scan_id, prompt)
                result = await attack_engine.execute_attack(target_url, prompt)
                await crud.log_attack(
                    db,
                    scan_id=scan_id,
                    prompt=result.prompt,
                    response=result.response,
                    score=result.score,
                    category=result.category,
                )

            await crud.update_scan_status(db, scan_id, "completed")
            logger.info("[scan:%s] Completed successfully", scan_id)

        except Exception as exc:
            logger.exception("[scan:%s] Failed: %s", scan_id, exc)
            await crud.update_scan_status(db, scan_id, "failed")


@router.post(
    "",
    response_model=ScanJobOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger a new LLM security scan",
)
async def trigger_scan(
    body: ScanRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    """
    Starts a scan in the background. Returns scan details immediately.
    Poll GET /scan/{id} to check status.
    """
    scan = await crud.create_scan(
        db,
        target_url=body.target_url,
        project_name=body.project_name,
        user_id=current_user.id,
    )
    background_tasks.add_task(
        _run_scan,
        scan_id=scan.id,
        target_url=body.target_url,
        num_attacks=body.num_attacks,
    )
    return scan


@router.get(
    "/{scan_id}",
    response_model=ScanJobOut,
    summary="Get scan status",
)
async def get_scan_status(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    """Poll this endpoint after triggering a scan to check its status."""
    scan = await crud.get_scan_by_id(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return scan
