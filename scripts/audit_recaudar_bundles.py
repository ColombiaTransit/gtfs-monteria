#!/usr/bin/env python3
"""Inventory public Gatsby assets and passenger-transport references only."""
import asyncio
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from playwright.async_api import async_playwright

BASE = "https://recaudarsinu.com"
HOSTS = {"recaudarsinu.com", "www.recaudarsinu.com"}
PAGES = ["/", "/rutas", "/apps/movisinu", "/nosotros"]
LIMIT = 12_000_000
MAX_ASSETS = 100
TERMS = re.compile(r"horarios?|frecuencias?|paraderos?|paradas?|sentidos?|rutas?|itinerarios?|trayectos?|planific(?:ar|ador|acion)|veh[ií]culos?|ubicaci[oó]n|op[-_]?tra|movisin[uú]|websocket|schedule|headway|tripplanner|gtfs|realtime|graphql", re.I)
URL = re.compile(r"""https?://[A-Za-z0-9.-]+(?::[0-9]+)?(?:/[A-Za-z0-9_./%-]+)?""")
PATH = re.compile(r"""["'`]/([A-Za-z0-9_./-]{2,140})["'`]""")
SENSITIVE = re.compile(r"token|password|secret|login|auth|account|saldo|tarjeta|usuario|customer|payment|pago|recarga", re.I)
MAP = re.compile(r"sourceMappingURL\s*=\s*([^\s*]+)")
def first_party(url):
    p=urlsplit(url)
    return p.scheme=="https" and p.hostname in HOSTS and not p.username and not p.password
def public_path(x):
    return bool(TERMS.search(x)) and not SENSITIVE.search(x)
def inspect(source):
    urls=sorted({m.group() for m in URL.finditer(source) if public_path(m.group()) or (urlsplit(m.group()).hostname or "").endswith(".recaudarsinu.com") and not SENSITIVE.search(m.group())})
    paths=sorted({"/"+m.group(1) for m in PATH.finditer(source) if public_path(m.group(1))})
    # Counts of explicit terms only; avoid publishing snippets containing secrets.
    counts={}
    for m in TERMS.finditer(source):
        key=m.group().lower()
        counts[key]=counts.get(key,0)+1
    return {"transport_urls":urls[:100],"transport_paths":paths[:150],"term_counts":counts}
async def main():
    report={"pages":[],"assets":[],"errors":[]}
    assets=set()
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        context=await browser.new_context(locale="es-CO")
        page=await context.new_page()
        def seen(r):
            if r.request.resource_type=="script" and first_party(r.url):
                assets.add(r.url.split("?")[0])
        page.on("response",seen)
        for path in PAGES:
            try:
                r=await page.goto(BASE+path,wait_until="domcontentloaded",timeout=35000)
                await page.wait_for_timeout(3500)
                links=await page.locator("script[src],link[rel=preload],link[rel=prefetch]").evaluate_all("(els)=>els.map(e=>e.src||e.href)")
                assets.update(u.split("?")[0] for u in links if first_party(u) and urlsplit(u).path.endswith(".js"))
                report["pages"].append({"path":path,"status":r.status if r else None,"scripts":len(links)})
            except Exception as e:
                report["errors"].append({"page":path,"error":type(e).__name__})
        # Include public Gatsby page-data references for these pages.
        async def fetch(url):
            r=await context.request.get(url,timeout=25000,max_redirects=0)
            if r.status!=200:
                return r.status,None
            if int(r.headers.get("content-length","0"))>LIMIT:
                return r.status,None
            body=await r.body()
            return r.status,body if len(body)<=LIMIT else None
        for path in PAGES:
            u=BASE+"/page-data/"+(path.strip("/") or "index")+"/page-data.json"
            try:
                status,body=await fetch(u)
                info={"url":u,"status":status}
                if body:
                    d=json.loads(body)
                    info["component_chunk_name"]=d.get("componentChunkName")
                    info.update(inspect(body.decode("utf-8","replace")))
                report["assets"].append(info)
            except Exception as e:
                report["errors"].append({"url":u,"error":type(e).__name__})
        for u in sorted(assets)[:MAX_ASSETS]:
            info={"url":u}
            try:
                status,body=await fetch(u)
                info["status"]=status
                if body:
                    source=body.decode("utf-8","replace")
                    info.update(bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),**inspect(source))
                    matches=MAP.findall(source)
                    if matches:
                        murl=urljoin(u,matches[-1])
                        if first_party(murl) and urlsplit(murl).path.endswith(".map"):
                            ms,mb=await fetch(murl)
                            mi={"url":murl,"status":ms}
                            if mb:
                                try:
                                    data=json.loads(mb)
                                    content=data.get("sourcesContent") or []
                                    names=data.get("sources") or []
                                    selected=[s for n,s in zip(names,content) if isinstance(s,str) and not "node_modules" in n]
                                    mi["source_count"]=len(names)
                                    mi["first_party_source_count"]=len(selected)
                                    mi.update(inspect("\n".join(selected)))
                                    # Review individual first-party source files, including
                                    # relative URL literals such as rutas and rutas/{id}.
                                    mi["source_inventory"] = []
                                    for name, src in zip(names, content):
                                        if not isinstance(src, str) or "node_modules" in name:
                                            continue
                                        rel = sorted({
                                            m.group(1) for m in re.finditer(
                                                r"""["'`]([A-Za-z0-9_./-]*(?:rutas?|sentidos?|paradas?|paraderos?|horarios?|frecuencias?|itinerarios?|trayectos?|vehiculos?|tripplanner|gtfs|optra)[A-Za-z0-9_./-]*)["'`]""",
                                                src, re.I)
                                            if public_path(m.group(1)) and len(m.group(1)) <= 150
                                        })
                                        calls = []
                                        for line_no, line in enumerate(src.splitlines(), 1):
                                            if not TERMS.search(line) or SENSITIVE.search(line):
                                                continue
                                            if re.search(r"\b(?:fetch|axios|api|client|http)\b|\.(?:get|post|request)\s*\(", line, re.I):
                                                # Report only line numbers and literal passenger
                                                # path fragments, not complete source lines.
                                                calls.append(line_no)
                                        item = {"source":name.split("?")[0], "relative_transport_literals":rel[:100],
                                                "transport_call_line_numbers":calls[:100]}
                                        item.update(inspect(src))
                                        if rel or calls or item["transport_urls"] or item["transport_paths"]:
                                            mi["source_inventory"].append(item)
                                except (ValueError,TypeError):
                                    mi["parse_error"]=True
                            info["sourcemap"]=mi
            except Exception as e:
                info["error"]=type(e).__name__
                report["errors"].append({"url":u,"error":type(e).__name__})
            report["assets"].append(info)
        report["discovered_script_count"]=len(assets)
        report["script_limit_reached"]=len(assets)>MAX_ASSETS
        await browser.close()
    out=Path("artifacts/recaudar-bundle-audit.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    if report["errors"] or any(a.get("error") or a.get("sourcemap", {}).get("parse_error") for a in report["assets"]):
        raise SystemExit("Incomplete audit: review asset errors")
if __name__=="__main__":
    asyncio.run(main())
