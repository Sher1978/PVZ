import re
from urllib.parse import unquote, parse_qs, urlparse
import httpx

async def resolve_search_query(query: str) -> str:
    """
    If the search query is a URL (Lazada, Shopee, Tiki, WB, Ozon, Shein),
    extract the real product title or keywords from the page/URL.
    """
    q_clean = query.strip()
    if not (q_clean.startswith("http://") or q_clean.startswith("https://")):
        return q_clean

    try:
        parsed = urlparse(q_clean)
        qs = parse_qs(parsed.query)

        # 1. Check URL parameters for explicit query tags (Lazada / Shopee tracking)
        if "clickTrackInfo" in qs:
            cti = unquote(unquote(qs["clickTrackInfo"][0]))
            match = re.search(r'query:([^;]+)', cti)
            if match:
                extracted = match.group(1).replace("+", " ").strip()
                if extracted and len(extracted) > 2:
                    return extracted

        if "q" in qs and not qs["q"][0].startswith("http"):
            return qs["q"][0]

        # 2. Try HTTP GET to fetch page title or og:title
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        async with httpx.AsyncClient(timeout=4.0, headers=headers, follow_redirects=True) as client:
            res = await client.get(q_clean)
            if res.status_code == 200:
                html = res.text
                og_title = re.search(
                    r'<meta\s+(?:property|name)=["\']og:title["\']\s+content=["\']([^"\'\n]+)["\']',
                    html,
                    re.IGNORECASE,
                )
                if not og_title:
                    og_title = re.search(
                        r'<meta\s+content=["\']([^"\'\n]+)["\']\s+(?:property|name)=["\']og:title["\']',
                        html,
                        re.IGNORECASE,
                    )

                title_text = ""
                if og_title:
                    title_text = og_title.group(1)
                else:
                    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
                    title_text = title_match.group(1) if title_match else ""

                if title_text:
                    clean = re.sub(
                        r'\s*[\|–-]\s*(Lazada|Shopee|Tiki|AliExpress|Wildberries|Ozon|Shein|Buy).*$',
                        '',
                        title_text,
                        flags=re.IGNORECASE,
                    ).strip()
                    if clean and len(clean) > 3:
                        return clean
    except Exception as e:
        print(f"[URL Parser] Extraction fallback: {e}")

    # Fallback to URL path slug clean up
    try:
        path_slug = urlparse(q_clean).path.split("/")[-1]
        path_slug = re.sub(r'\.(html|htm|php|asp)$', '', path_slug, flags=re.IGNORECASE)
        path_slug = re.sub(r'^(pdp|product|item|detail)[-_]?', '', path_slug, flags=re.IGNORECASE)
        path_slug = path_slug.replace("-", " ").replace("_", " ").strip()
        if len(path_slug) > 3 and not path_slug.isdigit():
            return path_slug
    except Exception:
        pass

    return q_clean
