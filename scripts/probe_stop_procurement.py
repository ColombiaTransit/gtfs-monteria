#!/usr/bin/env python3
"""Locate public procurement annexes, inspect document metadata and text coverage."""
import io
import json
import re
import subprocess
import tempfile
import unicodedata
import zipfile
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup

OUT = Path("artifacts/stop-procurement.json")
DATA = "https://www.datos.gov.co"
PROC1 = "18-1-193585"
PROC2 = ("CO1.REQ.9479470", "CO1.REQ.9771263", "SI-MCA-002-2026")
CONTRACT = "CO1.PCCNTR.9318841"
DOC_IDS = {"804228578": "INFORME DE GESTION FINAL BIG.pdf", "804228575": "ACTA DE EJECUCION FINAL BIGSIGNS.pdf", "804228571": "ACTA DE LIQUIDACION BILATERAL BIGSIGNS.pdf"}
MAX_BYTES = 65 * 1024 * 1024
HOSTS = {"www.datos.gov.co", "datos.gov.co", "www.contratos.gov.co", "contratos.gov.co",
         "community.secop.gov.co", "www.colombialicita.com", "colombialicita.com",
         "buscasecop.com", "www.buscasecop.com", "www.monteriaamable.gov.co", "monteriaamable.gov.co"}
S = requests.Session()
S.headers.update({"User-Agent": "ColombiaTransit-research/1.0", "Accept": "*/*"})
REPORT = {"queries": [], "documents": [], "errors": []}
PRIORITY = re.compile(r"planos|anexos?|especificaciones|estudios previos|informe de gestion final|acta de ejecucion final|acta de liquidacion|inventario|ubicacion|listado|georreferen", re.I)


def norm(s):
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()


def request(url, params=None, limit=MAX_BYTES):
    if urlsplit(url).hostname not in HOSTS or urlsplit(url).scheme != "https":
        raise ValueError("unapproved source host")
    with S.get(url, params=params, timeout=(15, 90), stream=True) as r:
        r.raise_for_status()
        if urlsplit(r.url).hostname not in HOSTS:
            raise ValueError("unexpected redirect host")
        b = bytearray()
        for block in r.iter_content(65536):
            b.extend(block)
            if len(b) > limit:
                raise ValueError("response too large")
        return bytes(b), r.url


def jsonget(url, params=None):
    return json.loads(request(url, params, 8_000_000)[0])


def safe_error(source, exc):
    REPORT["errors"].append({"source": source, "kind": type(exc).__name__,
                             "status": getattr(getattr(exc, "response", None), "status_code", None)})


def socrata(dataset, filters):
    try:
        meta = jsonget(f"{DATA}/api/views/{dataset}.json")
        cols = {c["fieldName"]: c.get("name", "") for c in meta["columns"]}
        types = {c["fieldName"]: c.get("dataTypeName") for c in meta["columns"]}
        def literal(k, v):
            if types.get(k) in ("number", "money") and str(v).isdigit():
                return str(v)
            return "'" + str(v).replace("'", "''") + "'"
        valid = [(k, values) for k, values in filters if k in cols]
        if not valid:
            raise ValueError("no expected filter columns")
        where = " OR ".join(f"{k} in ({','.join(literal(k, v) for v in values)})" for k,values in valid)
        rows = jsonget(f"{DATA}/resource/{dataset}.json", {"$where": where, "$limit": 500})
        REPORT["queries"].append({"dataset": dataset, "columns": cols, "where": where, "rows": len(rows),
                                  "possibly_truncated": len(rows) == 500})
        return rows
    except Exception as e:
        safe_error(dataset, e)
        return []


def url_value(v):
    if isinstance(v, dict):
        v = v.get("url")
    return v if isinstance(v, str) and v.startswith(("http://", "https://")) else None


def add_document(name, url, source):
    if not url:
        return
    if url.startswith("http://"):
        url = "https://" + url[len("http://"):]
    if urlsplit(url).hostname not in HOSTS:
        return
    if any(d["url"] == url for d in REPORT["documents"]):
        return
    REPORT["documents"].append({"name": name.strip()[:250], "url": url, "source": source,
                                "priority": bool(PRIORITY.search(norm(name)))})


def html_index(url):
    try:
        raw, final = request(url, limit=8_000_000)
        soup = BeautifulSoup(raw, "html.parser")
        links = 0
        for a in soup.find_all("a", href=True):
            name = a.get_text(" ", strip=True)
            href = urljoin(final, a["href"])
            if re.search(r"documento|archivo|descarga|download|retrievefile|verdocumento|\.pdf|\.zip", href, re.I):
                add_document(name or "unnamed document", href, final)
                links += 1
            elif PRIORITY.search(norm(name)):
                add_document(name, href, final)
                links += 1
        REPORT["queries"].append({"page": url, "title": soup.title.get_text(" ",strip=True) if soup.title else "",
                                  "links_found": links})
    except Exception as e:
        safe_error(url, e)


