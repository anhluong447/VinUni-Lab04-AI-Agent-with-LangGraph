from langchain_core.tools import tool

# =====================================================================
# MOCK DATA – Dữ liệu giả lập hệ thống du lịch
# =====================================================================

FLIGHTS_DB = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1_450_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2_800_000, "class": "business"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1_200_000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "10:00", "arrival": "12:15", "price": 1_350_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1_100_000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1_600_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "07:30", "arrival": "09:40", "price": 950_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "12:00", "arrival": "14:10", "price": 1_300_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3_200_000, "class": "business"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1_300_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780_000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "15:00", "arrival": "16:00", "price": 650_000, "class": "economy"},
    ],
}

HOTELS_DB = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1_800_000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1_200_000, "area": "Mỹ Khê", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650_000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250_000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350_000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3_500_000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Meliá", "stars": 4, "price_per_night": 1_500_000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800_000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200_000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2_800_000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1_400_000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550_000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room", "stars": 2, "price_per_night": 180_000, "area": "Quận 1", "rating": 4.6},
    ],
}

# --- IMPLEMENTATION ---

@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố, ngay trong ngày hôm nay, không hỏi lại.
    Tham số:
    - origin: thành phố khởi hành (VD: 'Hà Nội', 'Hồ Chí Minh')
    - destination: thành phố đến (VD: 'Đà Nẵng', 'Phú Quốc')
    Trả về danh sách chuyến bay với hãng, giờ bay, giá vé.
    Nếu không tìm thấy tuyến bay, trả về thông báo không có chuyến.
    """
    flights = FLIGHTS_DB.get((origin, destination))
    
    if not flights:
        flights = FLIGHTS_DB.get((destination, origin))
        if not flights:
            return f"Không tìm thấy chuyến bay từ {origin} đến {destination}."

    result = f"Danh sách chuyến bay từ {origin} đến {destination}:\n"
    for f in flights:
        price_fmt = "{:,.0f}đ".format(f['price']).replace(",", ".")
        result += f"- {f['airline']}: {f['departure']} -> {f['arrival']} | Giá: {price_fmt} ({f['class']})\n"
    
    return result

@tool
def search_hotels(city: str, max_price_per_night: int = 99999999) -> str:
    """
    Tìm kiếm khách sạn tại một thành phố, có thể lọc theo giá tối đa mỗi đêm.
    Tham số:
    - city: tên thành phố (VD: 'Đà Nẵng', 'Phú Quốc', 'Hồ Chí Minh')
    - max_price_per_night: giá tối đa mỗi đêm (VNĐ), mặc định không giới hạn
    Trả về danh sách khách sạn phù hợp với tên, số sao, giá, khu vực, rating.
    """
    try:
        # Ép kiểu an toàn đề phòng LLM truyền nhầm string
        max_price = int(max_price_per_night)
        
        hotels = HOTELS_DB.get(city, [])
        
        # Lọc theo giá và sắp xếp theo rating giảm dần
        filtered_hotels = [h for h in hotels if h['price_per_night'] <= max_price]
        filtered_hotels.sort(key=lambda x: x['rating'], reverse=True)

        if not filtered_hotels:
            return f"Không tìm thấy khách sạn tại {city} với giá dưới {'{:,.0f}đ'.format(max_price).replace(',', '.')} / đêm. Hãy thử tăng ngân sách."

        result = f"Khách sạn tại {city} phù hợp với yêu cầu:\n"
        for h in filtered_hotels:
            p_fmt = "{:,.0f}đ".format(h['price_per_night']).replace(",", ".")
            result += f"- {h['name']} ({h['stars']} sao): {p_fmt}/đêm | Khu vực: {h['area']} | Rating: {h['rating']}\n"
        
        return result
    except ValueError:
        return "Lỗi: Tham số max_price_per_night phải là một số nguyên (ví dụ: 1500000)."
    except Exception as e:
        return f"Lỗi không xác định khi tìm khách sạn: {str(e)}"

@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """
    Tính toán ngân sách còn lại sau khi trừ các khoản chi phí.
    Tham số:
    - total_budget: tổng ngân sách ban đầu (VNĐ)
    - expenses: chuỗi mô tả các khoản chi, mỗi khoản cách nhau bởi dấu phẩy, định dạng 'tên_khoản:số_tiền'
    Trả về bảng chi tiết các khoản chi và số tiền còn lại.
    Nếu vượt ngân sách, cảnh báo rõ ràng số tiền thiếu.
    """
    try:
        # Đảm bảo total_budget là số nguyên
        total_budget = int(total_budget)
        
        expense_dict = {}
        total_expense = 0
        
        # Parse chuỗi expenses
        items = expenses.split(",")
        for item in items:
            name, amount = item.split(":")
            amount = int(amount.strip())
            expense_dict[name.strip()] = amount
            total_expense += amount
        
        remaining = total_budget - total_expense
        
        # Format bảng kết quả
        res = "Bảng chi phí:\n"
        for name, amount in expense_dict.items():
            res += f"- {name}: {'{:,.0f}đ'.format(amount).replace(',', '.')}\n"
        
        res += "---\n"
        res += f"Tổng chi: {'{:,.0f}đ'.format(total_expense).replace(',', '.')}\n"
        res += f"Ngân sách: {'{:,.0f}đ'.format(total_budget).replace(',', '.')}\n"
        res += f"Còn lại: {'{:,.0f}đ'.format(remaining).replace(',', '.')}\n"
        
        if remaining < 0:
            res += f"Vượt ngân sách {'{:,.0f}đ'.format(abs(remaining)).replace(',', '.')}! Cần điều chỉnh lại."
            
        return res
    except ValueError:
        return "Lỗi định dạng: Tổng ngân sách và số tiền chi tiêu phải là chữ số."
    except Exception as e:
        return f"Lỗi định dạng expenses! Hãy dùng định dạng 'vé máy bay:890000,khách sạn:650000'. (Chi tiết: {str(e)})"
    

# --- KẾT THÚC CODE tools.py ---