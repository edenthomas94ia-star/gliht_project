import re
from playwright.sync_api import sync_playwright
import os


# ----------------------------
# URL builder
# ----------------------------
def build_kayak_url(origin, destination, departure_date, return_date):
    return (
        f"https://www.kayak.fr/flights/"
        f"{origin}-{destination}/{departure_date}/{return_date}"
        f"?sort=bestflight_a"
    )


# ----------------------------
# Helpers extraction
# ----------------------------
def clean_price(price_text: str):
    if not price_text:
        return None

    cleaned = (
        price_text
        .replace("\u202f", "")
        .replace("\xa0", "")
        .replace("€", "")
        .replace(" ", "")
        .strip()
    )

    match = re.search(r"\d+", cleaned)
    return float(match.group()) if match else None


def extract_times(text: str):
    times = re.findall(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b", text)
    return (
        times[0] if len(times) > 0 else None,
        times[1] if len(times) > 1 else None,
    )


def extract_duration(text: str):
    match = re.search(r"\b\d+h\s?\d{0,2}m?\b", text)
    return match.group(0) if match else None


def extract_stops(text: str):
    lower = text.lower()

    if "direct" in lower:
        return "direct"

    match = re.search(r"(\d+)\s+escale", lower)
    if match:
        return f"{match.group(1)} escale(s)"

    return None


def extract_airline(text: str):
    airlines = [
        "Air France", "easyJet", "Ryanair", "Transavia", "Vueling",
        "Iberia", "Lufthansa", "British Airways", "TAP Air Portugal",
        "KLM", "Swiss", "Austrian", "Brussels Airlines", "Volotea",
        "Binter Canarias", "Canaryfly", "ANA", "Japan Airlines",
        "Qatar Airways", "Emirates", "Etihad", "Turkish Airlines",
        "Air China", "China Eastern", "Finnair"
    ]

    for airline in airlines:
        if airline.lower() in text.lower():
            return airline

    return None


# ----------------------------
# Scraper principal
# ----------------------------
def scrape_page(url):
    with sync_playwright() as p:
        
        HEADLESS = os.getenv("GITHUB_ACTIONS") == "true"

        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context()  # 👈 équivalent incognito
        page = context.new_page()

        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120 Safari/537.36"
            )
        )

        print("Loading page...")
        page.goto(url, timeout=90000)

        cookie_selectors = [
            "button:has-text('Accepter')",
            "button:has-text('Tout accepter')",
            "button:has-text('Refuser')",
        ]

        clicked = False

        for selector in cookie_selectors:
            try:
                btn = page.locator(selector).first
                btn.wait_for(timeout=15000)
                btn.click()
                print(f"Cookie cliqué avec: {selector}")
                clicked = True
                break
            except:
                continue

        if not clicked:
            print("Pas de cookie trouvé")
        page.wait_for_timeout(8000)


        # scroll pour charger + résultats
        for _ in range(4):
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(2000)

        print("Extracting prices...")

        price_elements = page.query_selector_all(".e2GB-price-text")

        print(f"Found {len(price_elements)} price elements")

        results = []
        seen = set()

        for price_el in price_elements:
            try:
                price_text = price_el.inner_text()
                price = clean_price(price_text)

                if price is None:
                    continue

                # remonter au bloc parent du vol
                current = price_el
                block_text = None

                for _ in range(12):
                    current = current.evaluate_handle("el => el.parentElement").as_element()
                    if current is None:
                        break

                    text = current.inner_text()

                    has_time = re.search(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b", text)
                    has_duration = re.search(r"\b\d+h\s?\d{0,2}m?\b", text)
                    has_stop = "direct" in text.lower() or "escale" in text.lower()

                    if has_time and has_duration and has_stop:
                        block_text = text
                        break

                if not block_text:
                    continue

                dep_time, arr_time = extract_times(block_text)
                duration = extract_duration(block_text)
                stops = extract_stops(block_text)
                airline = extract_airline(block_text)

                key = (price, dep_time, arr_time, duration, stops, airline)

                if key in seen:
                    continue

                seen.add(key)

                results.append({
                    "price": price,
                    "currency": "EUR",
                    "departure_time": dep_time,
                    "arrival_time": arr_time,
                    "duration": duration,
                    "stops": stops,
                    "airline": airline,
                    "raw_text": block_text[:400],
                })

            except Exception as e:
                continue

        browser.close()

    return results


# ----------------------------
# Wrapper principal
# ----------------------------
def scrape_kayak(origin, destination, departure_date, return_date):
    url = build_kayak_url(origin, destination, departure_date, return_date)

    results = scrape_page(url)

    return {
        "url": url,
        "count": len(results),
        "min_price": min([r["price"] for r in results]) if results else None,
        "offers": results
    }