from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.engine import Engine

from ...stats.source_stats import SourceStatRow, fetch_source_stats
from ..auth import AuthPrincipal, require_scope
from ..deps import get_engine


router = APIRouter(tags=["admin"])


def _stat_to_dict(r: SourceStatRow) -> dict[str, Any]:
    return {
        "source_name": r.source_name,
        "tier": r.tier,
        "legal_mode": r.legal_mode,
        "canonical_listings": r.canonical_listings,
        "raw_captures": r.raw_captures,
        "with_description": r.with_description,
        "with_photos": r.with_photos,
        "photo_coverage_pct": r.photo_coverage_pct,
        "intent_sale": r.intent_sale,
        "intent_rent": r.intent_rent,
        "intent_str": r.intent_str,
        "intent_auction": r.intent_auction,
        "category_apartment": r.category_apartment,
        "category_house": r.category_house,
        "category_land": r.category_land,
        "category_commercial": r.category_commercial,
        "has_legal_rule": r.has_legal_rule,
        "has_endpoint": r.has_endpoint,
    }


@router.get("/admin/source-stats")
def source_stats(
    _principal: Annotated[AuthPrincipal, Depends(require_scope("admin:read"))],
    engine: Annotated[Engine, Depends(get_engine)],
) -> dict[str, Any]:
    rows = fetch_source_stats(engine)
    return {
        "ok": True,
        "count": len(rows),
        "rows": [_stat_to_dict(r) for r in rows],
    }


@router.get("/admin", response_class=HTMLResponse)
def admin_home(_principal: Annotated[AuthPrincipal, Depends(require_scope("admin:read"))]) -> HTMLResponse:
    # Minimal internal operator page (not public UI).
    body = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>BG Real Estate Admin</title>
    <style>
      body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial; padding: 24px; }
      table { border-collapse: collapse; width: 100%; margin-top: 12px; }
      th, td { border: 1px solid #ddd; padding: 8px; }
      th { background: #f7f7f7; text-align: left; }
      code { background: #f2f2f2; padding: 2px 4px; border-radius: 4px; }
      .bar-wrap { display: flex; align-items: center; gap: 8px; min-width: 180px; }
      .bar-bg { flex: 1; height: 10px; background: #efefef; border-radius: 999px; overflow: hidden; }
      .bar-fill { height: 100%; background: #4f46e5; border-radius: 999px; }
      .small { font-size: 12px; color: #666; white-space: nowrap; }
    </style>
  </head>
  <body>
    <h2>Admin: Source Health</h2>
    <p>API: <code>/admin/source-stats</code> (requires <code>DATABASE_URL</code>)</p>
    <div id="status"></div>
    <table id="tbl" style="display:none">
      <thead>
        <tr>
          <th>Source</th>
          <th>Tier</th>
          <th>Legal mode</th>
          <th>Canonical listings</th>
          <th>Raw captures</th>
          <th>With description</th>
          <th>Photo coverage</th>
          <th>Intent breakdown</th>
          <th>Category breakdown</th>
          <th>Legal rule</th>
          <th>Endpoint</th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
    <script>
      async function run() {
        const status = document.getElementById('status');
        try {
          const res = await fetch('/admin/source-stats');
          const data = await res.json();
          if (!data.ok) {
            status.textContent = 'Not ready: ' + (data.error || 'unknown error');
            return;
          }
          const tbl = document.getElementById('tbl');
          const tbody = tbl.querySelector('tbody');
          tbody.innerHTML = '';
          for (const r of data.rows) {
            const tr = document.createElement('tr');
            const photoPct = Math.max(0, Math.min(100, Number(r.photo_coverage_pct || 0)));
            const intentTxt = 'sale=' + r.intent_sale + ', rent=' + r.intent_rent + ', str=' + r.intent_str + ', auction=' + r.intent_auction;
            const catTxt = 'apt=' + r.category_apartment + ', house=' + r.category_house + ', land=' + r.category_land + ', comm=' + r.category_commercial;
            tr.innerHTML = '<td>' + r.source_name + '</td>' +
              '<td>' + (r.tier ?? '') + '</td>' +
              '<td>' + (r.legal_mode ?? '') + '</td>' +
              '<td>' + r.canonical_listings + '</td>' +
              '<td>' + r.raw_captures + '</td>' +
              '<td>' + r.with_description + '</td>' +
              '<td><div class=\"bar-wrap\"><div class=\"bar-bg\"><div class=\"bar-fill\" style=\"width:' + photoPct + '%\"></div></div><span class=\"small\">' + photoPct.toFixed(2) + '% (' + r.with_photos + ')</span></div></td>' +
              '<td class=\"small\">' + intentTxt + '</td>' +
              '<td class=\"small\">' + catTxt + '</td>' +
              '<td>' + (r.has_legal_rule ? 'Y' : 'N') + '</td>' +
              '<td>' + (r.has_endpoint ? 'Y' : 'N') + '</td>';
            tbody.appendChild(tr);
          }
          tbl.style.display = '';
          status.textContent = 'OK (' + data.count + ' sources)';
        } catch (e) {
          status.textContent = 'Error: ' + e;
        }
      }
      run();
    </script>
  </body>
</html>"""
    return HTMLResponse(content=body)

