#!/usr/bin/env python3
"""Observe the public Recaudar Sinu route portal, without bulk data export."""
import argparse
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit, urlunsplit

from playwright.async_api import async_playwright

BASE = "https://recaudarsinu.com"
MAX_BODY = 2_000_000
MAX_RECORDS = 250


def safe_url(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.hostname or "", p.path, "", ""))


def schema(value, depth=0):
    """Record field names, types and array sizes, never scalar values."""
    if depth >= 6:
        return type(value).__name__
    if isinstance(value, dict):
        return {k: schema(v, depth + 1) for k, v in list(value.items())[:60]
                if not re.search(r"password|token|secret|email|phone|authorization|cookie", k, re.I)}
    if isinstance(value, list):
        return {"type": "array", "count": len(value),
                "item": schema(value[0], depth + 1) if value else None}
    return type(value).__name__


async def probe(output):
    report = {"checked_at": datetime.now(timezone.utc).isoformat(),
              "pages": [], "requests": [], "scripts": [], "errors": []}
    pending = set()
    seen_scripts = set()
    phase = "initial"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(locale="es-CO",
                                            timezone_id="America/Bogota")
        page = await context.new_page()

        async def observe(response, label):
            req = response.request
            if len(report["requests"]) >= MAX_RECORDS:
                return
            url = safe_url(response.url)
            ct = response.headers.get("content-type", "")
            if req.resource_type == "script":
                if url in seen_scripts:
                    return
                seen_scripts.add(url)
                entry = {"url": url, "status": response.status}
                # Only route-related URL path literals in public first-party scripts.
                if urlsplit(url).hostname == "recaudarsinu.com":
                    try:
                        if int(response.headers.get("content-length", "0")) <= MAX_BODY:
                            body = await response.body()
                            if len(body) <= MAX_BODY:
                                source = body.decode("utf-8", errors="replace")
                                candidates = re.findall(
                                    r"""["']((?:https?://[A-Za-z0-9.-]+)?/(?:api|graphql|v[0-9]+)/[A-Za-z0-9_./-]{1,150})["']""",
                                    source)
                                entry["route_related_path_literals"] = sorted({
                                    x for x in candidates if re.search(
                                        r"route|ruta|stop|parada|shape|schedule|horario|itiner|direction|sentido|graphql",
                                        x, re.I)})[:100]
                                # Minified clients often concatenate a base URL,
                                # a short endpoint fragment and a numeric ID.
                                if "src-pages-rutas" in url:
                                    literals = re.findall(
                                        r"""["'\x60]((?:https?://[A-Za-z0-9.-]+)?/[A-Za-z0-9_./-]{1,150})["'\x60]""",
                                        source)
                                    entry["route_path_fragments"] = sorted({
                                        x for x in literals if re.search(
                                            r"ruta|route|sentido|direction|parada|stop|kmz|kml|horario|itiner",
                                            x, re.I)})[:100]
                                entry["framework_markers"] = [
                                    x for x in ("__NEXT_DATA__", "webpack", "vite", "angular", "react", "leaflet", "mapbox")
                                    if x in source.lower() or x in source]
                                entry["bytes"] = len(body)
                    except Exception as e:
                        entry["inspection_error"] = type(e).__name__
                report["scripts"].append(entry)
                return
            if req.resource_type not in ("xhr", "fetch"):
                return
            item = {"phase": label, "url": url, "method": req.method,
                    "status": response.status, "content_type": ct,
                    "query_parameter_names": sorted(parse_qs(urlsplit(response.url).query,
                                                             keep_blank_values=True))}
            report["requests"].append(item)
            try:
                if req.post_data and "json" in req.headers.get("content-type", ""):
                    item["request_schema"] = schema(json.loads(req.post_data))
                if "json" in ct.lower() and int(response.headers.get("content-length", "0")) <= MAX_BODY:
                    body = await response.body()
                    if len(body) <= MAX_BODY:
                        item["response_schema"] = schema(json.loads(body))
                        item["bytes"] = len(body)
            except Exception as e:
                item["inspection_error"] = type(e).__name__

        def on_response(response):
            task = asyncio.create_task(observe(response, phase))
            pending.add(task)
            task.add_done_callback(pending.discard)

        page.on("response", on_response)

        def on_failed(req):
            if req.resource_type in ("xhr", "fetch", "document"):
                report["errors"].append({"phase": phase, "url": safe_url(req.url),
                                         "kind": "request_failed", "reason": req.failure})
        page.on("requestfailed", on_failed)

        async def snapshot(label):
            # Only aggregate indicators, not the stop database or page HTML.
            text = await page.locator("body").inner_text(timeout=10000)
            counts = re.findall(r"(\d+)\s+paradas", text, re.I)
            report["pages"].append({"phase": label, "url": safe_url(page.url),
                                    "title": await page.title(),
                                    "no_routes_message": "No se encontraron rutas" in text,
                                    "stop_count_labels": [int(n) for n in counts],
                                    "direction_switch_visible": await page.get_by_text(
                                        "CAMBIAR SENTIDO", exact=False).count() > 0,
                                    "script_sources": [
                                        safe_url(s) for s in await page.locator("script[src]").evaluate_all(
                                            "(elements) => elements.map(e => e.src)") if s.startswith("http")]})

        try:
            response = await page.goto(BASE + "/rutas", wait_until="domcontentloaded", timeout=45000)
            report["navigation_status"] = response.status if response else None
            try:
                await page.get_by_text("P1", exact=False).first.wait_for(timeout=20000)
            except Exception:
                pass
            # The initial route list can render before the direction and
            # stop data. Wait for the actual route UI instead of the P1 label.
            try:
                await page.get_by_text(re.compile(r"CAMBIAR\s+SENTIDO|\d+\s+paradas", re.I)).first.wait_for(
                    state="visible", timeout=25000)
            except Exception:
                pass
            await page.wait_for_timeout(5000)
            await snapshot(phase)
            # A single normal direction switch and a second route selection,
            # if present. Do not enumerate or scrape every route.
            switch = page.get_by_text(re.compile(r"CAMBIAR\s+SENTIDO", re.I)).first
            if await switch.count() and await switch.is_visible():
                phase = "direction_switch"
                await switch.click(timeout=5000)
                await page.wait_for_timeout(8000)
                await snapshot(phase)
            second = page.get_by_text(re.compile(r"D1\s*[–-]\s*DORADO", re.I)).first
            if await second.count() and await second.is_visible():
                phase = "second_route"
                await second.click(timeout=5000)
                await page.wait_for_timeout(8000)
                await snapshot(phase)
        except Exception as e:
            report["errors"].append({"phase": phase, "kind": type(e).__name__})
        finally:
            if pending:
                await asyncio.gather(*list(pending), return_exceptions=True)
            await browser.close()
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
    print("Report:", output)
    print("Navigation:", report.get("navigation_status"))
    print("XHR/fetch:", len(report["requests"]), "scripts:", len(report["scripts"]))
    print("Snapshots:", len(report["pages"]), "errors:", len(report["errors"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/recaudar-probe.json"))
    args = parser.parse_args()
    asyncio.run(probe(args.output))
