r"""Fetch per-product support/troubleshooting docs from the web
and save them locally as plain text (one file per product id).

Run once at build time:  venv\Scripts\python.exe -X utf8 scripts\fetch_product_docs.py

Fetches are cached - files already present in data/shop/product_docs/
are skipped, so re-runs only fetch what is missing.

Failed fetches (404 / blocked / empty) are logged and skipped; the
app simply falls back to the generic troubleshooting guide for
products without a doc.
"""

import json
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))

CATALOG_FILE = PROJECT_ROOT / "data" / "shop" / "catalog.json"

DOCS_DIR = PROJECT_ROOT / "data" / "shop" / "product_docs"

TIMEOUT_SECONDS = 15

MIN_TEXT_LENGTH = 150

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Verified Samsung India support model codes (discovered and checked
# against https://www.samsung.com/in/support/model/<code>/).
# Only these products have live per-product support pages; the rest
# fall back to the generic troubleshooting guide at query time.

SUPPORT_CODE_MAP = {
    "P001": "SM-S938BZBCINS",  # Galaxy S25 Ultra
    "P002": "SM-S936BZSBINS",  # Galaxy S25+
    "P003": "SM-S928BZTCINS",  # Galaxy S24 Ultra
    "P006": "SM-S931BZSCINS",  # Galaxy S25
    "P018": "SM-F741BLBAINS",  # Galaxy Z Flip6
    "P019": "SM-F956BDBDINS",  # Galaxy Z Fold6
    "A001": "SM-R630NZAAINU",  # Galaxy Buds3 Pro
    "A002": "SM-R530NZAAINU",  # Galaxy Buds2 Pro
    "A008": "SM-R390NZSAINU",  # Galaxy Fit3
    # ---- 2025 / 2026 generation (live support pages) ----
    "P020": "SM-S948BZKBINS",  # Galaxy S26 Ultra (verified live)
    "P021": "SM-S947BZKBINS",  # Galaxy S26+
    "P022": "SM-S942BZKBINS",  # Galaxy S26
    "P023": "SM-F966BDBDINS",  # Galaxy Z Fold7
    "P024": "SM-F766BLBAINS",  # Galaxy Z Flip7
    "P025": "SM-F761BZGCINS",  # Galaxy Z Flip7 FE
    "P026": "SM-A566EZKAINS",  # Galaxy A56 5G
    "P027": "SM-A366EZKAINS",  # Galaxy A36 5G
    "P028": "SM-S761BZGCINS",  # Galaxy S25 FE
    "A015": "SM-L320NZKAINU",  # Galaxy Watch8 40mm
    "A016": "SM-L330NZKAINU",  # Galaxy Watch8 44mm
    "A017": "SM-L505NZKAINU",  # Galaxy Watch8 Classic
    "A018": "SM-L716BZKAINU",  # Galaxy Watch Ultra 2
    "A019": "SM-Q511NZAAINU",  # Galaxy Ring 2
    "A020": "SM-R540NZAAINU",  # Galaxy Buds4
    "A021": "SM-R640NZAAINU",  # Galaxy Buds4 Pro
    "L015": "NP960XJG-KG4IN",  # Galaxy Book6 Pro
    "L016": "NP960XJX-KG1IN",  # Galaxy Book6 Ultra
    "L017": "NP750XJG-KG1IN",  # Galaxy Book6
}

# Official Samsung India product/specs page for each new product.
# Used as a fallback when the per-model support page 404s, so the
# doc still contains the full official specification content.

SPECS_PAGE_MAP = {
    "P020": "https://www.samsung.com/in/smartphones/galaxy-s26-ultra/specs/",
    "P021": "https://www.samsung.com/in/smartphones/galaxy-s26-plus/specs/",
    "P022": "https://www.samsung.com/in/smartphones/galaxy-s26/specs/",
    "P023": "https://www.samsung.com/in/smartphones/galaxy-z-fold7/specs/",
    "P024": "https://www.samsung.com/in/smartphones/galaxy-z-flip7/specs/",
    "P025": "https://www.samsung.com/in/smartphones/galaxy-z-flip7-fe/specs/",
    "P026": "https://www.samsung.com/in/smartphones/galaxy-a/galaxy-a56-5g-awesome-graphite-256gb-sm-a566ezkhins",
    "P027": "https://www.samsung.com/in/smartphones/galaxy-a/galaxy-a36-5g-awesome-black-256gb-sm-a366ezkkins/",
    "P028": "https://news.samsung.com/in/meet-samsung-galaxy-s25-fe-the-gateway-to-the-galaxy-ai-and-flagship-essentials",
    "A015": "https://www.samsung.com/in/watches/galaxy-watch/galaxy-watch8-40mm-graphite-bluetooth-sm-l320ndaains/",
    "A016": "https://www.samsung.com/in/watches/galaxy-watch/galaxy-watch8-44mm-graphite-bluetooth-sm-l330ndaains/",
    "A017": "https://www.samsung.com/in/watches/galaxy-watch/galaxy-watch8-classic-46mm-black-lte-sm-l505fzkains/",
    "A018": "https://www.samsung.com/in/watches/galaxy-watch/galaxy-watch-ultra2-titanium-silver-lte-sm-l715fzsains/",
    "A019": "https://www.samsung.com/in/rings/all-rings/",
    "A020": "https://www.samsung.com/in/audio-sound/galaxy-buds/galaxy-buds4-black-sm-r540nzkainu/",
    "A021": "https://www.samsung.com/in/audio-sound/galaxy-buds4-pro/buy/",
    "L015": "https://www.samsung.com/in/computers/galaxy-book/galaxy-book6-pro/",
    "L016": "https://www.samsung.com/in/computers/galaxy-book/galaxy-book6-ultra-ultra-7-32gb-1tb-np960ujh-xg3in/",
    "L017": "https://www.samsung.com/in/computers/galaxy-book/galaxy-book6-16-inch-touch-u7-ultra-7-16gb-512gb-np760xjg-kg2in/",
}

SUPPORT_URL_TEMPLATE = (
    "https://www.samsung.com/in/support/model/{code}/"
)

# ---------------------------------------------------------------
# WAYBACK MODE
# ---------------------------------------------------------------
# Samsung India has de-listed older models (no live pages), but the
# Wayback Machine still holds archived copies of their support pages.
# Per product: candidate Samsung model-code prefixes for the support
# page (CDX prefix search), plus candidate product-page URL prefixes
# (used to recover a full model code from an archived product page
# when the support page cannot be found by the base code).

WAYBACK_PRODUCTS = {
    "A003": {  # Galaxy Buds3
        "codes": ["SM-R620"],
        "pages": ["www.samsung.com/in/audio-sound/galaxy-buds/galaxy-buds3"],
    },
    "A004": {  # Galaxy Buds FE
        "codes": ["SM-R400"],
        "pages": ["www.samsung.com/in/audio-sound/galaxy-buds/galaxy-buds-fe"],
    },
    "A005": {  # Galaxy Watch7 40mm
        "codes": ["SM-L310"],
        "pages": ["www.samsung.com/in/watches/galaxy-watch/galaxy-watch7-40mm"],
    },
    "A006": {  # Galaxy Watch7 44mm
        "codes": ["SM-L315"],
        "pages": ["www.samsung.com/in/watches/galaxy-watch/galaxy-watch7-44mm"],
    },
    "A007": {  # Galaxy Watch Ultra
        "codes": ["SM-L700"],
        "pages": ["www.samsung.com/in/watches/galaxy-watch/galaxy-watch-ultra"],
    },
    "A009": {  # Galaxy Ring
        "codes": ["SM-Q501"],
        "pages": [
            "www.samsung.com/in/watches/galaxy-ring",
            "www.samsung.com/in/wearables/galaxy-ring",
        ],
    },
    "A010": {  # 45W Super Fast Charger
        "codes": ["EP-T4510"],
        "pages": [
            "www.samsung.com/in/mobile-accessories/45w-super-fast-charger",
            "www.samsung.com/in/accessories/45w-super-fast-charger",
        ],
    },
    "A011": {  # 25W Super Fast Charger
        "codes": ["EP-T2510"],
        "pages": [
            "www.samsung.com/in/mobile-accessories/25w-super-fast-charger",
            "www.samsung.com/in/accessories/25w-super-fast-charger",
        ],
    },
    "A012": {  # 10000mAh 25W Power Bank
        "codes": ["EB-P3400"],
        "pages": ["www.samsung.com/in/mobile-accessories/10000mah-25w-power-bank"],
    },
    "A013": {  # 20000mAh 45W Power Bank
        "codes": ["EB-P4520"],
        "pages": ["www.samsung.com/in/mobile-accessories/20000mah-45w-power-bank"],
    },
    "A014": {  # SmartTag2
        "codes": ["EI-T5600", "SM-T560"],
        "pages": ["www.samsung.com/in/mobile-accessories/smarttag2"],
    },
    "L001": {  # Galaxy Book4
        "codes": ["NP750XGK", "NP750XGJ"],
        "pages": ["www.samsung.com/in/computers/galaxy-book/galaxy-book4-15"],
    },
    "L002": {  # Galaxy Book4 Pro
        "codes": ["NP940XGK", "NP940XGJ"],
        "pages": ["www.samsung.com/in/computers/galaxy-book/galaxy-book4-pro"],
    },
    "L003": {  # Galaxy Book4 360
        "codes": ["NP750XGK", "NP750XGJ"],
        "pages": ["www.samsung.com/in/computers/galaxy-book/galaxy-book4-360"],
    },
    "L004": {  # Galaxy Book4 Edge
        "codes": ["NP750XQB", "NP940XMB"],
        "pages": ["www.samsung.com/in/computers/galaxy-book/galaxy-book4-edge"],
    },
    "L005": {  # Galaxy Book4 Ultra
        "codes": ["NP960XGK", "NP960XGJ"],
        "pages": ["www.samsung.com/in/computers/galaxy-book/galaxy-book4-ultra"],
    },
    "L006": {  # Galaxy Book5 Pro
        "codes": ["NP960XGK", "NP750XHD"],
        "pages": ["www.samsung.com/in/computers/galaxy-book/galaxy-book5-pro"],
    },
    "L007": {  # Galaxy Book3
        "codes": ["NP750XFG"],
        "pages": ["www.samsung.com/in/computers/galaxy-book/galaxy-book3-15"],
    },
    "L008": {  # Galaxy Book3 Pro 360
        "codes": ["NP730XFG"],
        "pages": ["www.samsung.com/in/computers/galaxy-book/galaxy-book3-pro-360"],
    },
    "L009": {  # Galaxy Book3 Ultra
        "codes": ["NP960XFG"],
        "pages": ["www.samsung.com/in/computers/galaxy-book/galaxy-book3-ultra"],
    },
    "L010": {  # Galaxy Book3 360
        "codes": ["NP730XFG"],
        "pages": ["www.samsung.com/in/computers/galaxy-book/galaxy-book3-360"],
    },
    "L011": {  # Galaxy Book2 360
        "codes": ["NP730QFG"],
        "pages": ["www.samsung.com/in/computers/galaxy-book/galaxy-book2-360"],
    },
    "L012": {  # Galaxy Book Go
        "codes": ["NP340XNA"],
        "pages": ["www.samsung.com/in/computers/galaxy-book/galaxy-book-go"],
    },
    "L013": {  # Galaxy Chromebook Plus
        "codes": ["XE355QBA"],
        "pages": ["www.samsung.com/in/computers/galaxy-book/galaxy-chromebook-plus"],
    },
    "L014": {  # Galaxy Book5 Pro 360
        "codes": ["NP960XGK"],
        "pages": ["www.samsung.com/in/computers/galaxy-book/galaxy-book5-pro-360"],
    },
    "P004": {  # Galaxy A55 5G
        "codes": ["SM-A556E"],
        "pages": ["www.samsung.com/in/smartphones/galaxy-a55-5g"],
    },
    "P005": {  # Galaxy M35 5G
        "codes": ["SM-M356B"],
        "pages": ["www.samsung.com/in/smartphones/galaxy-m35-5g"],
    },
    "P007": {  # Galaxy S24 FE
        "codes": ["SM-S721B"],
        "pages": ["www.samsung.com/in/smartphones/galaxy-s24-fe"],
    },
    "P008": {  # Galaxy A35 5G
        "codes": ["SM-A356E"],
        "pages": ["www.samsung.com/in/smartphones/galaxy-a35-5g"],
    },
    "P009": {  # Galaxy A26 5G
        "codes": ["SM-A266B"],
        "pages": ["www.samsung.com/in/smartphones/galaxy-a26-5g"],
    },
    "P010": {  # Galaxy A25 5G
        "codes": ["SM-A256E"],
        "pages": ["www.samsung.com/in/smartphones/galaxy-a25-5g"],
    },
    "P011": {  # Galaxy A16 5G
        "codes": ["SM-A166E"],
        "pages": ["www.samsung.com/in/smartphones/galaxy-a16-5g"],
    },
    "P012": {  # Galaxy A15 5G
        "codes": ["SM-A156E"],
        "pages": ["www.samsung.com/in/smartphones/galaxy-a15-5g"],
    },
    "P013": {  # Galaxy A06
        "codes": ["SM-A065F"],
        "pages": ["www.samsung.com/in/smartphones/galaxy-a06"],
    },
    "P014": {  # Galaxy M55 5G
        "codes": ["SM-M556B"],
        "pages": ["www.samsung.com/in/smartphones/galaxy-m55-5g"],
    },
    "P015": {  # Galaxy M15 5G
        "codes": ["SM-M156B"],
        "pages": ["www.samsung.com/in/smartphones/galaxy-m15-5g"],
    },
    "P016": {  # Galaxy S23 FE
        "codes": ["SM-S711B"],
        "pages": ["www.samsung.com/in/smartphones/galaxy-s23-fe"],
    },
    "P017": {  # Galaxy S23
        "codes": ["SM-S911B"],
        "pages": ["www.samsung.com/in/smartphones/galaxy-s23-5g"],
    },
}

CDX_API = "https://web.archive.org/cdx/search/cdx"

WAYBACK_FETCH_TEMPLATE = "https://web.archive.org/web/{timestamp}/{url}"

MODEL_CODE_PATTERN = re.compile(
    r"\b(?:SM-[A-Z0-9]{8,}|NP[A-Z0-9]{7,}|XE[A-Z0-9]{6,}|EI-[A-Z0-9]{6,}|EP-[A-Z0-9]{6,}|EB-[A-Z0-9]{6,})\b"
)


def cdx_search(prefix: str, limit: int = 25):
    """Return [(timestamp, original_url)] for archived 200 pages
    whose URL starts with the given prefix (newest last)."""

    params = {
        "url": prefix if prefix.endswith("*") else prefix + "*",
        "output": "json",
        "limit": limit,
        "collapse": "urlkey",
        "filter": "statuscode:200",
    }

    try:

        response = requests.get(
            CDX_API,
            params=params,
            headers=HEADERS,
            timeout=TIMEOUT_SECONDS,
        )

        if response.status_code != 200:
            return []

        rows = response.json()

        if len(rows) < 2:
            return []

        return [
            (row[1], row[2])
            for row in rows[1:]
            if len(row) >= 3
        ]

    except Exception:
        return []


def wayback_fetch(timestamp: str, url: str):
    """Fetch an archived page with retries (Wayback rate-limits).
    Returns response or None."""

    target = WAYBACK_FETCH_TEMPLATE.format(
        timestamp=timestamp + "id_",
        url=url,
    )

    for attempt in range(4):

        try:

            response = requests.get(
                target,
                headers=HEADERS,
                timeout=45,
            )

            if (
                response.status_code == 200
                and len(response.text) > 500
            ):

                return response

        except Exception:
            pass

        time.sleep(5 * (attempt + 1))

    return None


def fetch_wayback_docs() -> None:

    if not CATALOG_FILE.exists():
        print("catalog.json not found")
        return

    products = json.loads(
        CATALOG_FILE.read_text(encoding="utf-8")
    )

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    fetched = 0
    skipped = 0
    failed = []

    for product in products:

        product_id = str(product.get("id", ""))

        name = product.get("name", product_id)

        if product_id not in WAYBACK_PRODUCTS:
            skipped += 1
            continue

        out_file = DOCS_DIR / f"{product_id}.txt"

        if out_file.exists() and out_file.stat().st_size > 0:

            skipped += 1
            continue

        entry = WAYBACK_PRODUCTS[product_id]

        print(f"[{product_id}] {name}")

        snapshot = None

        # 1) Try the support page by each candidate model code.
        for code in entry["codes"]:

            hits = cdx_search(
                f"www.samsung.com/in/support/model/{code}",
                limit=10,
            )

            time.sleep(0.8)

            if hits:

                snapshot = hits[-1]
                break

        # 2) Fall back to an archived product page to recover a
        # full model code, then re-try the support page.
        if not snapshot:

            for prefix in entry["pages"]:

                hits = cdx_search(prefix, limit=25)

                time.sleep(0.8)

                if not hits:
                    continue

                ts, url = hits[-1]

                response = wayback_fetch(ts, url)

                time.sleep(0.8)

                if response is None:
                    continue

                codes = set(
                    MODEL_CODE_PATTERN.findall(response.text)
                )

                matching = [
                    code
                    for code in codes
                    if any(
                        code.startswith(base)
                        for base in entry["codes"]
                    )
                ]

                for code in sorted(matching):

                    support_hits = cdx_search(
                        f"www.samsung.com/in/support/model/{code}",
                        limit=10,
                    )

                    time.sleep(0.8)

                    if support_hits:

                        snapshot = support_hits[-1]
                        break

                if snapshot:
                    break

        if not snapshot:

            failed.append(
                (product_id, name, "no archived support page")
            )
            continue

        ts, support_url = snapshot

        response = wayback_fetch(ts, support_url)

        time.sleep(0.8)

        if response is None:

            failed.append(
                (product_id, name, "archive fetch failed")
            )
            continue

        content = extract_text(response.text)

        if len(content) < MIN_TEXT_LENGTH:

            failed.append(
                (
                    product_id,
                    name,
                    "content too short",
                )
            )
            continue

        out_file.write_text(content, encoding="utf-8")

        fetched += 1

        print(
            f"   saved {len(content)} chars "
            f"(snapshot {ts})"
        )

    print()
    print(f"Wayback fetched: {fetched}")
    print(f"Skipped (cached / not targeted): {skipped}")
    print(f"Failed: {len(failed)}")

    for product_id, name, reason in failed:
        print(f"  - {product_id} {name}: {reason}")


def main() -> None:

    if "--wayback" in sys.argv:

        fetch_wayback_docs()
        return

    fetch_live_docs()


def extract_text(html: str) -> str:
    """Best-effort extraction of readable content from a page."""

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
            "nav",
            "footer",
            "header",
            "aside",
            "iframe",
            "form",
        ]
    ):
        tag.decompose()

    main = soup.find("main") or soup.body or soup

    lines = []

    for tag in main.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]
    ):

        text = tag.get_text(" ", strip=True)

        text = re.sub(r"\s+", " ", text)

        if len(text) >= 20:
            lines.append(text)

    # Deduplicate while preserving order.
    seen = set()
    unique = []

    for line in lines:

        key = line[:80]

        if key in seen:
            continue

        seen.add(key)
        unique.append(line)

    return "\n".join(unique)


