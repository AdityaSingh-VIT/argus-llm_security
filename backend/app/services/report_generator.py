"""
services/report_generator.py — PDF report generation using ReportLab.

Generates a professional security report with:
  - Scan summary table
  - Risk score overview
  - Per-attack prompt/response detail
"""

import logging
import os
from datetime import datetime, timezone
from typing import List

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    colors = None

from models.db_models import AttackResult, ScanJob

logger = logging.getLogger("argus.services.report")
REPORTS_DIR: str = os.getenv("REPORTS_DIR", "./reports")


def _score_color(score: float):
    if not REPORTLAB_AVAILABLE:
        return None
    if score >= 80:
        return colors.HexColor("#ef4444")
    if score >= 50:
        return colors.HexColor("#f97316")
    if score >= 25:
        return colors.HexColor("#eab308")
    return colors.HexColor("#22c55e")


def _score_label(score: float) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "MEDIUM"
    return "LOW"


async def generate_pdf(scan: ScanJob, attacks: List[AttackResult]) -> str:
    """Build the PDF and return its absolute file path."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"argus_report_{scan.id[:8]}_{ts}.pdf"
    file_path = os.path.join(REPORTS_DIR, filename)

    if not REPORTLAB_AVAILABLE:
        # Fallback to plain text / mock pdf bytes if reportlab is not installed
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"ARGUS SECURITY REPORT\nScan ID: {scan.id}\nTarget: {scan.target_url}\nAttacks: {len(attacks)}")
        return file_path

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ArgusTitle",
        parent=styles["Heading1"],
        fontSize=22,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "ArgusSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        "ArgusSection",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=16,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "ArgusBody",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#334155"),
    )

    story = []

    # ── Header ───────────────────────────────────────────────────────────────
    story.append(Paragraph("Argus Security Report", title_style))
    story.append(Paragraph(
        f"Project: <b>{scan.project_name}</b> &nbsp;|&nbsp; "
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        subtitle_style,
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
    story.append(Spacer(1, 12))

    # ── Scan Summary ─────────────────────────────────────────────────────────
    story.append(Paragraph("Scan Summary", section_style))

    scores = [a.score for a in attacks]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    max_score = max(scores) if scores else 0.0
    risk_label = _score_label(max_score)

    summary_data = [
        ["Scan ID",          scan.id],
        ["Project",          scan.project_name],
        ["Target URL",       scan.target_url],
        ["Status",           scan.status.upper()],
        ["Started",          str(scan.started_at)[:19] + " UTC"],
        ["Finished",         str(scan.finished_at)[:19] + " UTC" if scan.finished_at else "—"],
        ["Total Attacks",    str(len(attacks))],
        ["Average Risk",     f"{avg_score} / 100"],
        ["Peak Risk",        f"{max_score} / 100  [{risk_label}]"],
    ]

    summary_table = Table(summary_data, colWidths=[5 * cm, 12 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",     (0, 0), (-1, -1), colors.HexColor("#1e293b")),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("PADDING",       (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # ── Attack Details ────────────────────────────────────────────────────────
    if attacks:
        story.append(Paragraph("Attack Details", section_style))

        for i, attack in enumerate(attacks, start=1):
            lbl   = _score_label(attack.score)
            color = _score_color(attack.score)

            header_style = ParagraphStyle(
                f"AH{i}",
                parent=body_style,
                textColor=color or colors.HexColor("#0f172a"),
                fontSize=10,
                spaceBefore=10,
                fontName="Helvetica-Bold",
            )
            story.append(Paragraph(
                f"Attack #{i} &nbsp;·&nbsp; {attack.category} "
                f"&nbsp;·&nbsp; Score: {attack.score:.0f}/100 [{lbl}]",
                header_style,
            ))

            detail_data = [
                ["Prompt",   (attack.prompt   or "")[:600]],
                ["Response", (attack.response or "")[:800]],
            ]
            detail_table = Table(detail_data, colWidths=[3 * cm, 14 * cm])
            detail_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
                ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE",   (0, 0), (-1, -1), 8),
                ("TEXTCOLOR",  (0, 0), (-1, -1), colors.HexColor("#334155")),
                ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
                ("PADDING",    (0, 0), (-1, -1), 5),
                ("VALIGN",     (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(detail_table)

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
    story.append(Paragraph(
        "Argus — LLM Security Platform &nbsp;|&nbsp; Confidential",
        ParagraphStyle(
            "Footer", parent=body_style,
            textColor=colors.HexColor("#94a3b8"),
            alignment=1, fontSize=8,
        ),
    ))

    doc.build(story)
    logger.info("PDF report saved: %s", file_path)
    return file_path
