import re
from typing import Dict

# Dictionary for translating Russian search intent to Vietnamese/English marketplace search terms
RU_TO_VN_DICT: Dict[str, str] = {
    # Electronics & Tech
    "наушники": "tai nghe",
    "наушник": "tai nghe",
    "беспроводные наушники": "tai nghe bluetooth",
    "ноутбук": "laptop",
    "ноут": "laptop",
    "компьютер": "máy tính",
    "планшет": "máy tính bảng",
    "телефон": "điện thoại",
    "смартфон": "điện thoại thông minh",
    "зарядка": "sạc",
    "зарядное устройство": "củ sạc cable sạc",
    "пауэрбанк": "sạc dự phòng",
    "повербанк": "sạc dự phòng",
    "чехол": "ốp lưng",
    "стекло": "kính cường lực",
    "защитная пленка": "miếng dán màn hình",
    "колонки": "loa",
    "колонка": "loa bluetooth",
    "мышка": "chuột máy tính",
    "мышь": "chuột máy tính",
    "клавиатура": "bàn phím",
    "монитор": "màn hình",
    "часы": "đồng hồ",
    "смарт часы": "đồng hồ thông minh",
    "умные часы": "đồng hồ thông minh",
    "камера": "máy ảnh",
    "микрофон": "micro",

    # Clothing & Shoes
    "платье": "váy đầm",
    "платья": "váy đầm",
    "юбка": "chân váy",
    "футболка": "áo thun t-shirt",
    "майка": "áo ba lỗ",
    "рубашка": "áo sơ mi",
    "худи": "áo hoodie",
    "толстовка": "áo sweater",
    "куртка": "áo khoác",
    "штаны": "quần dài",
    "брюки": "quần tây",
    "джинсы": "quần jean",
    "шорты": "quần short",
    "купальник": "đồ bơi đồ tắm",
    "обувь": "giày",
    "кроссовки": "giày thể thao sneaker",
    "кеды": "giày sneaker",
    "сандалии": "dép sandal",
    "тапочки": "dép lê",
    "сумка": "túi xách",
    "рюкзак": "ba lô backpack",
    "кошелек": "ví da",
    "очки": "kính mát mắt kính",

    # Cosmetics & Personal Care
    "косметика": "mỹ phẩm",
    "крем": "kem dưỡng",
    "крем для лица": "kem dưỡng da mặt",
    "солнцезащитный крем": "kem chống nắng",
    "санскрин": "kem chống nắng",
    "сыворотка": "serum",
    "маска": "mặt nạ",
    "шампунь": "dầu gội",
    "кондиционер": "dầu xả",
    "духи": "nước hoa",
    "парфюм": "nước hoa",
    "помада": "son môi",
    "тушь": "mascara",

    # Home & Goods
    "кофе": "cà phê coffee",
    "чай": "trà tea",
    "кружка": "ly cốc",
    "бутылка": "bình nước",
    "подушка": "gối",
    "одеяло": "chăn mền",
    "постельное белье": "ga giường drap",
    "полотенце": "khăn tắm",
    "вентилятор": "quạt điện",
    "чайник": "ấm siêu tốc",
    "утюг": "bàn ủi",
}

def translate_query_for_marketplaces(query: str) -> str:
    """
    Translates Russian queries or expands English/Vietnamese queries for optimal results
    on Vietnamese marketplaces (Shopee, Lazada, Tiki, Shein, TikTok).
    """
    clean_q = query.strip()
    if not clean_q:
        return clean_q

    # Don't alter if it's already a URL
    if clean_q.startswith("http://") or clean_q.startswith("https://") or ".vn" in clean_q or ".com" in clean_q:
        return clean_q

    lower_q = clean_q.lower()

    # Check for direct phrase matches
    if lower_q in RU_TO_VN_DICT:
        return RU_TO_VN_DICT[lower_q]

    # Replace Russian keywords within composite queries while preserving brand/model names
    words = lower_q.split()
    translated_words = []
    has_ru = False

    for word in words:
        # Strip common Russian punctuation
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word in RU_TO_VN_DICT:
            translated_words.append(RU_TO_VN_DICT[clean_word])
            has_ru = True
        else:
            # Preserve original word (brand name, model number, English/Vietnamese word)
            translated_words.append(word)

    if has_ru:
        return " ".join(translated_words)

    return clean_q
