#!/usr/bin/env python3
"""Generate investor presentation PDF with charts for Bulgaria Real Estate Platform.

Produces: output/pdf/investor-presentation-{date}.pdf
Requires: matplotlib, reportlab
"""
from __future__ import annotations

import io
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _ensure_deps():
    missing = []
    try:
        import matplotlib  # noqa: F401
    except ImportError:
        missing.append("matplotlib")
    try:
        import reportlab  # noqa: F401
    except ImportError:
        missing.append("reportlab")
    if missing:
        print(f"[ERROR] Missing: {', '.join(missing)}. Install with: pip install {' '.join(missing)}")
        sys.exit(1)

_ensure_deps()

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

W, H = landscape(A4)
MARGIN = 2 * cm
styles = getSampleStyleSheet()

BRAND_DARK = colors.HexColor("#1a1a2e")
BRAND_ACCENT = colors.HexColor("#0f3460")
BRAND_HIGHLIGHT = colors.HexColor("#e94560")
BRAND_LIGHT = colors.HexColor("#f5f5f5")
BRAND_GREEN = colors.HexColor("#16c79a")
BRAND_BLUE = colors.HexColor("#4361ee")


def _style(name, **kw):
    base = dict(
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=BRAND_DARK,
    )
    base.update(kw)
    return ParagraphStyle(name, **base)


TITLE = _style("SlideTitle", fontSize=26, fontName="Helvetica-Bold", leading=32, spaceAfter=12)
SUBTITLE = _style("SlideSubtitle", fontSize=14, leading=18, textColor=BRAND_ACCENT, spaceAfter=8)
BODY = _style("SlideBody", fontSize=11, leading=15, spaceAfter=6)
BULLET = _style("SlideBullet", fontSize=11, leading=15, leftIndent=18, bulletIndent=6, spaceAfter=4)
SECTION = _style("SectionHeader", fontSize=20, fontName="Helvetica-Bold", leading=26, textColor=BRAND_HIGHLIGHT, spaceAfter=10)
KPI_NUM = _style("KPINum", fontSize=28, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=BRAND_HIGHLIGHT)
KPI_LABEL = _style("KPILabel", fontSize=9, alignment=TA_CENTER, textColor=BRAND_ACCENT)
FOOTER = _style("Footer", fontSize=7, textColor=colors.gray, alignment=TA_RIGHT)


def _chart_to_image(fig, width=18 * cm, height=10 * cm):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=width, height=height)


def _page_break():
    return PageBreak()


def _kpi_strip(pairs):
    """pairs = [(number_str, label_str), ...]"""
    data = [[Paragraph(n, KPI_NUM) for n, _ in pairs],
            [Paragraph(l, KPI_LABEL) for _, l in pairs]]
    col_w = (W - 2 * MARGIN) / len(pairs)
    t = Table(data, colWidths=[col_w] * len(pairs), rowHeights=[36, 18])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, BRAND_ACCENT),
    ]))
    return t


def _data_table(header, rows, col_widths=None):
    all_rows = [header] + rows
    para_rows = []
    for i, row in enumerate(all_rows):
        style = _style("TCellH", fontSize=9, fontName="Helvetica-Bold", textColor=colors.white) if i == 0 else _style("TCell", fontSize=9)
        para_rows.append([Paragraph(str(c), style) for c in row])
    if not col_widths:
        col_widths = [(W - 2 * MARGIN) / len(header)] * len(header)
    t = Table(para_rows, colWidths=col_widths)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.Color(0.85, 0.85, 0.85)),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


# ── Charts ──────────────────────────────────────────────────────────

