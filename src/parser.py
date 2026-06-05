import argparse
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://krisha.kz"
START_URL = "https://krisha.kz/prodazha/kvartiry/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def clean_text(text: str | None) -> str | None:
    if not text:
        return None

    return re.sub(
        r"\s+",
        " ",
        text.replace("\xa0", " ")
    ).strip()


def clean_price(price: str | None) -> int | None:
    if not price:
        return None

    digits = re.sub(r"\D", "", price)

    return int(digits) if digits else None


def parse_int(value: str | None) -> int | None:
    if not value:
        return None

    match = re.search(r"\d+", value)

    return int(match.group()) if match else None


def parse_float(value: str | None) -> float | None:
    if not value:
        return None

    value = value.replace(",", ".")
    match = re.search(r"\d+(?:\.\d+)?", value)

    return float(match.group()) if match else None


def extract_ad_id(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def split_city_district(value: str | None) -> tuple[str | None, str | None]:
    if not value:
        return None, None

    parts = [part.strip() for part in value.split(",")]

    city = parts[0] if len(parts) > 0 else None
    district = parts[1] if len(parts) > 1 else None

    return city, district


def parse_title(title: str | None) -> dict:
    result = {
        "rooms": None,
        "area": None,
        "floor": None,
        "total_floors": None,
    }

    if not title:
        return result

    rooms_match = re.search(r"(\d+)-комнат", title)
    area_match = re.search(r"(\d+(?:\.\d+)?)\s*м²", title)
    floor_full_match = re.search(r"(\d+)\/(\d+)\s*этаж", title)
    floor_only_match = re.search(r"·\s*(\d+)\s*этаж", title)

    if rooms_match:
        result["rooms"] = int(rooms_match.group(1))

    if area_match:
        result["area"] = float(area_match.group(1))

    if floor_full_match:
        result["floor"] = int(floor_full_match.group(1))
        result["total_floors"] = int(floor_full_match.group(2))
    elif floor_only_match:
        result["floor"] = int(floor_only_match.group(1))

    return result


def get_location(soup: BeautifulSoup) -> str | None:
    location_tag = soup.find(class_="offer__location")

    if not location_tag:
        return None

    span = location_tag.find("span")

    if span:
        return clean_text(span.get_text(" ", strip=True))

    return clean_text(location_tag.get_text(" ", strip=True))


def parse_short_info(soup: BeautifulSoup) -> dict:
    params = {}

    items = soup.find_all(class_="offer__info-item")

    for item in items:
        title_tag = item.find(class_="offer__info-title")
        value_tag = item.find(class_="offer__advert-short-info")

        if not title_tag or not value_tag:
            continue

        key = clean_text(title_tag.get_text(" ", strip=True))
        value = clean_text(value_tag.get_text(" ", strip=True))

        if key:
            params[key] = value

    return params


def parse_parameters(soup: BeautifulSoup) -> dict:
    params = {}

    block = soup.find(class_="offer__parameters")

    if not block:
        return params

    for dl in block.find_all("dl"):
        dt = dl.find("dt")
        dd = dl.find("dd")

        if not dt or not dd:
            continue

        key = clean_text(dt.get_text(" ", strip=True))
        value = clean_text(dd.get_text(" ", strip=True))

        if key:
            params[key] = value

    return params


def get_description(soup: BeautifulSoup) -> str | None:
    desc_tag = soup.find(class_="a-text")

    if desc_tag:
        return clean_text(desc_tag.get_text(" ", strip=True))

    return None


def get_ad_links(page: int = 1) -> list[str]:
    url = START_URL if page == 1 else f"{START_URL}?page={page}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    links = []

    for link_tag in soup.find_all("a", href=True):
        href = link_tag["href"]

        if "/a/show/" in href:
            links.append(urljoin(BASE_URL, href))

    return list(set(links))


def parse_ad(url: str) -> dict:
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=50
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("h1")
    price_tag = soup.find(class_="offer__price")

    title = clean_text(
        title_tag.get_text(" ", strip=True)
    ) if title_tag else None

    price_raw = clean_text(
        price_tag.get_text(" ", strip=True)
    ) if price_tag else None

    title_features = parse_title(title)

    params = {}
    params.update(parse_short_info(soup))
    params.update(parse_parameters(soup))

    location_raw = get_location(soup)
    city, district = split_city_district(location_raw)

    price = clean_price(price_raw)
    area = title_features["area"]

    price_per_m2 = (
        round(price / area, 2)
        if price and area
        else None
    )

    return {
        "id": extract_ad_id(url),
        "url": url,
        "title": title,
        "price": price,
        "price_raw": price_raw,
        "price_per_m2": price_per_m2,
        "rooms": title_features["rooms"],
        "area": area,
        "floor": title_features["floor"],
        "total_floors": title_features["total_floors"],
        "location_raw": location_raw,
        "city": city,
        "district": district,
        "residential_complex": params.get("Жилой комплекс"),
        "house_type": params.get("Тип дома"),
        "year_built": parse_int(params.get("Год постройки")),
        "condition": params.get("Состояние квартиры"),
        "bathroom": params.get("Санузел"),
        "balcony": params.get("Балкон"),
        "balcony_glazed": params.get("Балкон остеклён"),
        "door": params.get("Дверь"),
        "phone": params.get("Телефон"),
        "internet": params.get("Интернет"),
        "parking": params.get("Парковка"),
        "furniture": params.get("Квартира меблирована"),
        "floor_covering": params.get("Пол"),
        "ceiling_height": parse_float(params.get("Высота потолков")),
        "former_hostel": params.get("Бывшее общежитие"),
        "exchange_possible": params.get("Возможен обмен"),
        "description": get_description(soup),
    }


def safe_parse_ad(url: str, retries: int = 3) -> dict | None:
    for attempt in range(1, retries + 1):
        try:
            return parse_ad(url)

        except requests.exceptions.ReadTimeout:
            print(f"Timeout: {url}. Attempt {attempt}/{retries}")
            time.sleep(3)

        except requests.exceptions.RequestException as error:
            print(f"Request error: {url} — {error}")
            return None

        except Exception as error:
            print(f"Parsing error: {url} — {error}")
            return None

    print(f"Failed to parse: {url}")
    return None


def collect_links(
    start_page: int,
    end_page: int,
    sleep_between_pages: float
) -> list[str]:
    all_links = []

    for page in range(start_page, end_page + 1):
        print(f"Collecting links from page {page}")

        try:
            links = get_ad_links(page)
            print(f"Found links: {len(links)}")
            all_links.extend(links)

        except Exception as error:
            print(f"Failed to collect page {page}: {error}")

        time.sleep(sleep_between_pages)

    unique_links = list(set(all_links))

    print(f"Total unique links: {len(unique_links)}")

    return unique_links


def collect_ads(
    start_page: int,
    end_page: int,
    output_path: str,
    checkpoint_path: str | None = None,
    sleep_between_pages: float = 2,
    sleep_between_ads: float = 1,
    save_every: int = 50,
) -> pd.DataFrame:
    links = collect_links(
        start_page=start_page,
        end_page=end_page,
        sleep_between_pages=sleep_between_pages,
    )

    all_data = []

    for index, url in enumerate(links, start=1):
        print(f"{index}/{len(links)} -> {url}")

        item = safe_parse_ad(url)

        if item:
            all_data.append(item)

        if checkpoint_path and index % save_every == 0:
            checkpoint_df = pd.DataFrame(all_data)
            checkpoint_df.to_csv(
                checkpoint_path,
                index=False,
                encoding="utf-8-sig",
            )

        time.sleep(sleep_between_ads)

    df = pd.DataFrame(all_data)

    if not df.empty:
        df = df.drop_duplicates(subset="id")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse apartment listings from Krisha.kz"
    )

    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="First page to parse",
    )

    parser.add_argument(
        "--end-page",
        type=int,
        default=5,
        help="Last page to parse",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="data/raw/krisha_ads_raw.csv",
        help="Output CSV path",
    )

    parser.add_argument(
        "--checkpoint",
        type=str,
        default="data/raw/krisha_ads_checkpoint.csv",
        help="Checkpoint CSV path",
    )

    parser.add_argument(
        "--sleep-pages",
        type=float,
        default=2,
        help="Sleep time between listing pages",
    )

    parser.add_argument(
        "--sleep-ads",
        type=float,
        default=1,
        help="Sleep time between ad pages",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    collect_ads(
        start_page=args.start_page,
        end_page=args.end_page,
        output_path=args.output,
        checkpoint_path=args.checkpoint,
        sleep_between_pages=args.sleep_pages,
        sleep_between_ads=args.sleep_ads,
    )