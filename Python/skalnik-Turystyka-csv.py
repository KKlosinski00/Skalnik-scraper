import httpx
from selectolax.parser import HTMLParser
import time
from urllib.parse import urljoin
from dataclasses import asdict, dataclass, fields
import csv
from datetime import datetime

@dataclass
class Item: 
    name:   str  | None
    price:  str  | None
    rating: str  | None
    votes:  str  | None
    sizes:  str  | None
    date:   str  | None
    tech:   str  | None


def get_html(url, **kwargs):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"}
    if kwargs.get("page"):  
        resp = httpx.get(url + str(kwargs.get("page")), headers=headers, follow_redirects=True,timeout=30.0)
    else:
        resp = httpx.get(url, headers=headers, follow_redirects=True, timeout=30.0)
    
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}. Page Limit Reached")
            return False
    html = HTMLParser(resp.text)
    return html
    


def parse_search_page(html: HTMLParser):
    products = html.css("div.product-item-details")
    for product in products:
         yield urljoin("",product.css_first("a").attributes["href"])                                # nie ma tu podanego członu przed linkiem, bo w tym przypadku jest podany cały w html


def parse_item_page(html):
    new_item = Item(
         name   = extract_text(html, "span.base"),
         price  = extract_text(html, "span.price-final_price"),
         rating = extract_text(html, "div.rating-result"),
         votes  = extract_text(html, "div.reviews-actions"),
         sizes  = extract_text(html, "div.swatch-opt"),
         tech   = extract_text(html, "div.additional--technologies"),
         date   = datetime.now().date()
    )
    return asdict(new_item)


def extract_text(html, sel):
      try:
            text = html.css_first(sel).text()
            return clean_data(text)
      except AttributeError:
            return None


def append_to_csv(products):
    fieldnames = [field.name for field in fields(Item)]
    with open("Turystyka.csv", "a", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames)
        writer.writerow(products)


def clean_data(value):
    chars_to_remove = ["Cena", "zł","\xa0", "%"]
    for char in chars_to_remove:
        if char in value:
            value = value.replace(char, "")
    return value.strip()


def main():
    products = []
    baseurl = "https://www.skalnik.pl/sprzet-turystyczny/page:"
    for x in range(1,70):
        print(f"Gathering page: {x}")
        html = get_html(baseurl, page=x)
        if html is False:
            break
        product_urls = parse_search_page(html)
        for url in product_urls:
            print(url)
            html = get_html(url)
            append_to_csv(parse_item_page(html))
            time.sleep(0.1)  

if __name__ == "__main__":
  main()
