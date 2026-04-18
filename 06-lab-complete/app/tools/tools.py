import json
import requests


def search_google(query: str) -> str:
    """Tìm kiếm thông tin, giá, đánh giá laptop qua DuckDuckGo."""
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_redirect": 1, "kl": "vn-vi"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        if data.get("AbstractText"):
            results.append({
                "title":   data.get("Heading"),
                "snippet": data.get("AbstractText"),
                "link":    data.get("AbstractURL"),
            })

        for item in data.get("RelatedTopics", [])[:3]:
            if "Text" in item:
                results.append({
                    "title":   item.get("Text", "")[:60],
                    "snippet": item.get("Text"),
                    "link":    item.get("FirstURL"),
                })

        return json.dumps(results or [{"snippet": f"Kết quả tìm kiếm cho: {query}..."}], ensure_ascii=False)
    except Exception as e:
        return json.dumps([{"snippet": f"Kết quả tìm kiếm cho: {query}... (Lỗi: {str(e)})"}], ensure_ascii=False)


def get_user_location(args: str = None) -> str:
    """Lấy vị trí hiện tại của người dùng. Mặc định là Quận 1, TP. Hồ Chí Minh."""
    return "Quận 1, TP. Hồ Chí Minh"


def search_laptop_shop(location: str) -> str:
    """Tìm các cửa hàng laptop tại một địa điểm cụ thể."""
    return f"Các shop tại {location}: Phong Vũ, FPT Shop, CellphoneS."


def check_stock(item_name: str) -> str:
    """Kiểm tra số lượng tồn kho của sản phẩm laptop."""
    stock_db = {
        "macbook air m1": 15,
        "macbook air m2": 8,
        "dell xps 13": 5,
        "hp envy 13": 0,
        "asus zenbook": 12
    }
    item_lower = item_name.lower()
    for key, value in stock_db.items():
        if key in item_lower:
            return json.dumps({"item": key, "stock": value})
    
    return json.dumps({"item": item_name, "stock": "Liên hệ shop để biết chi tiết"})


def check_price(item_name: str) -> str:
    """Kiểm tra giá bán của sản phẩm laptop."""
    price_db = {
        "macbook air m1": "18.500.000 VNĐ",
        "macbook air m2": "24.990.000 VNĐ",
        "dell xps 13": "32.000.000 VNĐ",
        "hp envy 13": "21.500.000 VNĐ",
        "asus zenbook": "19.990.000 VNĐ"
    }
    item_lower = item_name.lower()
    for key, value in price_db.items():
        if key in item_lower:
            return json.dumps({"item": key, "price": value})
    
    return json.dumps({"item": item_name, "price": "Giá thay đổi theo cấu hình, vui lòng liên hệ"})


# ── Tool registry ────────────────────────────────────────────────
LAPTOP_TOOLS_CONFIG = [
    {
        "name":        "SearchGoogle",
        "description": "Tìm kiếm thông tin, giá, đánh giá laptop. Input: chuỗi tìm kiếm.",
        "function":    search_google,
    },
    {
        "name":        "GetUserLocation",
        "description": "Lấy vị trí hiện tại của người dùng. Input: không cần thiết.",
        "function":    get_user_location,
    },
    {
        "name":        "SearchLaptopShop",
        "description": "Tìm cửa hàng laptop tại khu vực. Input: địa điểm (location).",
        "function":    search_laptop_shop,
    },
    {
        "name":        "CheckStock",
        "description": "Kiểm tra tồn kho của laptop. Input: tên laptop.",
        "function":    check_stock,
    },
    {
        "name":        "CheckPrice",
        "description": "Kiểm tra giá bán laptop. Input: tên laptop.",
        "function":    check_price,
    },
]
