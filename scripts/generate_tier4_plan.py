#!/usr/bin/env python3
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _ensure_reportlab() -> None:
    try:
        import reportlab  # noqa: F401
    except ImportError:
        print("[ERROR] Missing dependency: reportlab. Install with: pip install reportlab")
        sys.exit(1)


def build_tier4_plan() -> Path:
    _ensure_reportlab()

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    out_dir = ROOT / "docs" / "exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_pdf = out_dir / "Tier4plan.pdf"
    out_md = out_dir / "Tier4plan.md"
    today = date.today().isoformat()

    markdown = f"""# Tier-4 Social Collection Plan

Date: {today}

## Goal
Build a legal-safe tier-4 social intelligence layer that stores social links in the registry database, stores each message/post as a separate CRM message row, and keeps all fixture tests fully offline.

## What to do with links
Every known tier-4 social URL should be inserted into `source_endpoint` using endpoint kind `social_channel`, while preserving source-level legal policy in `source_legal_rule`. Links are divided into primary and related URLs so operators can prioritize official endpoints first.

## What may be needed
Per-platform credentials for official APIs, operator approval workflows for consent-restricted sources, and moderation/redaction checks before any message is saved. For Facebook/Instagram/Threads, ingestion should remain manual/consent-driven until explicit authorization paths are in place.

## Options by platform
Telegram and X can run via official API ingestion with strong rate limits and audit metadata. Facebook/Instagram/Threads should run in assisted-manual mode unless official API scopes and app review are approved. Viber and WhatsApp should run only under explicit opt-in or official business/vendor channels.

## Database output model
Use `source_endpoint` for links, and `lead_thread` + `lead_message` for one row per post/message. Raw payload snapshots should be retained in `raw_capture` with redaction metadata and parser version for traceability.

## Execution order
First sync tier-4 links to DB, then seed/ingest social messages (fixture-first), then validate extraction quality and move to operator-reviewed live ingestion for explicitly allowed channels only.
"""
    out_md.write_text(markdown, encoding="utf-8")

    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=18, leading=22, spaceAfter=10)
    head = ParagraphStyle("Head", parent=styles["Heading2"], fontSize=13, leading=16, spaceAfter=6)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.5, leading=14, spaceAfter=8)

    doc = SimpleDocTemplate(str(out_pdf), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=1.8 * cm)
    story = [
        Paragraph("Tier-4 Social Collection Plan", title),
        Paragraph(f"Date: {today}", body),
        Spacer(1, 4),
        Paragraph("Goal", head),
        Paragraph("Build a legal-safe tier-4 social intelligence layer that stores social links in the registry database, stores each message/post as a separate CRM message row, and keeps all fixture tests fully offline.", body),
        Paragraph("What to do with links", head),
        Paragraph("Every known tier-4 social URL should be inserted into source_endpoint using endpoint kind social_channel, while preserving source-level legal policy in source_legal_rule. Links are divided into primary and related URLs so operators can prioritize official endpoints first.", body),
        Paragraph("What may be needed", head),
        Paragraph("Per-platform credentials for official APIs, operator approval workflows for consent-restricted sources, and moderation/redaction checks before any message is saved. For Facebook/Instagram/Threads, ingestion remains manual/consent-driven until explicit authorization paths are in place.", body),
        Paragraph("Options by platform", head),
        Paragraph("Telegram and X can run via official API ingestion with strong rate limits and audit metadata. Facebook/Instagram/Threads should run in assisted-manual mode unless official API scopes and app review are approved. Viber and WhatsApp should run only under explicit opt-in or official business/vendor channels.", body),
        Paragraph("Database output model", head),
        Paragraph("Use source_endpoint for links, and lead_thread plus lead_message for one row per post/message. Raw payload snapshots should be retained in raw_capture with redaction metadata and parser version for traceability.", body),
        Paragraph("Execution order", head),
        Paragraph("First sync tier-4 links to DB, then seed/ingest social messages (fixture-first), then validate extraction quality and move to operator-reviewed live ingestion for explicitly allowed channels only.", body),
    ]
    doc.build(story)
    print(f"[OK] wrote {out_md}")
    print(f"[OK] wrote {out_pdf}")
    return out_pdf


if __name__ == "__main__":
    build_tier4_plan()
