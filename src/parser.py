import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://krisha.kz"
START_URL = "https://krisha.kz/prodazha/kvartiry/"

headers = {
    "User-Agent": "Mozilla/5.0"
}


def clean_text(text):
    if not text:
        return None
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def clean_price(price):
    if not price:
        return None

    digits = re.sub(r"\D", "", price)
    return int(digits) if digits else None


def parse_int(value):
    if not value:
        return None

    match = re.search(r"\d+", value)
    return int(match.group()) if match else None


def parse_float(value):
    if not value:
        return None

    value = value.replace(",", ".")
    match = re.search(r"\d+(?:\.\d+)?", value)
    return float(match.group()) if match else None


def extract_ad_id(url):
    return url.rstrip("/").split("/")[-1]


def split_city_district(value):
    if not value:
        return None, None

    parts = [x.strip() for x in value.split(",")]

    city = parts[0] if len(parts) > 0 else None
    district = parts[1] if len(parts) > 1 else None

    return city, district


def parse_title(title):
    if not title:
        return {
            "rooms": None,
            "area": None,
            "floor": None,
            "total_floors": None,
        }

    rooms = None
    area = None
    floor = None
    total_floors = None

    rooms_match = re.search(r"(\d+)-комнат", title)
    area_match = re.search(r"(\d+(?:\.\d+)?)\s*м²", title)

    floor_full_match = re.search(r"(\d+)\/(\d+)\s*этаж", title)
    floor_only_match = re.search(r"·\s*(\d+)\s*этаж", title)

    if rooms_match:
        rooms = int(rooms_match.group(1))

    if area_match:
        area = float(area_match.group(1))

    if floor_full_match:
        floor = int(floor_full_match.group(1))
        total_floors = int(floor_full_match.group(2))
    elif floor_only_match:
        floor = int(floor_only_match.group(1))

    return {
        "rooms": rooms,
        "area": area,
        "floor": floor,
        "total_floors": total_floors,
    }


def get_location(soup):
    location_tag = soup.find(class_="offer__location")

    if not location_tag:
        return None

    span = location_tag.find("span")

    if span:
        return clean_text(span.get_text(" ", strip=True))

    return clean_text(location_tag.get_text(" ", strip=True))


def parse_short_info(soup):
    """
    Парсит блоки:
    offer__info-item + offer__advert-short-info

    Например:
    Город, Тип дома, Жилой комплекс, Год постройки, Состояние квартиры
    """
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


def parse_parameters(soup):
    """
    Парсит блок:
    offer__parameters

    Например:
    Санузел, Балкон, Интернет, Парковка, Пол, Высота потолков
    """
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


def get_description(soup):
    desc_tag = soup.find(class_="a-text")

    if desc_tag:
        return clean_text(desc_tag.get_text(" ", strip=True))

    return None


def get_ad_links(page=1):
    url = START_URL if page == 1 else f"{START_URL}?page={page}"

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/a/show/" in href:
            links.append(urljoin(BASE_URL, href))

    return list(set(links))


def parse_ad(url):
    response = requests.get(url, headers=headers, timeout=50)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("h1")
    price_tag = soup.find(class_="offer__price")

    title = clean_text(title_tag.get_text(" ", strip=True)) if title_tag else None
    price_raw = clean_text(price_tag.get_text(" ", strip=True)) if price_tag else None

    title_features = parse_title(title)

    short_params = parse_short_info(soup)
    detail_params = parse_parameters(soup)

    params = {}
    params.update(short_params)
    params.update(detail_params)

    location_raw = get_location(soup)
    city, district = split_city_district(location_raw)

    price = clean_price(price_raw)
    area = title_features.get("area")
    price_per_m2 = round(price / area, 2) if price and area else None

    return {
        "id": extract_ad_id(url),
        "url": url,
        "title": title,

        "price": price,
        "price_raw": price_raw,
        "price_per_m2": price_per_m2,

        "rooms": title_features.get("rooms"),
        "area": area,
        "floor": title_features.get("floor"),
        "total_floors": title_features.get("total_floors"),

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


def safe_parse_ad(url, retries=3):
    for attempt in range(retries):
        try:
            return parse_ad(url)

        except requests.exceptions.ReadTimeout:
            print(f"Таймаут: {url}. Попытка {attempt + 1}/{retries}")
            time.sleep(3)

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {url} — {e}")
            return None

        except Exception as e:
            print(f"Ошибка парсинга: {url} — {e}")
            return None

    print(f"Не удалось спарсить: {url}")
    return None


def collect_ads(pages=1, sleep_between_pages=2, sleep_between_ads=1):
    all_links = []

    for page in range(1, pages + 1):
        print(f"Собираю ссылки со страницы {page}")

        links = get_ad_links(page)
        print(f"Найдено ссылок: {len(links)}")

        all_links.extend(links)
        time.sleep(sleep_between_pages)

    all_links = list(set(all_links))
    print(f"Всего уникальных ссылок: {len(all_links)}")

    all_data = []

    for i, url in enumerate(all_links, start=1):
        print(f"{i}/{len(all_links)} — {url}")

        item = safe_parse_ad(url)

        if item:
            all_data.append(item)

        time.sleep(sleep_between_ads)

    df = pd.DataFrame(all_data)

    if not df.empty:
        df = df.drop_duplicates(subset="id")

    return df

data = parse_ad("https://krisha.kz/a/show/1012340227")

all_links = []

for page in range(801, 1000):
    print(f"Страница {page}")

    try:
        links = get_ad_links(page=page)
        print(f"Найдено {len(links)} ссылок")
        all_links.extend(links)

    except Exception as e:
        print(f"Ошибка на странице {page}: {e}")

    time.sleep(2)

all_links = list(set(all_links))
print(f"Всего ссылок: {len(all_links)}")

all_data = []

for i, url in enumerate(all_links, start=1):
    print(f"{i}/{len(all_links)} -> {url}")

    item = safe_parse_ad(url)

    if item:
        all_data.append(item)

    # промежуточное сохранение каждые 50 объявлений
    if i % 50 == 0:
        pd.DataFrame(all_data).to_csv(
            "krisha_ads_part.csv",
            index=False,
            encoding="utf-8-sig"
        )

    time.sleep(1)

df = pd.DataFrame(all_data)
df = df.drop_duplicates(subset="id")

df.to_csv("krisha_ads_3.csv", index=False, encoding="utf-8-sig")