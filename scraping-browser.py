import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import json

AUTH = "" # lien AUTH
SBR_WS_CDP = "" # URL WebSocket

url = "" #URL ou liste d'URLS

JSON_DATA_FILE = "data.json"


BYPASS_SCRAPING = False

def get_text_if_not_none(e):
    if e:
        return e.text.strip()
    return None

def extract_product_page_infos(html):
    infos = {}

    soup = BeautifulSoup(html, "html.parser")

    infos["title"] = get_text_if_not_none(soup.find("span", id="productTitle"))

    # récupération du prix
    infos["price"] = 0.0
    price_whole = get_text_if_not_none(soup.find("span", class_="price-whole"))
    price_fraction = get_text_if_not_none(soup.find("span", class_="product-fraction"))
    if price_whole and price_whole.isdigit():
        price = float(price_whole)
        if price_fraction and price_fraction.isdigit():
            price += float(price_fraction)/100

        infos["price"] = price

    # récupération de la description
    desc_el = soup.find("div", id="product-description")
    infos["description"] = get_text_if_not_none(desc_el)

    # récupération des avis
    rating_el = soup.find("span", id="customer-review-text")
    if rating_el:
        rating_str = rating_el.text.strip().split()[0]
        infos["rating"] = int(rating_str) if rating_str.isdigit() else 0
    else:
        infos["rating"] = 0

    return infos


async def run(pw):
    all_data = {}

    try:
        with open(JSON_DATA_FILE, "r") as f:
                json_data = f.read()
                all_data = json.loads(json_data)
    except:
        print("json file does not exist")
    
    browser = None
    try:
        if not BYPASS_SCRAPING:
            print('Connecting to Browser API...')
            browser = await pw.chromium.connect_over_cdp(SBR_WS_CDP)
            page = await browser.new_page()
            print('Connected! Navigating to webpage')
            await page.goto(url)
            await page.screenshot(path="page.png", full_page=True)
            print("Screenshot saved as 'page.png'")
            html = await page.content()
            with open("scraping-browser.html", "w", encoding="utf-8") as f:
                f.write(html)
        else:
            with open("scraping-browser.html", "r", encoding="utf-8") as f:
                html = f.read()

        print("Extracting infos...")
        infos = extract_product_page_infos(html)
        print(infos)
        if url not in all_data:
            all_data[url] = {"title": infos["title"], "description": infos["description"]}

    finally:
        if browser:
            await browser.close()
        with open(JSON_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
                


async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == '__main__':
    asyncio.run(main())