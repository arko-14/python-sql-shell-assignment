#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import dataclass, asdict
from typing import Optional, Iterable
from urllib.parse import urljoin, urlencode

import requests
from bs4 import BeautifulSoup


BASE = "https://mdcomputers.in/"


@dataclass
class Product:
    name: str
    url: str
    price_current: Optional[str] = None
    price_old: Optional[str] = None


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": BASE,
    })
    return s


def search_url(term: str, page: Optional[int] = None) -> str:
    params = {"route": "product/search", "search": term}
    if page is not None:
        params["page"] = str(page)
    return urljoin(BASE, "?" + urlencode(params))


def parse_price(text: str) -> tuple[Optional[str], Optional[str]]:
    """
    Extract rupee prices from a chunk of text.
    Returns (current, old) best-effort.
    """
    amounts = re.findall(r"₹\s*([\d,]+)", text)
    if not amounts:
        return None, None
    if len(amounts) == 1:
        return amounts[0], None
    return amounts[-1], amounts[0]


def _to_int_price(p: Optional[str]) -> Optional[int]:
    if not p:
        return None
    try:
        return int(p.replace(",", "").strip())
    except Exception:
        return None


def normalize_prices(cur: Optional[str], old: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """
    If both prices exist and old < current, swap them.
    This fixes cases where parsing order is reversed.
    """
    cur_i = _to_int_price(cur)
    old_i = _to_int_price(old)
    if cur_i is not None and old_i is not None and old_i < cur_i:
        return old, cur
    return cur, old


def parse_products(html: str, page_url: str) -> list[Product]:
    soup = BeautifulSoup(html, "html.parser")
    products: list[Product] = []

    cards = soup.select("div.product-thumb")
    if not cards:
        cards = soup.select("div.product-layout")

    for card in cards:
        a = card.select_one(
            ".caption h4 a, .caption h3 a, h4 a, h3 a, "
            "a[href*='/product/'], a[href*='route=product/product']"
        )
        if not a:
            continue

        name = a.get_text(strip=True)
        href = a.get("href")
        if not name or not href:
            continue

        products.append(Product(
            name=name,
            url=urljoin(page_url, href),
            price_current=None,
            price_old=None
        ))

    if not products:
        for a in soup.select("a[href*='/product/'], a[href*='route=product/product']"):
            name = a.get_text(strip=True)
            href = a.get("href")
            if not name or not href:
                continue
            if len(name) < 8:
                continue
            products.append(Product(
                name=name,
                url=urljoin(page_url, href),
                price_current=None,
                price_old=None
            ))

    uniq = {p.url: p for p in products}
    return list(uniq.values())


def find_next_page(html: str, page_url: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")

    pag = soup.select_one("ul.pagination")
    if pag:
        for a in pag.select("a"):
            if a.get_text(strip=True) == ">":
                href = a.get("href")
                if href:
                    return urljoin(page_url, href)

    for a in soup.find_all("a"):
        if a.get_text(strip=True) == ">":
            href = a.get("href")
            if href:
                return urljoin(page_url, href)

    return None


def fetch_product_price(session: requests.Session, product_url: str, debug: bool = False) -> tuple[Optional[str], Optional[str]]:
    """
    Fetch a product detail page and extract price.
    Tries:
      1) .price-new / .price-old
      2) visible price blocks
      3) JSON-LD (schema.org Offer)
      4) meta property=product:price:amount / itemprop=price
    """
    r = session.get(product_url, timeout=30)
    r.raise_for_status()
    html = r.text
    soup = BeautifulSoup(html, "html.parser")

    # 1) Common OpenCart patterns
    new_el = soup.select_one(".price-new")
    old_el = soup.select_one(".price-old")
    if new_el:
        cur_txt = new_el.get_text(" ", strip=True)
        cur, _ = parse_price(cur_txt if "₹" in cur_txt else f"₹{cur_txt}")

        old = None
        if old_el:
            old_txt = old_el.get_text(" ", strip=True)
            _, old = parse_price(old_txt if "₹" in old_txt else f"₹{old_txt}")

        cur, old = normalize_prices(cur, old)
        return cur, old

    # 2) Visible blocks that might contain rupee symbol
    for el in soup.select(".price, p.price, .product-price, .list-unstyled, .price-box, .product-info"):
        txt = el.get_text(" ", strip=True)
        cur, old = parse_price(txt)
        if cur:
            cur, old = normalize_prices(cur, old)
            return cur, old

    # 3) JSON-LD (schema.org) often contains offers.price
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string or "")
        except Exception:
            continue

        nodes = data if isinstance(data, list) else [data]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            offers = node.get("offers")
            if isinstance(offers, dict) and offers.get("price"):
                return str(offers["price"]).strip(), None
            if isinstance(offers, list):
                for off in offers:
                    if isinstance(off, dict) and off.get("price"):
                        return str(off["price"]).strip(), None

    # 4) Meta tags / itemprop
    meta_price = soup.select_one('meta[property="product:price:amount"]')
    if meta_price and meta_price.get("content"):
        return meta_price["content"].strip(), None

    itemprop_price = soup.select_one('[itemprop="price"]')
    if itemprop_price:
        if itemprop_price.get("content"):
            return itemprop_price["content"].strip(), None
        txt = itemprop_price.get_text(" ", strip=True)
        cur, old = parse_price(txt)
        if cur:
            cur, old = normalize_prices(cur, old)
            return cur, old

    if debug:
        title = soup.title.get_text(strip=True) if soup.title else "NO TITLE"
        print(f"[DEBUG] Price not found on product page: {product_url} (title={title})", file=sys.stderr)

    return None, None


def scrape_all(term: str, sleep_s: float, debug: bool) -> Iterable[Product]:
    s = make_session()
    url = search_url(term)
    seen_pages = set()
    seen_products = set()

    while url and url not in seen_pages:
        seen_pages.add(url)

        r = s.get(url, timeout=30)
        if debug:
            print(f"[DEBUG] GET {url} -> {r.status_code}, bytes={len(r.content)}", file=sys.stderr)

        r.raise_for_status()
        html = r.text

        products = parse_products(html, url)

        if debug and not products:
            with open("debug_mdcomputers.html", "w", encoding="utf-8") as f:
                f.write(html)
            title = BeautifulSoup(html, "html.parser").title
            print("[DEBUG] No products parsed. Saved HTML to debug_mdcomputers.html", file=sys.stderr)
            print(f"[DEBUG] Page <title>: {title.get_text(strip=True) if title else 'NONE'}", file=sys.stderr)

        for p in products:
            if p.url in seen_products:
                continue
            seen_products.add(p.url)

            cur, old = fetch_product_price(s, p.url, debug=debug)
            p.price_current, p.price_old = normalize_prices(cur, old)
            yield p

            time.sleep(0.1)  # polite throttle

        url = find_next_page(html, url)
        if url:
            time.sleep(sleep_s)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("term", help='Search term, e.g. "external harddrive"')
    ap.add_argument("--format", choices=["jsonl", "json", "csv"], default="jsonl")
    ap.add_argument("--sleep", type=float, default=0.2)
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    items = list(scrape_all(args.term, args.sleep, args.debug))

    if args.format == "json":
        json.dump([asdict(x) for x in items], sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    elif args.format == "csv":
        w = csv.DictWriter(sys.stdout, fieldnames=["name", "url", "price_current", "price_old"])
        w.writeheader()
        for x in items:
            w.writerow(asdict(x))
    else:
        for x in items:
            sys.stdout.write(json.dumps(asdict(x), ensure_ascii=False) + "\n")

    if not items:
        print("[WARN] 0 products found. Try --debug to inspect debug_mdcomputers.html", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