def fetch_live_doc_fallback(
    product_id: str,
    name: str,
    out_file: Path,
    failed: list,
) -> None:
    """Try the official Samsung specs/product page when the per-model
    support page fails. On success the last failure entry is removed
    so the run summary reflects the recovered doc."""

    specs_url = SPECS_PAGE_MAP.get(product_id)

    if not specs_url:
        return

    print(f"   fallback: {specs_url}")

    try:

        response = requests.get(
            specs_url,
            headers=HEADERS,
            timeout=TIMEOUT_SECONDS,
        )

        if response.status_code != 200:
            return

        content = extract_text(response.text)

        if len(content) < MIN_TEXT_LENGTH:
            return

        out_file.write_text(content, encoding="utf-8")

        if failed:
            failed.pop()

        print(f"   fallback saved {len(content)} chars")

    except Exception as error:

        print(f"   fallback failed: {str(error)[:80]}")


def fetch_live_docs() -> None:

    if not CATALOG_FILE.exists():
        print("catalog.json not found")
        return

    products = json.loads(
        CATALOG_FILE.read_text(encoding="utf-8")
    )

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    fetched = 0
    skipped = 0
    failed = []

    for product in products:

        product_id = str(product.get("id", ""))

        name = product.get("name", product_id)

        code = SUPPORT_CODE_MAP.get(product_id, "")

        if not code:

            skipped += 1
            continue

        url = SUPPORT_URL_TEMPLATE.format(code=code)

        out_file = DOCS_DIR / f"{product_id}.txt"

        if out_file.exists() and out_file.stat().st_size > 0:

            skipped += 1
            continue

        if not url:

            failed.append((product_id, name, "no URL"))
            continue

        print(f"[{product_id}] {name}")

        try:

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT_SECONDS,
            )

            if response.status_code != 200:

                failed.append(
                    (
                        product_id,
                        name,
                        f"HTTP {response.status_code}",
                    )
                )

                fetch_live_doc_fallback(
                    product_id,
                    name,
                    out_file,
                    failed,
                )
                continue

            content = extract_text(response.text)

            if len(content) < MIN_TEXT_LENGTH:

                failed.append(
                    (
                        product_id,
                        name,
                        "content too short",
                    )
                )

                fetch_live_doc_fallback(
                    product_id,
                    name,
                    out_file,
                    failed,
                )
                continue

            out_file.write_text(
                content,
                encoding="utf-8",
            )

            fetched += 1

            print(f"   saved {len(content)} chars")

        except Exception as error:

            failed.append(
                (
                    product_id,
                    name,
                    str(error)[:80],
                )
            )

            fetch_live_doc_fallback(
                product_id,
                name,
                out_file,
                failed,
            )

        time.sleep(0.5)

    print()
    print(f"Fetched: {fetched}")
    print(f"Skipped (cached): {skipped}")
    print(f"Failed: {len(failed)}")

    for product_id, name, reason in failed:
        print(f"  - {product_id} {name}: {reason}")


if __name__ == "__main__":
    main()