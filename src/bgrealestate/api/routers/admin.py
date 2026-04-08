from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine

from ...stats.source_stats import fetch_source_stats


router = APIRouter(tags=["admin"])


@router.get("/admin/source-stats")
def source_stats() -> dict[str, Any]:
    url = os.getenv("DATABASE_URL")
    if not url:
        return {"ok": False, "error": "DATABASE_URL not set"}
    engine = create_engine(url, pool_pre_ping=True)
    rows = fetch_source_stats(engine)
    return {
        "ok": True,
        "count": len(rows),
        "rows": [
            {
                "source_name": r.source_name,
                "canonical_listings": r.canonical_listings,
                "raw_captures": r.raw_captures,
                "with_description": r.with_description,
            }
            for r in rows
        ],
    }


@router.get("/admin", response_class=HTMLResponse)
def admin_home() -> HTMLResponse:
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
          <th>Canonical listings</th>
          <th>Raw captures</th>
          <th>With description</th>
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
            tr.innerHTML = '<td>' + r.source_name + '</td>' +
              '<td>' + r.canonical_listings + '</td>' +
              '<td>' + r.raw_captures + '</td>' +
              '<td>' + r.with_description + '</td>';
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