def chart_price_growth():
    fig, ax = plt.subplots(figsize=(8, 4))
    cities = ["Sofia", "Varna", "Burgas", "Plovdiv", "EU avg"]
    growth = [18, 17, 19, 13, 3.2]
    bars = ax.barh(cities, growth, color=["#4361ee", "#e94560", "#16c79a", "#f9c74f", "#adb5bd"])
    ax.set_xlabel("YoY Price Growth (%)", fontsize=10)
    ax.set_title("Residential Price Growth 2025 — Bulgaria vs EU", fontsize=12, fontweight="bold")
    for bar, val in zip(bars, growth):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val}%", va="center", fontsize=10, fontweight="bold")
    ax.set_xlim(0, 25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig


def chart_tam_sam_som():
    fig, ax = plt.subplots(figsize=(7, 5))
    from matplotlib.patches import FancyBboxPatch
    rects = [
        (0.1, 0.05, 0.8, 0.85, "#4361ee", "TAM\n€74.7M/yr\nBulgaria nationwide"),
        (0.2, 0.1, 0.6, 0.55, "#16c79a", "SAM\n€22.6M/yr\nVarna + Burgas coastal"),
        (0.3, 0.15, 0.4, 0.3, "#e94560", "SOM (Y3)\n€4.5–6.8M/yr\n20–30% share"),
    ]
    for x, y, w, h, col, label in rects:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                              facecolor=col, alpha=0.25, edgecolor=col, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=11, fontweight="bold", color=col)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("TAM / SAM / SOM", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return fig


def chart_revenue_projection():
    fig, ax = plt.subplots(figsize=(8, 4.5))
    years = ["Y1", "Y2", "Y3", "Y5"]
    revenue = [0.7, 2.3, 4.5, 8.0]
    costs = [0.14, 0.4, 0.8, 1.5]
    profit = [r - c for r, c in zip(revenue, costs)]

    x_pos = range(len(years))
    bar_w = 0.25
    ax.bar([p - bar_w for p in x_pos], revenue, bar_w, label="Revenue (€M)", color="#4361ee")
    ax.bar(list(x_pos), costs, bar_w, label="Costs (€M)", color="#adb5bd")
    ax.bar([p + bar_w for p in x_pos], profit, bar_w, label="Operating Profit (€M)", color="#16c79a")

    ax.set_xticks(x_pos)
    ax.set_xticklabels(years)
    ax.set_ylabel("€ Millions")
    ax.set_title("Revenue Projection — Conservative Case", fontsize=12, fontweight="bold")
    ax.legend(loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig


def chart_source_distribution():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    labels = ["Portals\n(imot.bg, Homes.bg,\nimoti.net, property.bg)", "Classifieds\n(OLX, alo.bg,\nBazar.bg, Imoti.info)",
              "Agencies\n(Address, SUPRIMMO,\nLUXIMMO, +10)", "International\n(Domaza, Indomio,\nRealistimo)",
              "STR/Vendors\n(Airbnb, Booking,\nAirDNA)", "Social\n(Telegram, FB,\nViber)"]
    sizes = [30, 22, 25, 8, 10, 5]
    colors_list = ["#4361ee", "#e94560", "#16c79a", "#f9c74f", "#7209b7", "#adb5bd"]
    explode = [0.05] * 6

    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, autopct="%1.0f%%",
                                       colors=colors_list, startangle=90, textprops={"fontsize": 8})
    for at in autotexts:
        at.set_fontsize(9)
        at.set_fontweight("bold")
    ax.set_title("Bulgarian RE Listing Distribution by Source Type", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig


def chart_varna_metrics():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    cats = ["Avg Price\n€/m²", "YoY Growth\n%", "STR ADR\n€/night", "STR Occupancy\n%"]
    varna_vals = [1900, 17, 65, 59]
    burgas_vals = [1700, 19, 58, 50]

    x = range(len(cats))
    ax1.bar([i - 0.15 for i in x], varna_vals, 0.3, label="Varna", color="#e94560")
    ax1.bar([i + 0.15 for i in x], burgas_vals, 0.3, label="Burgas", color="#4361ee")
    ax1.set_xticks(x)
    ax1.set_xticklabels(cats, fontsize=8)
    ax1.set_title("Varna vs Burgas — Key Metrics", fontsize=11, fontweight="bold")
    ax1.legend(fontsize=9)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    quarters = ["Q1'24", "Q2'24", "Q3'24", "Q4'24", "Q1'25", "Q2'25"]
    varna_prices = [1450, 1520, 1600, 1700, 1800, 1900]
    burgas_prices = [1250, 1320, 1400, 1480, 1580, 1700]
    ax2.plot(quarters, varna_prices, "o-", color="#e94560", linewidth=2, label="Varna")
    ax2.plot(quarters, burgas_prices, "s-", color="#4361ee", linewidth=2, label="Burgas")
    ax2.set_ylabel("€/m²")
    ax2.set_title("Price Trajectory (€/m²)", fontsize=11, fontweight="bold")
    ax2.legend(fontsize=9)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter("€%d"))

    fig.tight_layout()
    return fig


def chart_competitive_landscape():
    fig, ax = plt.subplots(figsize=(8, 5))
    platforms = {
        "imot.bg":           (3, 4, 300),
        "Homes.bg":          (4, 3, 250),
        "OLX.bg":            (5, 2, 200),
        "alo.bg":            (4, 3, 200),
        "BulgarianProperties": (2, 5, 150),
        "Address.bg":        (2, 4, 150),
        "SUPRIMMO":          (2, 4, 120),
        "Our Platform":      (9, 9, 400),
    }
    for name, (coverage, ux, size) in platforms.items():
        color = "#e94560" if name == "Our Platform" else "#4361ee"
        alpha = 1.0 if name == "Our Platform" else 0.5
        ax.scatter(coverage, ux, s=size, c=color, alpha=alpha, edgecolors="white", linewidth=1.5)
        offset = (8, 8) if name != "Our Platform" else (10, -15)
        ax.annotate(name, (coverage, ux), xytext=offset, textcoords="offset points",
                    fontsize=8, fontweight="bold" if name == "Our Platform" else "normal")

    ax.set_xlabel("Source Coverage (1–10)", fontsize=10)
    ax.set_ylabel("UX Quality (1–10)", fontsize=10)
    ax.set_title("Competitive Landscape: Coverage vs UX", fontsize=12, fontweight="bold")
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 10.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.axhline(5, color="gray", linewidth=0.5, linestyle="--", alpha=0.5)
    ax.axvline(5, color="gray", linewidth=0.5, linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig


def chart_unit_economics():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    segments = ["Agency\nPremium", "Featured\nListings", "Lead\nPackages", "STR\nAnalytics", "Developer\nShowcase", "AI Chat\nPremium"]
    revenue_k = [180, 120, 180, 77, 72, 60]
    ax1.barh(segments, revenue_k, color=["#4361ee", "#e94560", "#16c79a", "#7209b7", "#f9c74f", "#adb5bd"])
    ax1.set_xlabel("Annual Revenue (€K)")
    ax1.set_title("Year 1 Revenue by Segment", fontsize=11, fontweight="bold")
    for i, v in enumerate(revenue_k):
        ax1.text(v + 3, i, f"€{v}K", va="center", fontsize=9)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    cost_labels = ["Cloud\nInfra", "AI API", "Data\nAcq.", "Map\nTiles", "Team", "Marketing", "Legal"]
    cost_vals = [18, 9.6, 4.8, 2.4, 72, 24, 6]
    total_cost = sum(cost_vals)
    wedges, texts, autotexts = ax2.pie(cost_vals, labels=cost_labels, autopct=lambda p: f"€{p * total_cost / 100:.0f}K",
                                        colors=["#4361ee", "#e94560", "#16c79a", "#f9c74f", "#7209b7", "#adb5bd", "#ff6b6b"],
                                        textprops={"fontsize": 8}, startangle=90)
    for at in autotexts:
        at.set_fontsize(8)
    ax2.set_title(f"Year 1 Cost Breakdown (€{total_cost:.0f}K)", fontsize=11, fontweight="bold")
    fig.tight_layout()
    return fig


# ── Slide assembly ──────────────────────────────────────────────────

def build_slides():
    today = date.today().isoformat()
    out_dir = ROOT / "output" / "pdf"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"investor-presentation-{today}.pdf"

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=landscape(A4),
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.5 * cm, bottomMargin=1.2 * cm,
    )
    story = []

    # ── Slide 1: Title ──
    story.append(Spacer(1, 4 * cm))
    story.append(Paragraph("Bulgaria Real Estate Platform", TITLE))
    story.append(Paragraph("Unified marketplace for property search with 3D map & AI chat", SUBTITLE))
    story.append(Spacer(1, 1 * cm))
    story.append(_kpi_strip([
        ("30+", "Sources Aggregated"),
        ("€74.7M", "TAM (nationwide)"),
        ("€22.6M", "SAM (coastal)"),
        ("80%+", "Gross Margin"),
        ("45:1", "LTV:CAC Ratio"),
    ]))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(f"Investor Briefing — {today}", BODY))
    story.append(_page_break())

    # ── Slide 2: The Problem ──
    story.append(Paragraph("The Problem: Fragmented Distribution", SECTION))
    story.append(Paragraph(
        "Bulgaria has <b>30+ real estate platforms</b> with zero unified search. "
        "A buyer must check 10–15 sites to see 70% of supply — missing 30% entirely. "
        "No existing portal aggregates across sources, deduplicates, or provides 3D map/AI search.",
        BODY
    ))
    story.append(Spacer(1, 6 * mm))
    story.append(_chart_to_image(chart_source_distribution(), width=14 * cm, height=9 * cm))
    story.append(_page_break())

    # ── Slide 3: Market Size ──
    story.append(Paragraph("Market: Bulgaria Is EU's Fastest-Growing RE Market", SECTION))
    story.append(_chart_to_image(chart_price_growth(), width=18 * cm, height=8 * cm))
    story.append(Spacer(1, 4 * mm))
    story.append(_kpi_strip([
        ("€1,900/m²", "Varna Avg Price"),
        ("+17%", "Varna YoY Growth"),
        ("2.2%", "Mortgage Rate"),
        ("+26%", "New Loan Growth"),
        ("Jan 2026", "Eurozone Entry"),
    ]))
    story.append(_page_break())

    # ── Slide 4: Varna + Burgas Deep Dive ──
    story.append(Paragraph("Coastal Focus: Varna & Burgas", SECTION))
    story.append(_chart_to_image(chart_varna_metrics(), width=22 * cm, height=9 * cm))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "<b>Varna</b>: Black Sea capital, highest price growth, 819 new units Q2 2025, "
        "Airbnb revenue €14.2K/listing/year. "
        "<b>Burgas</b>: Construction boom (+51% YoY), 1,647 new apartments, slightly lower prices.",
        BODY
    ))
    story.append(_page_break())

    # ── Slide 5: TAM/SAM/SOM ──
    story.append(Paragraph("TAM / SAM / SOM", SECTION))
    story.append(_chart_to_image(chart_tam_sam_som(), width=14 * cm, height=10 * cm))
    story.append(Spacer(1, 4 * mm))
    story.append(_data_table(
        ["Market", "Annual Revenue", "Basis"],
        [
            ["TAM (Bulgaria)", "€74.7M", "Agency subs + listing fees + leads + STR + AI + developer"],
            ["SAM (Varna+Burgas)", "€22.6M", "28–35% coastal share of national activity"],
            ["SOM Year 1", "€0.7–1.1M", "3–5% of SAM, Varna-only MVP"],
            ["SOM Year 3", "€4.5–6.8M", "20–30% coastal share, multi-city"],
            ["SOM Year 5", "€8.0–10.0M", "35–45% national leader position"],
        ],
        col_widths=[5 * cm, 4 * cm, 13 * cm],
    ))
    story.append(_page_break())

    # ── Slide 6: Revenue Projection ──
    story.append(Paragraph("Revenue & Profit Projection", SECTION))
    story.append(_chart_to_image(chart_revenue_projection(), width=18 * cm, height=9 * cm))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Conservative case: breakeven by <b>Month 4–5</b> with 50 agency subscriptions. "
        "Year 1 operating profit: <b>€552K</b>. Year 3 target: <b>€3.7M profit</b> at 82% margin.",
        BODY
    ))
    story.append(_page_break())

    # ── Slide 7: Unit Economics ──
    story.append(Paragraph("Unit Economics Breakdown", SECTION))
    story.append(_chart_to_image(chart_unit_economics(), width=22 * cm, height=9 * cm))
    story.append(Spacer(1, 4 * mm))
    story.append(_kpi_strip([
        ("€5,400", "LTV (agency, 18mo)"),
        ("€120", "CAC (blended)"),
        ("45:1", "LTV:CAC"),
        ("80%", "Gross Margin"),
        ("0.4 mo", "Payback Period"),
    ]))
    story.append(_page_break())

    # ── Slide 8: Competitive Positioning ──
    story.append(Paragraph("Competitive Landscape", SECTION))
    story.append(_chart_to_image(chart_competitive_landscape(), width=18 * cm, height=10 * cm))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "No existing Bulgarian portal combines multi-source aggregation with modern UX. "
        "Our platform occupies the <b>top-right quadrant</b>: highest source coverage + best UX.",
        BODY
    ))
    story.append(_page_break())

    # ── Slide 9: Product Overview ──
    story.append(Paragraph("Product: LUN-Style Unified Marketplace", SECTION))
    story.append(Spacer(1, 4 * mm))
    story.append(_data_table(
        ["Feature", "Description", "Status"],
        [
            ["3D Map (Varna)", "OSM buildings + MapLibre GL JS + deck.gl extrusion", "MVP scope"],
            ["AI Chat Assistant", "Property-aware search via chat, always sees selected item + filters", "Planned"],
            ["Multi-Source Aggregation", "30+ sources normalized and deduplicated", "10 tier-1 done"],
            ["Owner-First Posting", "Owners post directly; agents appear as 'representative'", "Design phase"],
            ["STR Analytics", "AirDNA/Airbtics integration for rental yield intelligence", "Connector ready"],
            ["Price History", "Cross-source price tracking and trend charts", "DB schema ready"],
            ["CRM Chat Inbox", "Lead management with thread assignment and templates", "API scaffolded"],
            ["Reverse Publishing", "Authorized publishing to partner portals", "Phase 7"],
        ],
        col_widths=[5 * cm, 12 * cm, 5 * cm],
    ))
    story.append(_page_break())

    # ── Slide 10: Go-to-Market ──
    story.append(Paragraph("Go-to-Market Roadmap", SECTION))
    story.append(Spacer(1, 4 * mm))
    story.append(_data_table(
        ["Phase", "Timeline", "Scope", "Target"],
        [
            ["MVP", "Months 1–4", "Varna-only, 10 tier-1 sources, 3D map, AI chat", "5K MAU, 50 agencies"],
            ["Coastal", "Months 5–8", "Add Burgas + resorts, 25+ sources, STR analytics", "15K MAU, 200 agencies"],
            ["National", "Months 9–14", "Sofia, Plovdiv, Bansko, CRM, publishing", "50K MAU, 500 agencies"],
            ["International", "Months 15–24", "EU buyer funnel, multi-lang, cross-border tools", "100K MAU, market leader"],
        ],
        col_widths=[4 * cm, 4 * cm, 9 * cm, 5 * cm],
    ))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Revenue Flywheel", SECTION))
    story.append(Paragraph(
        "More sources → more complete listings → more buyer traffic → more leads for agencies → "
        "agency subscriptions increase → revenue funds more integration → <b>cycle reinforces</b>",
        BODY
    ))
    story.append(_page_break())

    # ── Slide 11: Risk & Mitigation ──
    story.append(Paragraph("Risk Factors & Mitigation", SECTION))
    story.append(Spacer(1, 4 * mm))
    story.append(_data_table(
        ["Risk", "Severity", "Mitigation"],
        [
            ["Portal blocking / legal action", "Medium", "Fixture-first testing; legal review per source; partnership priority"],
            ["Agency resistance", "Medium", "Free tier + lead value exceeds fee; partner incentives"],
            ["Market cooling post-euro", "Low", "Platform value is market-condition agnostic"],
            ["OSM data gaps for 3D map", "Low", "Fallback to 2D where 3D data incomplete"],
            ["GDPR / data protection", "Medium", "Consent gates; no PII in scraped data; proper DPO"],
            ["Competition: portal consortium", "Low", "First-mover + network effects from buyer traffic"],
        ],
        col_widths=[5.5 * cm, 3 * cm, 13.5 * cm],
    ))
    story.append(_page_break())

    # ── Slide 12: Team & Ask ──
    story.append(Paragraph("Summary", SECTION))
    story.append(Spacer(1, 6 * mm))
    story.append(_kpi_strip([
        ("30+", "Sources"),
        ("€74.7M", "TAM"),
        ("€22.6M", "SAM"),
        ("80%+", "Margin"),
        ("Month 5", "Breakeven"),
    ]))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        "<b>Bulgaria's real estate market is the EU's fastest-growing</b>, yet its digital infrastructure is a decade behind. "
        "30+ fragmented portals, zero aggregation, no 3D maps, no AI search. "
        "Our platform fills this gap with a LUN-style unified marketplace starting from Varna — "
        "the region with the highest price growth and strongest STR demand.",
        BODY
    ))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(
        "Sources: NSI Bulgaria, Eurostat, Colliers Bulgaria, BulgarianProperties, "
        "AirDNA, Airbtics, GlobalPropertyGuide, Investropa, CBRE, BNP Paribas",
        FOOTER
    ))

    doc.build(story)
    print(f"[OK] Investor presentation: {out_path}")
    print(f"     {out_path.stat().st_size / 1024:.0f} KB, {len(story)} elements")
    return out_path


if __name__ == "__main__":
    build_slides()