def pdf_summary(data):
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)/"document.pdf"
        p.write_bytes(data)
        result = subprocess.run(["pdftotext","-layout",str(p),"-"],capture_output=True,timeout=90)
        if result.returncode:
            return {"text_extraction_failed": True}
        pages = result.stdout.decode("utf-8",errors="replace").split("\f")
        if pages and not pages[-1].strip():
            pages.pop()
        terms = re.compile(r"coordenadas?|latitud|longitud|georreferen|ubicaci[oó]n|inventario|listado|localizaci[oó]n|direcci[oó]n|paradero|colombina|t[oó]tem|\b(?:BD|CO)\d{3}\b|\bM10\d{2}\b", re.I)
        coord = re.compile(r"(?<!\d)8[.,]\d{4,}\s*[,; /]+\s*-?75[.,]\d{4,}")
        matches = []
        for i, page in enumerate(pages,1):
            hits = len(terms.findall(page))
            if hits:
                matches.append({"page":i,"keyword_hits":hits,"coordinate_pair_candidates":len(coord.findall(page)),
                                "stop_code_candidates":len(set(re.findall(r"\b(?:BD|CO)\d{3}\b|\bM10\d{2}\b",page,re.I)))})
        return {"pages":len(pages),"pages_with_text":sum(bool(p.strip()) for p in pages),
                "keyword_pages":sorted(matches,key=lambda m:(m["coordinate_pair_candidates"],m["stop_code_candidates"],m["keyword_hits"]),reverse=True)[:40]}


def inspect_doc(doc):
    try:
        blob, _ = request(doc["url"])
        doc["bytes"] = len(blob)
        if blob.startswith(b"%PDF"):
            doc["format"] = "pdf"
            doc["analysis"] = pdf_summary(blob)
        elif zipfile.is_zipfile(io.BytesIO(blob)):
            doc["format"] = "zip"
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                members = [m for m in z.infolist() if not m.is_dir()]
                doc["members"] = [{"name":m.filename,"bytes":m.file_size} for m in members[:150]]
                doc["member_count"] = len(members)
                for m in members[:100]:
                    if m.filename.lower().endswith(".pdf") and m.file_size <= MAX_BYTES and PRIORITY.search(norm(m.filename)):
                        try:
                            next(x for x in doc["members"] if x["name"]==m.filename)["analysis"] = pdf_summary(z.read(m))
                        except Exception:
                            pass
        else:
            doc["format"] = "not_pdf_or_zip"
    except Exception as e:
        doc["download_error"] = type(e).__name__
        doc["http_status"] = getattr(getattr(e,"response",None),"status_code",None)


def main():
    # Query the observed field names separately to isolate schema/type errors.
    for filters in (
        [("n_mero_de_contrato", (CONTRACT,))],
        [("id_documento", tuple(DOC_IDS))],
        [("proceso", PROC2)],
    ):
        rows = socrata("dmgg-8hin", filters)
        for r in rows:
            add_document(r.get("nombre_archivo", ""), url_value(r.get("url_descarga_documento")), "SECOP II 2026 archive")
    # Public SECOP II download URL pattern; IDs originate from the contract index.
    # These are candidate URLs until the returned PDF is validated.
    for doc_id, name in DOC_IDS.items():
        add_document(name, "https://community.secop.gov.co/Public/Archive/RetrieveFile/Index?DocUniqueIdentifier=&DocumentId="+doc_id+"&InCommunity=False&InPaymentGateway=False", "SECOP II direct URL candidate")
    # Exact SECOP I constancia only; LP-001-2018 is not globally unique.
    rows = socrata("f789-7hwg", [("numero_de_constancia",(PROC1,))])
    urls = set()
    for r in rows:
        if str(r.get("numero_de_constancia")) != PROC1:
            continue
        u = url_value(r.get("ruta_proceso_en_secop_i"))
        if u:
            urls.add("https://" + u[7:] if u.startswith("http://") else u)
    urls.add("https://www.contratos.gov.co/consultas/detalleProceso.do?numConstancia="+PROC1)
    for u in sorted(urls):
        html_index(u)
    # Limit downloads to the documents directly relevant to physical stops.
    for d in sorted(REPORT["documents"],key=lambda x: (not bool(re.search(r"planos|anexo|informe de gestion final",norm(x["name"]))),x["name"]))[:100]:
        if d["priority"]:
            inspect_doc(d)
    REPORT["summary"] = {"document_links": len(REPORT["documents"]), "pdf_or_zip_downloads": sum(d.get("format") in ("pdf","zip") for d in REPORT["documents"]), "download_errors": sum("download_error" in d for d in REPORT["documents"])}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(REPORT,ensure_ascii=False))


if __name__ == "__main__":
    main()
