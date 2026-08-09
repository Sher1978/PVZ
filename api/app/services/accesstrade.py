"""
ACCESSTRADE Vietnam Affiliate Link Service
Generates tracked CPS affiliate links for approved campaigns.
API Docs: https://api.accesstrade.vn/
"""
import httpx
from typing import Optional
from app.config import settings

# Campaign IDs on ACCESSTRADE Vietnam (set after approval)
CAMPAIGN_IDS = {
    "lazada": settings.ACCESSTRADE_LAZADA_CAMPAIGN_ID or "5087153089503673507",
    "shopee": settings.ACCESSTRADE_SHOPEE_CAMPAIGN_ID or "4751584435713464237",
    "tiki":   settings.ACCESSTRADE_TIKI_CAMPAIGN_ID or "4348614231480407268",
    "kiki":   settings.ACCESSTRADE_KIKI_CAMPAIGN_ID or "",
    "tiktok": settings.ACCESSTRADE_TIKTOK_CAMPAIGN_ID or "748",
}

ACCESSTRADE_API_URL = "https://api.accesstrade.vn/v1/product_link/create"


async def generate_affiliate_link(
    platform: str,
    product_url: str,
    sub1: Optional[str] = None,
) -> str:
    """
    Wrap a product URL into an ACCESSTRADE tracked affiliate deeplink.
    Falls back to original URL if token not configured or API fails.

    Args:
        platform:    One of "lazada", "shopee", "kiki"
        product_url: The original product page URL
        sub1:        Optional tracking label (e.g. user_id or master_id)

    Returns:
        Affiliate URL string (or original URL on failure).
    """
    token = settings.ACCESSTRADE_TOKEN
    campaign_id = CAMPAIGN_IDS.get(platform, "")

    if not token or not campaign_id:
        # No credentials yet — return original URL so the app still works
        return product_url

    payload = {
        "campaign_id": campaign_id,
        "urls": [product_url],
        "url_enc": True,
    }
    if sub1:
        payload["sub1"] = sub1[:50]  # ACCESSTRADE limits sub params

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"token {token}",
    }

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.post(ACCESSTRADE_API_URL, json=payload, headers=headers)
            if res.status_code == 200:
                data = res.json()
                # Response: {"data": [{"url": "https://..."}, ...]}
                links = data.get("data", [])
                if links and isinstance(links, list):
                    return links[0].get("url", product_url)
    except Exception as e:
        print(f"[ACCESSTRADE] link generation failed for {platform}: {e}")

    return product_url


def build_lazada_search_url(query: str) -> str:
    """Direct Lazada VN search URL (no auth needed)."""
    from urllib.parse import quote_plus
    return f"https://www.lazada.vn/catalog/?q={quote_plus(query)}&sort=popularity"


def build_shopee_search_url(query: str) -> str:
    """Direct Shopee VN search URL."""
    from urllib.parse import quote_plus
    return f"https://shopee.vn/search?keyword={quote_plus(query)}"


def build_kiki_search_url(query: str) -> str:
    """Kiki Fashion VN search URL."""
    from urllib.parse import quote_plus
    return f"https://www.kikifashion.com/search?q={quote_plus(query)}"
