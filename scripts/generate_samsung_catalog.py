# scripts/generate_samsung_catalog.py
"""
Generates the comprehensive Samsung Product Catalog (2020-2026)
across Mobiles, Laptops, Smart TVs, Washing Machines, and Wearables/Accessories.
"""

import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = PROJECT_ROOT / "data" / "shop" / "catalog.json"

NOW_ISO = datetime.now().isoformat()

def make_yt_search(query: str) -> str:
    import urllib.parse
    return f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"

def generate_catalog():
    products = []
    
    # -------------------------------------------------------------
    # 1. SMARTPHONES & FOLDABLES (2020 - 2026)
    # -------------------------------------------------------------
    mobiles_data = [
        # S25 Series (2025/2026)
        ("P001", "Samsung Galaxy S25 Ultra", "phone", 134999, 12, "2025-01",
         "Flagship titanium powerhouse with Snapdragon 8 Elite, 200MP quad-camera, built-in S-Pen, and advanced Galaxy AI 2.0.",
         {"display": "6.9-inch Dynamic AMOLED 2X, QHD+, 120Hz, 2800 nits", "processor": "Snapdragon 8 Elite for Galaxy (3nm)", "ram_storage": "12GB/16GB RAM, 256GB/512GB/1TB UFS 4.0", "camera": "200MP main + 50MP ultra-wide + 50MP 5x periscope + 10MP 3x telephoto", "battery": "5000mAh, 45W wired, 15W wireless", "os_updates": "7 Years Android & Security Updates", "extras": "Titanium Frame, IP68, S-Pen, Gorilla Glass Armor"}),
        ("P002", "Samsung Galaxy S25+", "phone", 99999, 12, "2025-01",
         "Large screen flagship offering 6.7-inch QHD+ AMOLED display, Snapdragon 8 Elite, 4900mAh battery and full Galaxy AI suite.",
         {"display": "6.7-inch Dynamic AMOLED 2X, QHD+, 120Hz", "processor": "Snapdragon 8 Elite for Galaxy", "ram_storage": "12GB RAM, 256GB/512GB storage", "camera": "50MP main + 12MP ultra-wide + 10MP 3x telephoto", "battery": "4900mAh, 45W fast charging", "extras": "Armor Aluminum, IP68, 7 years OS updates"}),
        ("P003", "Samsung Galaxy S25", "phone", 84999, 12, "2025-01",
         "Compact flagship with 6.2-inch FHD+ 120Hz AMOLED screen, Snapdragon 8 Elite processor, 4000mAh battery and Galaxy AI.",
         {"display": "6.2-inch Dynamic AMOLED 2X, FHD+, 120Hz", "processor": "Snapdragon 8 Elite for Galaxy", "ram_storage": "12GB RAM, 128GB/256GB storage", "camera": "50MP main + 12MP ultra-wide + 10MP 3x telephoto", "battery": "4000mAh, 25W fast charging", "extras": "IP68, Armor Aluminum, 7 years OS updates"}),
        
        # S24 Series (2024)
        ("P004", "Samsung Galaxy S24 Ultra", "phone", 121999, 12, "2024-01",
         "First Galaxy AI flagship with titanium chassis, 200MP camera system, flat anti-glare display, and built-in S-Pen.",
         {"display": "6.8-inch Dynamic AMOLED 2X, QHD+, 120Hz, 2600 nits, Gorilla Armor", "processor": "Snapdragon 8 Gen 3 for Galaxy", "ram_storage": "12GB RAM, 256GB/512GB/1TB", "camera": "200MP main + 12MP ultra-wide + 50MP 5x periscope + 10MP 3x telephoto", "battery": "5000mAh, 45W charging", "extras": "Titanium frame, S-Pen, Circle to Search, Live Translate"}),
        ("P005", "Samsung Galaxy S24+", "phone", 89999, 12, "2024-01",
         "Premium flagship with 6.7-inch QHD+ 120Hz display, Exynos 2400 / Snapdragon 8 Gen 3, and 4900mAh battery.",
         {"display": "6.7-inch Dynamic AMOLED 2X, QHD+, 120Hz", "processor": "Exynos 2400 / Snapdragon 8 Gen 3", "ram_storage": "12GB RAM, 256GB/512GB", "camera": "50MP + 12MP + 10MP", "battery": "4900mAh, 45W charging", "extras": "Galaxy AI suite, Armor Aluminum 2.0"}),
        ("P006", "Samsung Galaxy S24", "phone", 74999, 12, "2024-01",
         "Compact premium device with 6.2-inch FHD+ 120Hz LTPO display, full Galaxy AI capabilities, and triple cameras.",
         {"display": "6.2-inch Dynamic AMOLED 2X, FHD+, 1-120Hz", "processor": "Exynos 2400 / Snapdragon 8 Gen 3", "ram_storage": "8GB RAM, 128GB/256GB", "camera": "50MP main + 12MP ultra-wide + 10MP telephoto", "battery": "4000mAh, 25W charging", "extras": "IP68 water resistance, Galaxy AI"}),
        ("P007", "Samsung Galaxy S24 FE", "phone", 59999, 12, "2024-10",
         "Fan Edition flagship offering 6.7-inch 120Hz AMOLED, Exynos 2400e chip, Galaxy AI features, and 4700mAh battery.",
         {"display": "6.7-inch Dynamic AMOLED 2X, FHD+, 120Hz", "processor": "Exynos 2400e (4nm)", "ram_storage": "8GB RAM, 128GB/256GB", "camera": "50MP main + 12MP ultra-wide + 8MP 3x telephoto", "battery": "4700mAh, 25W charging", "extras": "7 years updates, IP68"}),

        # S23 Series (2023)
        ("P008", "Samsung Galaxy S23 Ultra", "phone", 94999, 12, "2023-02",
         "Legendary flagship featuring 200MP ISOCELL HP2 sensor, Snapdragon 8 Gen 2 for Galaxy, 100x Space Zoom and S-Pen.",
         {"display": "6.8-inch Dynamic AMOLED 2X, QHD+, 120Hz", "processor": "Snapdragon 8 Gen 2 for Galaxy", "ram_storage": "12GB RAM, 256GB/512GB/1TB", "camera": "200MP + 12MP + 10MP (3x) + 10MP (10x periscope)", "battery": "5000mAh, 45W charging", "extras": "S-Pen, Astro Photography, IP68"}),
        ("P009", "Samsung Galaxy S23+", "phone", 69999, 12, "2023-02",
         "High-performance flagship with 6.6-inch AMOLED display, Snapdragon 8 Gen 2, and 4700mAh battery.",
         {"display": "6.6-inch Dynamic AMOLED 2X, FHD+, 120Hz", "processor": "Snapdragon 8 Gen 2 for Galaxy", "ram_storage": "8GB RAM, 256GB/512GB", "camera": "50MP + 12MP + 10MP", "battery": "4700mAh, 45W charging", "extras": "Armor Aluminum, IP68"}),
        ("P010", "Samsung Galaxy S23", "phone", 54999, 12, "2023-02",
         "Pocket-sized powerhouse with 6.1-inch 120Hz AMOLED, Snapdragon 8 Gen 2 for Galaxy, and 3900mAh battery.",
         {"display": "6.1-inch Dynamic AMOLED 2X, 120Hz", "processor": "Snapdragon 8 Gen 2 for Galaxy", "ram_storage": "8GB RAM, 128GB/256GB", "camera": "50MP + 12MP + 10MP", "battery": "3900mAh, 25W charging", "extras": "IP68, Wireless PowerShare"}),
        ("P011", "Samsung Galaxy S23 FE", "phone", 39999, 12, "2023-10",
         "Affordable flagship with 6.4-inch AMOLED display, Exynos 2200 / Snapdragon 8 Gen 1, and 50MP main camera.",
         {"display": "6.4-inch Dynamic AMOLED 2X, 120Hz", "processor": "Exynos 2200 / Snapdragon 8 Gen 1", "ram_storage": "8GB RAM, 128GB/256GB", "camera": "50MP + 12MP + 8MP telephoto", "battery": "4500mAh, 25W charging", "extras": "IP68 water resistance"}),

        # S22 Series (2022)
        ("P012", "Samsung Galaxy S22 Ultra", "phone", 74999, 12, "2022-02",
         "The first S-series phone with integrated Note S-Pen, 108MP camera with 100x zoom, and Snapdragon 8 Gen 1.",
         {"display": "6.8-inch Dynamic AMOLED 2X, QHD+, 120Hz", "processor": "Snapdragon 8 Gen 1 (4nm)", "ram_storage": "12GB RAM, 256GB/512GB", "camera": "108MP + 12MP + 10MP (3x) + 10MP (10x)", "battery": "5000mAh, 45W charging", "extras": "Built-in S-Pen, IP68"}),
        ("P013", "Samsung Galaxy S22+", "phone", 54999, 12, "2022-02",
         "Solid 6.6-inch AMOLED flagship with Snapdragon 8 Gen 1, 50MP camera and 4500mAh battery.",
         {"display": "6.6-inch Dynamic AMOLED 2X, 120Hz", "processor": "Snapdragon 8 Gen 1", "ram_storage": "8GB RAM, 128GB/256GB", "camera": "50MP + 12MP + 10MP", "battery": "4500mAh, 45W charging", "extras": "Armor Aluminum, IP68"}),
        ("P014", "Samsung Galaxy S22", "phone", 42999, 12, "2022-02",
         "Compact glass and aluminum flagship with 6.1-inch 120Hz AMOLED and 50MP triple camera.",
         {"display": "6.1-inch Dynamic AMOLED 2X, 120Hz", "processor": "Snapdragon 8 Gen 1", "ram_storage": "8GB RAM, 128GB/256GB", "camera": "50MP + 12MP + 10MP", "battery": "3700mAh, 25W charging", "extras": "IP68"}),

        # S21 Series (2021)
        ("P015", "Samsung Galaxy S21 Ultra 5G", "phone", 58999, 12, "2021-01",
         "Iconic contour-cut flagship with 108MP quad-camera, dual telephoto lenses (3x & 10x), and S-Pen support.",
         {"display": "6.8-inch Dynamic AMOLED 2X, WQHD+, 120Hz", "processor": "Exynos 2100 / Snapdragon 888", "ram_storage": "12GB/16GB RAM, 256GB/512GB", "camera": "108MP + 12MP + 10MP + 10MP", "battery": "5000mAh, 25W charging", "extras": "S-Pen compatible, IP68"}),
        ("P016", "Samsung Galaxy S21 FE 5G", "phone", 28999, 12, "2022-01",
         "Fan favorite offering flagship speed, 6.4-inch 120Hz AMOLED, Snapdragon 888 / Exynos 2100, and pro-grade cameras.",
         {"display": "6.4-inch Dynamic AMOLED 2X, 120Hz", "processor": "Snapdragon 888 / Exynos 2100", "ram_storage": "8GB RAM, 128GB/256GB", "camera": "12MP + 12MP + 8MP 3x telephoto", "battery": "4500mAh, 25W charging", "extras": "IP68, Wireless charging"}),
        
        # S20 Series (2020)
        ("P017", "Samsung Galaxy S20 Ultra 5G", "phone", 46999, 12, "2020-02",
         "Pioneering 100x Space Zoom camera flagship with 108MP sensor, 6.9-inch 120Hz AMOLED and 5000mAh battery.",
         {"display": "6.9-inch Dynamic AMOLED 2X, QHD+, 120Hz", "processor": "Exynos 990 / Snapdragon 865", "ram_storage": "12GB/16GB RAM, 128GB/512GB", "camera": "108MP + 12MP + 48MP 4x periscope + ToF", "battery": "5000mAh, 45W charging", "extras": "100x Space Zoom, IP68"}),
        ("P018", "Samsung Galaxy S20 FE 5G", "phone", 24999, 12, "2020-10",
         "Best-selling budget flagship with Snapdragon 865 5G, 6.5-inch 120Hz Super AMOLED, and IP68 rating.",
         {"display": "6.5-inch Super AMOLED, 120Hz, HDR10+", "processor": "Snapdragon 865 5G (7nm+)", "ram_storage": "8GB RAM, 128GB storage + microSD", "camera": "12MP main (OIS) + 12MP ultra-wide + 8MP telephoto", "battery": "4500mAh, 25W fast charging", "extras": "IP68 rating, stereo speakers by AKG"}),

        # Z Series Foldables (2020 - 2026)
        ("P019", "Samsung Galaxy Z Fold6", "phone", 164999, 12, "2024-07",
         "Ultra-thin book-style foldable with symmetrical bezel design, dual displays, Snapdragon 8 Gen 3, and Galaxy AI.",
         {"main_display": "7.6-inch Dynamic AMOLED 2X Foldable, 120Hz", "cover_display": "6.3-inch Dynamic AMOLED 2X, 120Hz", "processor": "Snapdragon 8 Gen 3 for Galaxy", "ram_storage": "12GB RAM, 256GB/512GB/1TB", "camera": "50MP + 12MP + 10MP", "battery": "4400mAh, 25W charging", "extras": "Dual screen multitasking, IP48, S-Pen fold edition"}),
        ("P020", "Samsung Galaxy Z Flip6", "phone", 109999, 12, "2024-07",
         "Pocket foldable with 3.4-inch FlexWindow cover display, 50MP camera, vapor chamber cooling, and Snapdragon 8 Gen 3.",
         {"main_display": "6.7-inch Dynamic AMOLED 2X Foldable, 120Hz", "cover_display": "3.4-inch Super AMOLED FlexWindow", "processor": "Snapdragon 8 Gen 3 for Galaxy", "ram_storage": "12GB RAM, 256GB/512GB", "camera": "50MP main + 12MP ultra-wide", "battery": "4000mAh, 25W charging", "extras": "FlexCam, Auto Zoom, IP48"}),
        ("P021", "Samsung Galaxy Z Fold5", "phone", 139999, 12, "2023-07",
         "Zero-gap flex hinge foldable with 7.6-inch main screen, Snapdragon 8 Gen 2, and pro productivity multi-window.",
         {"main_display": "7.6-inch Dynamic AMOLED 2X, 120Hz", "cover_display": "6.2-inch Dynamic AMOLED 2X", "processor": "Snapdragon 8 Gen 2 for Galaxy", "ram_storage": "12GB RAM, 256GB/512GB/1TB", "camera": "50MP + 12MP + 10MP", "battery": "4400mAh, 25W charging", "extras": "Flex Hinge, IPX8"}),
        ("P022", "Samsung Galaxy Z Flip5", "phone", 79999, 12, "2023-07",
         "Iconic flip phone with 3.4-inch FlexWindow outer display, Snapdragon 8 Gen 2, and gapless folding hinge.",
         {"main_display": "6.7-inch Dynamic AMOLED 2X, 120Hz", "cover_display": "3.4-inch Super AMOLED (720x748)", "processor": "Snapdragon 8 Gen 2 for Galaxy", "ram_storage": "8GB RAM, 256GB/512GB", "camera": "12MP + 12MP", "battery": "3700mAh, 25W charging", "extras": "Flex Hinge, IPX8"}),
        ("P023", "Samsung Galaxy Z Fold4", "phone", 114999, 12, "2022-08",
         "Durable foldable with taskbar OS integration, 50MP main camera, Snapdragon 8+ Gen 1, and IPX8 rating.",
         {"main_display": "7.6-inch Dynamic AMOLED 2X", "cover_display": "6.2-inch Dynamic AMOLED 2X", "processor": "Snapdragon 8+ Gen 1", "ram_storage": "12GB RAM, 256GB/512GB", "camera": "50MP + 12MP + 10MP", "battery": "4400mAh", "extras": "Taskbar, S-Pen"}),
        ("P024", "Samsung Galaxy Z Flip4", "phone", 59999, 12, "2022-08",
         "Stylish compact flip phone with Snapdragon 8+ Gen 1, 3700mAh battery, and FlexCam hands-free shooting.",
         {"main_display": "6.7-inch Dynamic AMOLED 2X", "cover_display": "1.9-inch Super AMOLED", "processor": "Snapdragon 8+ Gen 1", "ram_storage": "8GB RAM, 128GB/256GB", "camera": "12MP + 12MP", "battery": "3700mAh", "extras": "IPX8"}),
        ("P025", "Samsung Galaxy Z Fold3 5G", "phone", 89999, 12, "2021-08",
         "First water-resistant foldable with under-display camera, 120Hz dual displays, and S-Pen support.",
         {"main_display": "7.6-inch Foldable AMOLED, 120Hz", "cover_display": "6.2-inch AMOLED", "processor": "Snapdragon 888", "ram_storage": "12GB RAM, 256GB/512GB", "camera": "12MP + 12MP + 12MP", "battery": "4400mAh", "extras": "IPX8, UDC camera"}),
        ("P026", "Samsung Galaxy Z Flip3 5G", "phone", 44999, 12, "2021-08",
         "Mainstream foldable flip phone with 120Hz main screen, 1.9-inch cover display, and stereo speakers.",
         {"main_display": "6.7-inch Foldable AMOLED, 120Hz", "cover_display": "1.9-inch Super AMOLED", "processor": "Snapdragon 888", "ram_storage": "8GB RAM, 128GB/256GB", "camera": "12MP + 12MP", "battery": "3300mAh", "extras": "IPX8"}),
        ("P027", "Samsung Galaxy Z Fold2 5G", "phone", 74999, 12, "2020-09",
         "Groundbreaking foldable redesign with 6.2-inch full cover screen, 120Hz 7.6-inch inner screen, and Hideaway Hinge.",
         {"main_display": "7.6-inch Dynamic AMOLED 2X, 120Hz", "cover_display": "6.2-inch Super AMOLED", "processor": "Snapdragon 865+ 5G", "ram_storage": "12GB RAM, 256GB", "camera": "12MP + 12MP + 12MP", "battery": "4500mAh", "extras": "Hideaway Hinge with CAM mechanism"}),

        # Galaxy A Series Mid-Range (2020 - 2026)
        ("P028", "Samsung Galaxy A55 5G", "phone", 39999, 12, "2024-03",
         "Metal-frame mid-range device with 6.6-inch 120Hz Super AMOLED, Exynos 1480 with AMD GPU, and Knox Vault.",
         {"display": "6.6-inch Super AMOLED, FHD+, 120Hz, 1000 nits, Vision Booster", "processor": "Exynos 1480 (4nm) with Xclipse 530 GPU (AMD RDNA2)", "ram_storage": "8GB/12GB RAM, 128GB/256GB storage", "camera": "50MP main (OIS) + 12MP ultra-wide + 5MP macro", "battery": "5000mAh, 25W fast charging", "extras": "IP67 water/dust resistance, Metal frame, Knox Vault"}),
        ("P029", "Samsung Galaxy A35 5G", "phone", 28999, 12, "2024-03",
         "Premium glass back mid-ranger with 6.6-inch 120Hz AMOLED, 50MP camera with OIS, and 5000mAh battery.",
         {"display": "6.6-inch Super AMOLED, 120Hz, 1000 nits", "processor": "Exynos 1380 (5nm)", "ram_storage": "8GB RAM, 128GB/256GB", "camera": "50MP main (OIS) + 8MP ultra-wide + 5MP macro", "battery": "5000mAh, 25W charging", "extras": "IP67, Corning Gorilla Glass Victus+"}),
        ("P030", "Samsung Galaxy A54 5G", "phone", 33999, 12, "2023-03",
         "Glass design mid-ranger with 6.4-inch 120Hz Super AMOLED, Exynos 1380, and 50MP No Shake OIS camera.",
         {"display": "6.4-inch Super AMOLED, 120Hz", "processor": "Exynos 1380", "ram_storage": "8GB RAM, 128GB/256GB", "camera": "50MP + 12MP + 5MP", "battery": "5000mAh, 25W charging", "extras": "IP67 water resistance, Stereo speakers"}),
        ("P031", "Samsung Galaxy A34 5G", "phone", 24999, 12, "2023-03",
         "Vibrant 6.6-inch 120Hz AMOLED smartphone with Dimensity 1080 processor, 48MP OIS camera, and IP67 rating.",
         {"display": "6.6-inch Super AMOLED, 120Hz", "processor": "MediaTek Dimensity 1080 (6nm)", "ram_storage": "8GB RAM, 128GB", "camera": "48MP + 8MP + 5MP", "battery": "5000mAh, 25W charging", "extras": "IP67, 4 OS updates"}),
        ("P032", "Samsung Galaxy A73 5G", "phone", 37999, 12, "2022-04",
         "High-end A-series phone with 108MP OIS camera, 6.7-inch 120Hz Super AMOLED Plus, and Snapdragon 778G.",
         {"display": "6.7-inch Super AMOLED+, 120Hz", "processor": "Snapdragon 778G 5G", "ram_storage": "8GB RAM, 128GB/256GB", "camera": "108MP + 12MP + 5MP + 5MP", "battery": "5000mAh, 25W charging", "extras": "IP67"}),
        ("P033", "Samsung Galaxy A53 5G", "phone", 27999, 12, "2022-03",
         "Reliable all-rounder with 6.5-inch 120Hz Super AMOLED, 64MP OIS camera, Exynos 1280, and IP67 rating.",
         {"display": "6.5-inch Super AMOLED, 120Hz", "processor": "Exynos 1280 (5nm)", "ram_storage": "6GB/8GB RAM, 128GB", "camera": "64MP + 12MP + 5MP + 5MP", "battery": "5000mAh, 25W charging", "extras": "IP67"}),
        ("P034", "Samsung Galaxy A52s 5G", "phone", 26999, 12, "2021-09",
         "Legendary performer powered by Snapdragon 778G, 120Hz AMOLED, 64MP OIS quad-camera and IP67 rating.",
         {"display": "6.5-inch Super AMOLED, 120Hz", "processor": "Snapdragon 778G 5G (6nm)", "ram_storage": "6GB/8GB RAM, 128GB", "camera": "64MP + 12MP + 5MP + 5MP", "battery": "4500mAh, 25W charging", "extras": "IP67, 3.5mm headphone jack"}),
        ("P035", "Samsung Galaxy A51", "phone", 18999, 12, "2020-01",
         "Global top-selling phone of 2020 with 6.5-inch Super AMOLED Infinity-O screen, 48MP quad-camera, and 4000mAh battery.",
         {"display": "6.5-inch Super AMOLED, FHD+", "processor": "Exynos 9611 (10nm)", "ram_storage": "6GB/8GB RAM, 128GB", "camera": "48MP + 12MP + 5MP + 5MP", "battery": "4000mAh, 15W fast charging", "extras": "On-screen fingerprint, 3.5mm jack"}),

        # Galaxy M & F Series Monster Battery Phones (2020 - 2026)
        ("P036", "Samsung Galaxy M55 5G", "phone", 26999, 12, "2024-04",
         "Slim performance phone with Snapdragon 7 Gen 1, 6.7-inch 120Hz Super AMOLED+, 50MP selfie camera and 45W charging.",
         {"display": "6.7-inch Super AMOLED+, 120Hz, 1000 nits", "processor": "Snapdragon 7 Gen 1 (4nm)", "ram_storage": "8GB/12GB RAM, 128GB/256GB", "camera": "50MP OIS main + 8MP ultra-wide + 2MP macro, 50MP selfie", "battery": "5000mAh, 45W fast charging", "extras": "Stereo speakers by Dolby Atmos"}),
        ("P037", "Samsung Galaxy M35 5G", "phone", 19999, 12, "2024-07",
         "Battery beast featuring massive 6000mAh battery, 120Hz Super AMOLED display, Exynos 1380, and vapor cooling chamber.",
         {"display": "6.6-inch Super AMOLED, 120Hz, 1000 nits", "processor": "Exynos 1380 (5nm) with Vapor Cooling", "ram_storage": "6GB/8GB RAM, 128GB/256GB", "camera": "50MP main (OIS) + 8MP ultra-wide + 2MP macro", "battery": "6000mAh, 25W charging", "extras": "Corning Gorilla Glass Victus+, Knox Vault"}),
        ("P038", "Samsung Galaxy M34 5G", "phone", 16999, 12, "2023-07",
         "Monster 6000mAh battery phone with 120Hz Super AMOLED screen, 50MP No Shake OIS camera and 4 OS upgrades.",
         {"display": "6.5-inch Super AMOLED, 120Hz", "processor": "Exynos 1280 (5nm)", "ram_storage": "6GB/8GB RAM, 128GB", "camera": "50MP OIS + 8MP + 2MP", "battery": "6000mAh, 25W charging", "extras": "Voice Focus, Gorilla Glass 5"}),
        ("P039", "Samsung Galaxy M51", "phone", 22999, 12, "2020-09",
         "Record-breaking 7000mAh battery phone with Snapdragon 730G, 6.7-inch Super AMOLED Plus, and 25W reverse charging.",
         {"display": "6.7-inch Super AMOLED Plus, FHD+", "processor": "Snapdragon 730G (8nm)", "ram_storage": "6GB/8GB RAM, 128GB", "camera": "64MP main + 12MP ultra-wide + 5MP macro + 5MP depth", "battery": "7000mAh, 25W fast charging with reverse charging", "extras": "Dedicated microSD slot"}),
    ]

    for item in mobiles_data:
        p_id, name, cat, price, war, ldate, desc, specs = item
        products.append({
            "shop_id": "S001",
            "id": p_id,
            "name": name,
            "brand": "Samsung",
            "category": cat,
            "price": price,
            "stock": "In stock",
            "warranty_months": war,
            "description": desc,
            "specs": specs,
            "created_at": NOW_ISO,
            "support_url": f"https://www.samsung.com/in/support/model/{p_id}/",
            "launch_date": ldate,
            "video_review_url": make_yt_search(f"{name} review unboxing"),
            "video_review_title": f"{name} Full Review & Unboxing",
        })

    # -------------------------------------------------------------
    # 2. LAPTOPS (GALAXY BOOK SERIES 2020 - 2026)
    # -------------------------------------------------------------
    laptops_data = [
        # Galaxy Book5 (2025/2026)
        ("L001", "Samsung Galaxy Book5 Pro 360", "laptop", 184990, 12, "2025-01",
         "Next-generation Copilot+ PC powered by Intel Core Ultra Series 2 (Lunar Lake), 3K Dynamic AMOLED 2X touchscreen, and 47+ TOPS NPU.",
         {"display": "16-inch 3K Dynamic AMOLED 2X (2880x1800), 120Hz, 120% DCI-P3, Touch & S-Pen", "processor": "Intel Core Ultra 7 256V / Ultra 9 288V (Lunar Lake)", "ram_storage": "16GB/32GB LPDDR5X, 512GB/1TB PCIe 4.0 SSD", "graphics": "Intel Arc 140V Graphics (8 Xe2 cores)", "battery": "76Wh, up to 25 hours video playback, 65W USB-C adapter", "weight": "1.66 kg", "extras": "Included S-Pen, Copilot+ PC, Quad AKG speakers, Wi-Fi 7"}),

        # Galaxy Book4 Series (2024)
        ("L002", "Samsung Galaxy Book4 Ultra", "laptop", 239990, 12, "2024-02",
         "Ultra-premium creator and gaming laptop with 16-inch 3K AMOLED touch display, Intel Core Ultra 9, and NVIDIA RTX 4070 GPU.",
         {"display": "16-inch Dynamic AMOLED 2X Touch (2880x1800), 120Hz, Anti-Reflective, 400 nits", "processor": "Intel Core Ultra 9 185H (16 cores, up to 5.1GHz, Intel AI Boost NPU)", "ram_storage": "32GB LPDDR5X, 1TB PCIe 4.0 NVMe SSD", "graphics": "NVIDIA GeForce RTX 4070 (8GB GDDR6)", "battery": "76Wh, 140W USB-C Super Fast Charger (55% in 30 mins)", "weight": "1.86 kg", "extras": "Vapor Chamber cooling, Studio Quad speakers with Dolby Atmos, Wi-Fi 6E"}),
        ("L003", "Samsung Galaxy Book4 Pro 360", "laptop", 169990, 12, "2024-02",
         "2-in-1 convertible laptop with 16-inch 3K 120Hz AMOLED touchscreen, Intel Core Ultra 7, S-Pen included, and 76Wh battery.",
         {"display": "16-inch Dynamic AMOLED 2X Touch 3K (2880x1800), 120Hz, S-Pen included", "processor": "Intel Core Ultra 7 155H (16 cores, Intel AI Boost)", "ram_storage": "16GB/32GB LPDDR5X, 512GB/1TB SSD", "graphics": "Intel Arc Graphics", "battery": "76Wh, up to 21 hours battery life, 65W USB-C charging", "weight": "1.66 kg", "extras": "360-degree rotating hinge, S-Pen, Knox security"}),
        ("L004", "Samsung Galaxy Book4 Pro", "laptop", 139990, 12, "2024-02",
         "Ultra-slim premium laptop with 14-inch/16-inch 3K AMOLED screen, Intel Core Ultra 7, weighing just 1.23 kg.",
         {"display": "14-inch Dynamic AMOLED 2X (2880x1800), 120Hz, 120% DCI-P3", "processor": "Intel Core Ultra 7 155H", "ram_storage": "16GB LPDDR5X, 512GB SSD", "graphics": "Intel Arc Graphics", "battery": "63Wh, 65W USB-C fast charging", "weight": "1.23 kg", "extras": "Aluminum body, AKG Quad Speakers"}),
        ("L005", "Samsung Galaxy Book4 360", "laptop", 114990, 12, "2024-02",
         "Versatile 15.6-inch FHD Super AMOLED 2-in-1 touchscreen laptop with Intel Core 7 150U and S-Pen compatibility.",
         {"display": "15.6-inch FHD Super AMOLED Touchscreen (1920x1080)", "processor": "Intel Core 7 150U (10 cores, up to 5.4GHz)", "ram_storage": "16GB LPDDR5, 512GB SSD", "graphics": "Intel Graphics", "battery": "68Wh, 65W adapter", "weight": "1.46 kg", "extras": "360 convertible hinge, Dolby Atmos"}),
        ("L006", "Samsung Galaxy Book4 (Core 5)", "laptop", 69990, 12, "2024-02",
         "Mainstream productivity laptop with 15.6-inch FHD anti-glare display, Intel Core 5 120U, full port selection, and metal body.",
         {"display": "15.6-inch FHD Anti-Glare LED Display (1920x1080)", "processor": "Intel Core 5 120U (10 cores, up to 5.0GHz)", "ram_storage": "8GB/16GB LPDDR4X, 512GB NVMe SSD (dual SSD slots)", "graphics": "Intel Graphics", "battery": "54Wh, 45W USB-C charger", "weight": "1.55 kg", "extras": "Dual SSD expansion slots, HDMI, RJ45 LAN, MicroSD"}),

        # Galaxy Book3 Series (2023)
        ("L007", "Samsung Galaxy Book3 Ultra", "laptop", 199990, 12, "2023-02",
         "High-performance workstation laptop featuring 16-inch 3K AMOLED display, 13th Gen Intel Core i9, and NVIDIA RTX 4070.",
         {"display": "16-inch 3K Dynamic AMOLED 2X (2880x1800), 120Hz", "processor": "13th Gen Intel Core i9-13900H (14 cores, up to 5.4GHz)", "ram_storage": "32GB LPDDR5, 1TB NVMe SSD", "graphics": "NVIDIA GeForce RTX 4070 (8GB GDDR6)", "battery": "76Wh, 100W USB-C adapter", "weight": "1.79 kg", "extras": "AKG Quad speakers, Studio mics"}),
        ("L008", "Samsung Galaxy Book3 Pro 360", "laptop", 149990, 12, "2023-02",
         "Convertible 16-inch 3K AMOLED 120Hz 2-in-1 laptop with 13th Gen Intel Core i7-1360P and precision S-Pen.",
         {"display": "16-inch 3K Dynamic AMOLED 2X Touchscreen, 120Hz", "processor": "13th Gen Intel Core i7-1360P (12 cores)", "ram_storage": "16GB LPDDR5, 512GB SSD", "graphics": "Intel Iris Xe", "battery": "76Wh, 65W charging", "weight": "1.66 kg", "extras": "S-Pen included, 360 hinge"}),
        ("L009", "Samsung Galaxy Book3 Pro", "laptop", 124990, 12, "2023-02",
         "Lightweight 14-inch/16-inch 3K AMOLED 120Hz business laptop with 13th Gen Intel Core i7 and quad AKG speakers.",
         {"display": "14-inch 3K Dynamic AMOLED 2X, 120Hz", "processor": "13th Gen Intel Core i7-1360P", "ram_storage": "16GB LPDDR5, 512GB SSD", "graphics": "Intel Iris Xe", "battery": "63Wh, 65W USB-C adapter", "weight": "1.17 kg", "extras": "Full aluminum body, Thunderbolt 4"}),
        ("L010", "Samsung Galaxy Book3 360", "laptop", 99990, 12, "2023-02",
         "13.3-inch/15.6-inch FHD Super AMOLED 2-in-1 convertible with 13th Gen Intel Core i5/i7 and S-Pen support.",
         {"display": "13.3-inch FHD Super AMOLED Touch (1920x1080)", "processor": "13th Gen Intel Core i5-1335U", "ram_storage": "16GB LPDDR4X, 512GB SSD", "graphics": "Intel Iris Xe", "battery": "61.1Wh, 65W charger", "weight": "1.16 kg", "extras": "360 hinge, S-Pen compatible"}),

        # Galaxy Book2 Series (2022)
        ("L011", "Samsung Galaxy Book2 Pro 360", "laptop", 119990, 12, "2022-03",
         "Ultra-thin 13.3-inch/15.6-inch Super AMOLED 2-in-1 laptop with 12th Gen Intel Core i7, S-Pen, and 21h battery.",
         {"display": "13.3-inch FHD Super AMOLED Touch (1920x1080)", "processor": "12th Gen Intel Core i7-1260P (12 cores)", "ram_storage": "16GB LPDDR5, 512GB SSD", "graphics": "Intel Iris Xe", "battery": "63Wh, 65W USB-C adapter", "weight": "1.04 kg", "extras": "S-Pen included, Wi-Fi 6E"}),
        ("L012", "Samsung Galaxy Book2 Pro", "laptop", 99990, 12, "2022-03",
         "Featherlight 870g laptop with 13.3-inch AMOLED display, 12th Gen Intel Core i5/i7, and full-day battery.",
         {"display": "13.3-inch FHD AMOLED Display", "processor": "12th Gen Intel Core i5-1240P", "ram_storage": "16GB LPDDR5, 512GB SSD", "graphics": "Intel Iris Xe", "battery": "63Wh", "weight": "0.87 kg", "extras": "Military-grade durability, Fingerprint sensor"}),
        ("L013", "Samsung Galaxy Book2", "laptop", 58990, 12, "2022-03",
         "Everyday laptop with 15.6-inch FHD screen, 12th Gen Intel Core i5-1235U, dual SSD slots, and metal chassis.",
         {"display": "15.6-inch FHD Anti-Glare LED", "processor": "12th Gen Intel Core i5-1235U", "ram_storage": "8GB/16GB RAM, 512GB SSD", "graphics": "Intel Iris Xe", "battery": "54Wh, 45W charger", "weight": "1.57 kg", "extras": "Dual SSD slots"}),

        # Galaxy Book (2020 - 2021)
        ("L014", "Samsung Galaxy Book Pro 360 (2021)", "laptop", 89990, 12, "2021-04",
         "Original ultra-portable AMOLED convertible laptop with 11th Gen Intel Core i7 and S-Pen.",
         {"display": "13.3-inch FHD Super AMOLED Touchscreen", "processor": "11th Gen Intel Core i7-1165G7", "ram_storage": "16GB LPDDR4X, 512GB SSD", "graphics": "Intel Iris Xe", "battery": "63Wh", "weight": "1.04 kg", "extras": "S-Pen, Wi-Fi 6"}),
        ("L015", "Samsung Galaxy Book Go", "laptop", 34990, 12, "2021-06",
         "Always-connected, fanless, ultra-budget laptop with Qualcomm Snapdragon 7c Gen 2 processor, 18-hour battery, and 4G LTE.",
         {"display": "14.0-inch FHD TFT LCD (1920x1080), 180-degree hinge", "processor": "Qualcomm Snapdragon 7c Gen 2 Compute Platform (Octa-core)", "ram_storage": "4GB/8GB LPDDR4X, 128GB eUFS", "graphics": "Qualcomm Adreno GPU", "battery": "42.3Wh, up to 18 hours battery life, 25W USB-C fast charging", "weight": "1.38 kg", "extras": "Silent fanless design, 180-degree lay-flat hinge, Military-grade MIL-STD-810G durability"}),
        ("L016", "Samsung Galaxy Book Flex", "laptop", 94990, 12, "2020-05",
         "World's first laptop with QLED display, Wireless PowerShare trackpad, 10th Gen Intel Core i7, and integrated S-Pen.",
         {"display": "13.3-inch FHD QLED Display (600 nits Outdoor mode)", "processor": "10th Gen Intel Core i7-1065G7", "ram_storage": "16GB LPDDR4X, 512GB SSD", "graphics": "Intel Iris Plus", "battery": "69.7Wh with Wireless PowerShare on touchpad", "weight": "1.16 kg", "extras": "Built-in S-Pen silo, Royal Blue aluminum body"}),
        ("L017", "Samsung Galaxy Book Ion", "laptop", 84990, 12, "2020-05",
         "Ultra-lightweight magnesium alloy laptop with 13.3-inch QLED screen weighing just 970g with 10th Gen Intel Core i5/i7.",
         {"display": "13.3-inch FHD QLED Display, 600 nits", "processor": "10th Gen Intel Core i5-10210U", "ram_storage": "8GB/16GB DDR4, 512GB NVMe SSD", "graphics": "Intel UHD Graphics", "battery": "69.7Wh, Wireless PowerShare touchpad", "weight": "0.97 kg", "extras": "Aura Silver prism finish, AKG Stereo speakers"}),
    ]

    for item in laptops_data:
        p_id, name, cat, price, war, ldate, desc, specs = item
        products.append({
            "shop_id": "S001",
            "id": p_id,
            "name": name,
            "brand": "Samsung",
            "category": cat,
            "price": price,
            "stock": "In stock",
            "warranty_months": war,
            "description": desc,
            "specs": specs,
            "created_at": NOW_ISO,
            "support_url": f"https://www.samsung.com/in/support/model/{p_id}/",
            "launch_date": ldate,
            "video_review_url": make_yt_search(f"{name} review test"),
            "video_review_title": f"{name} Laptop Review & Benchmarks",
        })

    # -------------------------------------------------------------
    # 3. SMART TELEVISIONS (2020 - 2026)
    # -------------------------------------------------------------
    tvs_data = [
        # Neo QLED 8K (2021 - 2026)
        ("TV001", "Samsung 85\" Neo QLED 8K Smart TV (QN900D - 2024)", "tv", 899990, 24, "2024-04",
         "Flagship 8K AI TV with NQ8 AI Gen3 Processor, Infinity Air Design, 8K AI Upscaling Pro, Quantum Matrix Pro Mini-LEDs, and 90W 6.2.4Ch Dolby Atmos.",
         {"screen_size": "85-inch", "resolution": "8K Ultra HD (7680 x 4320)", "display_tech": "Neo QLED (Mini LED) Quantum Matrix Pro", "refresh_rate": "Up to 240Hz (Motion Xcelerator 240Hz)", "processor": "NQ8 AI Gen3 Processor (512 AI neural networks)", "audio": "90W 6.2.4Ch Dolby Atmos with Object Tracking Sound Pro", "hdr": "Neo Quantum HDR 8K Pro, Real Depth Enhancer Pro", "smart_features": "Tizen OS, AI Motion Enhancer Pro, Built-in SmartThings Hub, Gaming Hub", "ports": "4x HDMI 2.1 (8K@60Hz, 4K@240Hz, eARC), 3x USB, Attachable One Connect Box"}),
        ("TV002", "Samsung 75\" Neo QLED 8K Smart TV (QN800D - 2024)", "tv", 499990, 24, "2024-04",
         "Premium 8K Smart TV with NQ8 AI Gen2 Processor, Infinity One Design, 8K AI Upscaling, and 70W 4.2.2Ch Dolby Atmos audio.",
         {"screen_size": "75-inch", "resolution": "8K Ultra HD (7680 x 4320)", "display_tech": "Neo QLED Mini LED", "refresh_rate": "165Hz", "processor": "NQ8 AI Gen2 Processor", "audio": "70W 4.2.2Ch Dolby Atmos, OTS+", "ports": "4x HDMI 2.1, One Connect Box, Wi-Fi 6E"}),
        ("TV003", "Samsung 75\" Neo QLED 8K Smart TV (QN900C - 2023)", "tv", 449990, 24, "2023-04",
         "Flagship 2023 8K TV with Neural Quantum Processor 8K, Infinity Screen (99% screen-to-body), and 90W Dolby Atmos sound.",
         {"screen_size": "75-inch", "resolution": "8K UHD (7680 x 4320)", "display_tech": "Neo QLED Mini LED", "refresh_rate": "144Hz", "processor": "Neural Quantum Processor 8K", "audio": "90W 6.2.4Ch OTS Pro", "ports": "4x HDMI 2.1, Slim One Connect Box"}),

        # OLED 4K TVs (2022 - 2026)
        ("TV004", "Samsung 65\" OLED 4K Smart TV (S95D - 2024)", "tv", 239990, 24, "2024-04",
         "Award-winning OLED TV with OLED Glare-Free technology, NQ4 AI Gen2 Processor, 144Hz refresh rate, Pantone Validated colors, and 70W Dolby Atmos.",
         {"screen_size": "65-inch", "resolution": "4K Ultra HD (3840 x 2160)", "display_tech": "Quantum Dot OLED with Glare-Free Matte Coating", "refresh_rate": "144Hz (Motion Xcelerator 144Hz)", "processor": "NQ4 AI Gen2 Processor (20 neural networks)", "audio": "70W 4.2.2Ch Dolby Atmos with OTS+", "hdr": "OLED HDR Pro, Real Depth Enhancer", "gaming": "FreeSync Premium Pro, 4x HDMI 2.1, 4K 144Hz VRR", "smart_features": "Tizen OS with Knox Security, Slim One Connect Box"}),
        ("TV005", "Samsung 55\" OLED 4K Smart TV (S90D - 2024)", "tv", 149990, 24, "2024-04",
         "High-performance OLED TV with deep inky blacks, vibrant Quantum Dot colors, 144Hz gaming support, and NQ4 AI processor.",
         {"screen_size": "55-inch", "resolution": "4K Ultra HD (3840 x 2160)", "display_tech": "QD-OLED / WOLED Panel", "refresh_rate": "144Hz", "processor": "NQ4 AI Gen2 Processor", "audio": "40W 2.1Ch Dolby Atmos, OTS Lite", "ports": "4x HDMI 2.1 (4K@144Hz), 2x USB, eARC"}),
        ("TV006", "Samsung 65\" OLED 4K Smart TV (S95C - 2023)", "tv", 189990, 24, "2023-04",
         "Flagship 2023 QD-OLED TV with Neural Quantum Processor 4K, Infinity One Design with One Connect Box, and 70W 4.2.2Ch audio.",
         {"screen_size": "65-inch", "resolution": "4K UHD (3840 x 2160)", "display_tech": "QD-OLED", "refresh_rate": "144Hz", "processor": "Neural Quantum Processor 4K", "audio": "70W 4.2.2Ch Dolby Atmos", "ports": "4x HDMI 2.1, Slim One Connect Box"}),
        ("TV007", "Samsung 55\" OLED 4K Smart TV (S95B - 2022)", "tv", 119990, 24, "2022-04",
         "Samsung's first revolutionary Quantum Dot OLED TV featuring LaserSlim Design, self-illuminating pixels, and 120Hz 4K gaming.",
         {"screen_size": "55-inch", "resolution": "4K Ultra HD (3840 x 2160)", "display_tech": "QD-OLED", "refresh_rate": "120Hz", "processor": "Neural Quantum Processor 4K", "audio": "60W 2.2.2Ch Dolby Atmos", "ports": "4x HDMI 2.1"}),

        # Neo QLED 4K (2021 - 2026)
        ("TV008", "Samsung 65\" Neo QLED 4K Smart TV (QN90D - 2024)", "tv", 174990, 24, "2024-04",
         "Top-tier 4K Mini-LED TV with NQ4 AI Gen2 Processor, Quantum Matrix Technology, 144Hz refresh rate, and anti-glare wide viewing angle.",
         {"screen_size": "65-inch", "resolution": "4K Ultra HD (3840 x 2160)", "display_tech": "Neo QLED (Mini LED) with Anti-Reflection", "refresh_rate": "144Hz", "processor": "NQ4 AI Gen2 Processor", "audio": "60W 4.2.2Ch Dolby Atmos, OTS+", "hdr": "Neo Quantum HDR+", "ports": "4x HDMI 2.1 (4K@144Hz), eARC"}),
        ("TV009", "Samsung 55\" Neo QLED 4K Smart TV (QN85D - 2024)", "tv", 114990, 24, "2024-04",
         "Mini-LED 4K TV with Quantum Matrix Technology, NQ4 AI Processor, Dolby Atmos, and 120Hz gaming support.",
         {"screen_size": "55-inch", "resolution": "4K Ultra HD (3840 x 2160)", "display_tech": "Neo QLED Mini LED", "refresh_rate": "120Hz", "processor": "NQ4 AI Gen2 Processor", "audio": "40W 2.2Ch Dolby Atmos", "ports": "4x HDMI 2.1"}),
        ("TV010", "Samsung 65\" Neo QLED 4K Smart TV (QN90C - 2023)", "tv", 139990, 24, "2023-04",
         "2023 flagship 4K Mini-LED TV with Neural Quantum Processor 4K, Neo Quantum HDR+, and 60W 4.2.2Ch Dolby Atmos.",
         {"screen_size": "65-inch", "resolution": "4K UHD (3840 x 2160)", "display_tech": "Neo QLED Mini LED", "refresh_rate": "144Hz", "processor": "Neural Quantum Processor 4K", "audio": "60W 4.2.2Ch Dolby Atmos", "ports": "4x HDMI 2.1"}),
        ("TV011", "Samsung 55\" Neo QLED 4K Smart TV (QN90A - 2021)", "tv", 89990, 24, "2021-04",
         "First-generation Neo QLED 4K TV with Quantum Mini LEDs, Neo Quantum Processor 4K, and Object Tracking Sound+.",
         {"screen_size": "55-inch", "resolution": "4K UHD (3840 x 2160)", "display_tech": "Neo QLED Mini LED", "refresh_rate": "120Hz", "processor": "Neo Quantum Processor 4K", "audio": "60W 4.2.2Ch OTS+", "ports": "1x HDMI 2.1, 3x HDMI 2.0"}),

        # Lifestyle & Frame TVs (2020 - 2026)
        ("TV012", "Samsung 55\" The Frame 4K QLED TV (LS03D - 2024)", "tv", 94990, 24, "2024-04",
         "Artwork when it's off, TV when it's on. Features Matte Display (anti-reflection), customizable magnetic bezels, Art Mode with 2500+ curated art pieces, and Quantum HDR.",
         {"screen_size": "55-inch", "resolution": "4K Ultra HD (3840 x 2160)", "display_tech": "QLED with Matte Anti-Glare Display (Pantone ArtfulColor Validated)", "refresh_rate": "120Hz", "processor": "Quantum Processor 4K", "audio": "40W 2.0.2Ch Dolby Atmos with OTS", "design": "Modern Frame Design with customizable magnetic bezels & Slim-Fit Wall Mount included", "art_mode": "Samsung Art Store, Motion & Brightness Sensors", "ports": "4x HDMI 2.1 via One Connect Box, eARC"}),
        ("TV013", "Samsung 65\" The Frame 4K QLED TV (LS03C - 2023)", "tv", 119990, 24, "2023-04",
         "2023 Matte Display Frame TV with Art Mode, One Connect Box, 100% Color Volume with Quantum Dot, and Slim Fit Wall Mount.",
         {"screen_size": "65-inch", "resolution": "4K UHD (3840 x 2160)", "display_tech": "QLED Matte Display", "refresh_rate": "120Hz", "processor": "Quantum Processor 4K", "audio": "40W Dolby Atmos", "ports": "One Connect Box, 4x HDMI"}),
        ("TV014", "Samsung 55\" The Frame 4K QLED TV (LS03A - 2021)", "tv", 69990, 24, "2021-04",
         "Ultra-slim Frame TV with customizable bezels, Quantum Processor 4K, SpaceFit Sound, and Art Mode.",
         {"screen_size": "55-inch", "resolution": "4K UHD (3840 x 2160)", "display_tech": "QLED Display", "refresh_rate": "120Hz", "processor": "Quantum Processor 4K", "audio": "40W Stereo", "ports": "One Connect Box"}),
        ("TV015", "Samsung 43\" The Serif 4K QLED TV (LS01T)", "tv", 64990, 24, "2020-07",
         "Iconic 360-degree all-round design TV crafted by Bouroullec brothers with 'I' shape profile, NFC on TV, and metal floor stand.",
         {"screen_size": "43-inch", "resolution": "4K UHD (3840 x 2160)", "display_tech": "QLED Display", "refresh_rate": "60Hz", "audio": "40W 4.0Ch with NFC Tap View", "design": "360 Design with detachable metal easel stand", "ports": "4x HDMI, 2x USB"}),
        ("TV016", "Samsung 43\" The Sero Rotating 4K TV (LS05T)", "tv", 79990, 24, "2020-08",
         "World's first rotating TV screen that smoothly turns vertically for mobile content / TikTok and horizontally for movies.",
         {"screen_size": "43-inch", "resolution": "4K UHD (3840 x 2160)", "display_tech": "QLED Display with Motorized Rotating Screen", "refresh_rate": "60Hz", "audio": "60W 4.1Ch Premium Sound with deep bass", "smart_os": "Tizen OS with Mobile Mirroring Auto-Rotate", "ports": "3x HDMI, 2x USB"}),

        # QLED & Crystal 4K UHD Series (2020 - 2026)
        ("TV017", "Samsung 55\" QLED 4K Smart TV (Q60D - 2024)", "tv", 64990, 24, "2024-04",
         "Slim QLED TV with Quantum Processor Lite 4K, Dual LED backlight for enhanced contrast, 100% Color Volume, and AirSlim Design.",
         {"screen_size": "55-inch", "resolution": "4K Ultra HD (3840 x 2160)", "display_tech": "QLED with Dual LED Backlight", "refresh_rate": "60Hz (Motion Xcelerator)", "processor": "Quantum Processor Lite 4K", "audio": "20W 2Ch with OTS Lite & Q-Symphony", "ports": "3x HDMI (eARC), 2x USB, Wi-Fi 5"}),
        ("TV018", "Samsung 65\" QLED 4K Smart TV (Q80C - 2023)", "tv", 99990, 24, "2023-04",
         "Direct Full Array backlight QLED TV with Neural Quantum Processor 4K, 120Hz refresh rate, and 40W Dolby Atmos sound.",
         {"screen_size": "65-inch", "resolution": "4K UHD (3840 x 2160)", "display_tech": "QLED with Direct Full Array", "refresh_rate": "120Hz", "processor": "Neural Quantum Processor 4K", "audio": "40W 2.2Ch Dolby Atmos", "ports": "4x HDMI 2.1"}),
        ("TV019", "Samsung 55\" Crystal 4K UHD Smart TV (DU8000 - 2024)", "tv", 46990, 24, "2024-04",
         "Value-packed Crystal 4K UHD TV with Dynamic Crystal Color, Crystal Processor 4K, AirSlim body (26mm thin), and SmartThings Hub.",
         {"screen_size": "55-inch", "resolution": "4K Ultra HD (3840 x 2160)", "display_tech": "LED with Dynamic Crystal Color (1 Billion colors)", "refresh_rate": "60Hz (Motion Xcelerator)", "processor": "Crystal Processor 4K", "audio": "20W 2Ch with Q-Symphony & OTS Lite", "smart_os": "Tizen OS with SolarCell Remote", "ports": "3x HDMI (eARC), 2x USB, Optical Audio, LAN"}),
        ("TV020", "Samsung 43\" Crystal 4K UHD Smart TV (CU8000 - 2023)", "tv", 32990, 24, "2023-04",
         "Popular 43-inch Crystal 4K TV with Dynamic Crystal Color, AirSlim design, Tizen OS, and Voice Assistant support.",
         {"screen_size": "43-inch", "resolution": "4K Ultra HD (3840 x 2160)", "display_tech": "LED Display", "refresh_rate": "60Hz", "processor": "Crystal Processor 4K", "audio": "20W with OTS Lite", "ports": "3x HDMI, 2x USB"}),
        ("TV021", "Samsung 55\" Crystal 4K UHD Smart TV (AU8000 - 2021)", "tv", 38990, 24, "2021-04",
         "Slim Crystal 4K UHD TV with Dynamic Crystal Color, Crystal Processor 4K, PC on TV mode, and Bixby/Alexa built-in.",
         {"screen_size": "55-inch", "resolution": "4K UHD (3840 x 2160)", "display_tech": "LED Display", "refresh_rate": "60Hz", "processor": "Crystal Processor 4K", "audio": "20W Stereo with Q-Symphony", "ports": "3x HDMI, 2x USB"}),
        ("TV022", "Samsung 55\" Crystal 4K UHD Smart TV (TU8000 - 2020)", "tv", 34990, 24, "2020-04",
         "2020 Crystal 4K TV featuring Crystal Display, Ambient Mode, Game Enhancer, and clean cable management solution.",
         {"screen_size": "55-inch", "resolution": "4K UHD (3840 x 2160)", "display_tech": "LED Display", "refresh_rate": "60Hz", "processor": "Crystal Processor 4K", "audio": "20W 2Ch", "ports": "3x HDMI, 2x USB"}),
    ]

    for item in tvs_data:
        p_id, name, cat, price, war, ldate, desc, specs = item
        products.append({
            "shop_id": "S001",
            "id": p_id,
            "name": name,
            "brand": "Samsung",
            "category": cat,
            "price": price,
            "stock": "In stock",
            "warranty_months": war,
            "description": desc,
            "specs": specs,
            "created_at": NOW_ISO,
            "support_url": f"https://www.samsung.com/in/support/model/{p_id}/",
            "launch_date": ldate,
            "video_review_url": make_yt_search(f"{name} review picture test"),
            "video_review_title": f"{name} Picture Quality & Gaming Test",
        })

    # -------------------------------------------------------------
    # 4. WASHING MACHINES & DRYERS (2020 - 2026)
    # -------------------------------------------------------------
    wm_data = [
        # Bespoke AI Laundry Hubs & Combos (2024 - 2026)
        ("WM001", "Samsung Bespoke AI Laundry Combo 18kg/10kg (WD18DB8995BZ)", "washing_machine", 249990, 36, "2024-05",
         "All-in-one Washer and Heat Pump Dryer with 18kg Wash / 10kg Dry capacity. Features AI OptiWash & Dry, 7-inch LCD touchscreen, Super Speed 98 min cycle, and Auto Open Door.",
         {"capacity": "18 kg Wash / 10 kg Dry", "technology": "Heat Pump Dryer + Inverter EcoBubble Washer", "motor": "Digital Inverter Motor (20-Year Warranty)", "smart_features": "AI OptiWash & Dry (detects fabric & soil level), 7-inch AI Hub Touchscreen, SmartThings Wi-Fi", "cycle_time": "Super Speed Wash & Dry in 98 minutes", "efficiency": "5-Star Energy Rating with AI Energy Mode (up to 70% energy savings)", "dimensions": "686 x 1110 x 875 mm", "extras": "Auto Open Door, Auto Dispense System (holds up to 32 loads detergent)"}),
        ("WM002", "Samsung Bespoke AI Front Load 12kg (WW12BB944DGB)", "washing_machine", 68990, 36, "2024-03",
         "12kg Front Load Washer with SpaceMax technology (standard 600mm depth), AI EcoBubble, AI Wash 4-sensor system, and 1400 RPM spin.",
         {"capacity": "12 kg (SpaceMax technology)", "type": "Front Load Fully Automatic", "motor": "Digital Inverter Motor (20-Year Warranty)", "spin_speed": "1400 RPM", "technology": "AI EcoBubble, AI Wash (auto-detects weight & fabric softness)", "features": "Auto Dispenser, Hygiene Steam (eliminates 99.9% bacteria), Drum Clean+", "connectivity": "SmartThings Wi-Fi with AI Energy Mode", "energy_rating": "5 Star"}),
        ("WM003", "Samsung Bespoke AI Front Load 9kg (WW90BB844DGB)", "washing_machine", 48990, 36, "2024-03",
         "9kg Premium Front Load Washer with AI EcoBubble, QuickDrive (50% faster wash time), Hygiene Steam, and 1400 RPM.",
         {"capacity": "9 kg", "type": "Front Load Fully Automatic", "spin_speed": "1400 RPM", "technology": "AI EcoBubble + QuickDrive (Q-Bubble technology)", "steam": "Hygiene Steam with In-built Heater (up to 90°C)", "noise_level": "VRT Plus (Vibration Reduction Technology)", "connectivity": "SmartThings AI Control", "energy_rating": "5 Star"}),

        # Front Load EcoBubble Washers (2021 - 2024)
        ("WM004", "Samsung 8kg AI EcoBubble Front Load (WW80T504DAB)", "washing_machine", 36990, 36, "2023-02",
         "Top-rated 8kg Front Load Washing Machine with AI Pattern display, EcoBubble technology for cold wash fabric care, Hygiene Steam, and 1400 RPM.",
         {"capacity": "8 kg (Ideal for 3-4 family members)", "type": "Front Load Fully Automatic", "spin_speed": "1400 RPM", "technology": "EcoBubble (generates bubbles that penetrate fabric 40x faster)", "steam": "Hygiene Steam Cycle (99.9% allergen removal)", "motor": "Digital Inverter Motor with 20-Year Warranty", "programs": "21 Wash Programs (15' Quick Wash, Wool, Cotton, Bedding)", "connectivity": "SmartThings App Support & AI Control", "energy_rating": "5 Star Rating"}),
        ("WM005", "Samsung 7kg AI EcoBubble Front Load (WW70T502DAW)", "washing_machine", 31990, 36, "2023-02",
         "7kg Front Load Washer with AI Control, EcoBubble, Hygiene Steam with built-in heater, Diamond Drum, and 1200 RPM.",
         {"capacity": "7 kg (Suitable for couples & small families)", "type": "Front Load Fully Automatic", "spin_speed": "1200 RPM", "technology": "EcoBubble Technology", "heater": "Built-in Ceramic Heater (Rust-proof)", "steam": "Hygiene Steam Cycle", "motor": "Digital Inverter Motor (20-Year Warranty)", "energy_rating": "5 Star"}),
        ("WM006", "Samsung 6kg Inverter Front Load (WW60R20GLMA)", "washing_machine", 24990, 36, "2022-01",
         "Compact 6kg Front Load Washer with Digital Inverter, Hygiene Steam, 15-minute Quick Wash, and 1000 RPM spin.",
         {"capacity": "6 kg (Ideal for singles & bachelors)", "type": "Front Load Fully Automatic", "spin_speed": "1000 RPM", "technology": "Diamond Drum, Ceramic Heater", "steam": "Hygiene Steam at 60°C", "energy_rating": "5 Star Rating"}),

        # Washer Dryer Combos (2020 - 2024)
        ("WM007", "Samsung 12kg/8kg AI Control Washer Dryer (WD12TP44DSX)", "washing_machine", 79990, 36, "2023-05",
         "All-in-one Washer Dryer with 12kg Wash and 8kg 100% Dry capacity, AirWash deodorizing & sanitizing, AI Pattern control, and 1400 RPM.",
         {"capacity": "12 kg Wash / 8 kg Dry", "type": "Front Load Washer Dryer Combo", "spin_speed": "1400 RPM", "technology": "EcoBubble + AirWash (sanitizes without water or detergent)", "drying_tech": "Condenser Drying (100% Cupboard Dry)", "motor": "Digital Inverter Motor (20-Year Warranty)", "smart_features": "SmartThings AI Pattern Recognition", "energy_rating": "5 Star"}),
        ("WM008", "Samsung 9kg/6kg AddWash Washer Dryer (WD90T654DBX)", "washing_machine", 61990, 36, "2022-04",
         "Versatile Washer Dryer with AddWash door (add clothes mid-cycle), AirWash, Super Speed 59-min wash, and Hygiene Steam.",
         {"capacity": "9 kg Wash / 6 kg Dry", "type": "Washer Dryer with AddWash Door", "spin_speed": "1400 RPM", "technology": "AddWash, EcoBubble, AirWash, Super Speed (59 mins)", "motor": "Digital Inverter Motor (20-Year Warranty)", "energy_rating": "5 Star"}),
        ("WM009", "Samsung 8kg/5kg EcoBubble Washer Dryer (WD80T604DBX)", "washing_machine", 52990, 36, "2021-03",
         "8kg Wash / 5kg Dry combo with AI Control, AirWash, Hygiene Steam, and 1400 RPM Digital Inverter motor.",
         {"capacity": "8 kg Wash / 5 kg Dry", "type": "Washer Dryer Combo", "spin_speed": "1400 RPM", "technology": "EcoBubble, AirWash, Hygiene Steam", "energy_rating": "5 Star"}),

        # Top Load Washing Machines (2020 - 2026)
        ("WM010", "Samsung 10kg EcoBubble Top Load (WA10BG4686BV)", "washing_machine", 29990, 36, "2024-02",
         "Large 10kg Top Load Washer with EcoBubble, Dual Storm pulsator, Super Speed 29-min cycle, Soft Close glass lid, and SmartThings Wi-Fi.",
         {"capacity": "10 kg (Large family load)", "type": "Top Load Fully Automatic", "spin_speed": "700 RPM", "technology": "EcoBubble with Dual Storm Pulsator (tangle-free wash)", "tub": "Stainless Steel Diamond Drum", "smart_features": "SmartThings Wi-Fi with AI Energy Mode", "motor": "Digital Inverter Motor with 20-Year Warranty", "lid": "Soft Close Toughened Glass Lid", "energy_rating": "5 Star Rating"}),
        ("WM011", "Samsung 9kg EcoBubble Top Load (WA90BG4546BD)", "washing_machine", 25990, 36, "2023-08",
         "9kg Fully Automatic Top Load with EcoBubble, Magic Filter (lint free), Deep Softener mode, and 5-Star efficiency.",
         {"capacity": "9 kg", "type": "Top Load Fully Automatic", "spin_speed": "700 RPM", "technology": "EcoBubble, Dual Storm, Magic Filter", "motor": "Digital Inverter Motor (20-Year Warranty)", "energy_rating": "5 Star"}),
        ("WM012", "Samsung 8kg EcoBubble Top Load (WA80BG4441BG)", "washing_machine", 21990, 36, "2023-03",
         "8kg Top Load Washer with EcoBubble, 9 wash programs, Soft Close lid, Intensive Wash, and 20-year motor warranty.",
         {"capacity": "8 kg (Ideal for 3-5 members)", "type": "Top Load Fully Automatic", "spin_speed": "700 RPM", "technology": "EcoBubble, Magic Dispenser", "motor": "Digital Inverter Motor (20-Year Warranty)", "energy_rating": "5 Star"}),
        ("WM013", "Samsung 7kg Inverter Top Load (WA70BG4441BY)", "washing_machine", 18990, 36, "2022-06",
         "7kg Fully Automatic Top Load with EcoBubble, Magic Filter, Soft Closing door, and Digital Inverter Motor.",
         {"capacity": "7 kg", "type": "Top Load Fully Automatic", "spin_speed": "700 RPM", "technology": "EcoBubble, Diamond Drum", "motor": "Digital Inverter Motor (20-Year Warranty)", "energy_rating": "5 Star"}),
        ("WM014", "Samsung 6.5kg Wobble Top Load (WA65A4002VS)", "washing_machine", 14990, 36, "2021-01",
         "Best-selling 6.5kg Top Load Washer with Wobble Technology (prevents tangles & twists), Diamond Drum, and Magic Filter.",
         {"capacity": "6.5 kg (Ideal for 2-3 members)", "type": "Top Load Fully Automatic", "spin_speed": "680 RPM", "technology": "Wobble Pulsator (multi-directional wash flow)", "drum": "Diamond Drum (gentle on fabrics)", "programs": "6 Programs (Normal, Quick Wash, Delicates, Soak, Energy Saving, Eco Tub Clean)", "extras": "Magic Filter, Child Lock, Air Turbo Drying", "energy_rating": "5 Star Rating"}),
        ("WM015", "Samsung 7kg Wobble Top Load (WA70A4002GS)", "washing_machine", 16490, 36, "2020-08",
         "7kg Top Load Washer with Wobble Pulsator, Tempered glass lid, Magic Filter, and 5-Star BEE certification.",
         {"capacity": "7 kg", "type": "Top Load Fully Automatic", "spin_speed": "680 RPM", "technology": "Wobble Technology", "drum": "Diamond Drum", "energy_rating": "5 Star"}),
    ]

    for item in wm_data:
        p_id, name, cat, price, war, ldate, desc, specs = item
        products.append({
            "shop_id": "S001",
            "id": p_id,
            "name": name,
            "brand": "Samsung",
            "category": cat,
            "price": price,
            "stock": "In stock",
            "warranty_months": war,
            "description": desc,
            "specs": specs,
            "created_at": NOW_ISO,
            "support_url": f"https://www.samsung.com/in/support/model/{p_id}/",
            "launch_date": ldate,
            "video_review_url": make_yt_search(f"{name} review wash test"),
            "video_review_title": f"{name} Wash Test & Demo",
        })

    # -------------------------------------------------------------
    # 5. WEARABLES & ACCESSORIES (2020 - 2026)
    # -------------------------------------------------------------
    wearables_data = [
        # Galaxy Watch Series (2020 - 2026)
        ("A001", "Samsung Galaxy Watch Ultra (47mm LTE)", "accessory", 59999, 12, "2024-07",
         "Extreme rugged smartwatch with Grade 4 Titanium cushion frame, 100m water resistance (10ATM), dual-frequency GPS, Multi-Sport tile, and 100-hour battery life.",
         {"display": "1.5-inch Super AMOLED (480x480), Sapphire Crystal, 3000 nits peak brightness", "processor": "Exynos W1000 (3nm, 5-core)", "sensors": "BioActive Sensor (ECG, Optical Heart Rate, BIA Body Composition, Skin Temp, Dual GPS)", "battery": "590mAh, up to 100 hours in Power Saving mode", "durability": "Titanium Grade 4, 10ATM + IP68, MIL-STD-810H, Operating Temp -20°C to 55°C", "connectivity": "4G LTE eSIM, Bluetooth 5.3, Wi-Fi, NFC"}),
        ("A002", "Samsung Galaxy Watch7 (44mm Bluetooth)", "accessory", 32999, 12, "2024-07",
         "Advanced health smartwatch featuring 3nm Exynos W1000 chip, Dual-Frequency GPS, Energy Score AI, and FDA-authorized sleep apnea detection.",
         {"display": "1.5-inch Super AMOLED, Sapphire Crystal", "processor": "Exynos W1000 (3nm)", "sensors": "Enhanced BioActive Sensor, AGEs index tracker, ECG, Body Composition", "battery": "425mAh, Wireless Fast Charging", "durability": "5ATM + IP68, MIL-STD-810H"}),
        ("A003", "Samsung Galaxy Watch6 Classic (47mm BT)", "accessory", 28999, 12, "2023-07",
         "Timeless luxury smartwatch with rotating physical bezel, stainless steel case, 1.5-inch sapphire screen, and advanced sleep coaching.",
         {"display": "1.5-inch Super AMOLED, Sapphire Crystal, Rotating Bezel", "processor": "Exynos W930 (Dual Core 1.4GHz)", "sensors": "BioActive sensor, Blood pressure, ECG, Fall detection", "battery": "425mAh", "durability": "Stainless Steel, 5ATM + IP68"}),
        ("A004", "Samsung Galaxy Watch6 (40mm BT)", "accessory", 19999, 12, "2023-07",
         "Sleek everyday health watch with 20% larger display, thinner bezels, personalized heart rate zones, and One-Click band mechanism.",
         {"display": "1.3-inch Super AMOLED", "processor": "Exynos W930", "battery": "300mAh", "durability": "Armor Aluminum, 5ATM + IP68"}),
        ("A005", "Samsung Galaxy Watch5 Pro (45mm BT)", "accessory", 24999, 12, "2022-08",
         "Adventure smartwatch with Titanium casing, D-buckle magnetic strap, route workout with trackback navigation, and 3-day battery.",
         {"display": "1.4-inch Super AMOLED, Sapphire Glass", "processor": "Exynos W920", "battery": "590mAh (up to 80 hours)", "durability": "Titanium case, 5ATM + IP68"}),
        ("A006", "Samsung Galaxy Watch4 Classic (46mm)", "accessory", 14999, 12, "2021-08",
         "First Wear OS Powered by Samsung smartwatch with physical rotating bezel and Body Composition (BIA) analysis.",
         {"display": "1.4-inch Super AMOLED", "processor": "Exynos W920 (5nm)", "sensors": "BioActive sensor (BIA, ECG, Optical HR)", "battery": "361mAh"}),
        ("A007", "Samsung Galaxy Watch3 (45mm)", "accessory", 12999, 12, "2020-08",
         "Classic stainless steel smartwatch with rotating bezel, Tizen OS, SpO2 blood oxygen monitoring, and genuine leather strap.",
         {"display": "1.4-inch Super AMOLED, Gorilla Glass DX", "processor": "Exynos 9110", "battery": "340mAh"}),

        # Galaxy Ring (2024 - 2026)
        ("A008", "Samsung Galaxy Ring", "accessory", 38999, 12, "2024-07",
         "Ultra-lightweight titanium smart ring (2.3g) with 24/7 heart rate tracking, skin temperature sensor, sleep analysis, and 7-day battery life.",
         {"weight": "2.3g to 3.0g (Size 5 to 13)", "material": "Titanium Grade 5, concave design", "sensors": "Optical Bio-signal Sensor, Skin Temperature Sensor, Accelerometer", "battery": "Up to 7 days on single charge, transparent portable charging cradle", "durability": "10ATM + IP68 water resistance"}),

        # Galaxy Buds TWS Audio (2020 - 2026)
        ("A009", "Samsung Galaxy Buds3 Pro", "accessory", 23999, 12, "2024-07",
         "Blade design premium TWS earbuds with Blade Lights, 2-way dual amplifier drivers, Adaptive Noise Control, and 24-bit 96kHz SSC audio.",
         {"driver": "2-way (10.5mm dynamic woofer + 6.1mm planar tweeter)", "battery": "6 hours (ANC on), 26 hours with case", "connectivity": "Bluetooth 5.4, Seamless codec (24-bit 96kHz)", "extras": "Blade Lights, Adaptive ANC, Siren Detect, IP57 water resistance"}),
        ("A010", "Samsung Galaxy Buds3", "accessory", 14999, 12, "2024-07",
         "Open-type blade design earbuds with 11mm dynamic driver, active noise cancellation, and Galaxy AI live interpreter integration.",
         {"driver": "11mm dynamic driver", "battery": "5 hours (ANC on), 24 hours with case", "connectivity": "Bluetooth 5.4", "extras": "Open type fit, ANC, IP57"}),
        ("A011", "Samsung Galaxy Buds FE", "accessory", 6999, 12, "2023-10",
         "Fan Edition earbuds with ergonomic wingtips, powerful Active Noise Cancellation, deep bass, and 30-hour battery life.",
         {"driver": "1-way dynamic driver", "battery": "6 hours (ANC on), 21 hours with case", "connectivity": "Bluetooth 5.2, Auto Switch", "extras": "Wing-tip fit, ANC, Ambient sound, IPX2"}),
        ("A012", "Samsung Galaxy Buds2 Pro", "accessory", 12999, 12, "2022-08",
         "Compact ergonomic TWS earbuds with 24-bit Hi-Fi audio, Intelligent 3-mic ANC, 360 Audio with direct multichannel, and IPX7 rating.",
         {"driver": "2-way coaxial (10mm woofer + 5.3mm tweeter)", "battery": "5 hours (ANC on), 18 hours with case", "connectivity": "Bluetooth 5.3, SSC HiFi", "extras": "Voice Detect, IPX7 water resistance"}),
        ("A013", "Samsung Galaxy Buds2", "accessory", 7999, 12, "2021-08",
         "Lightweight 5g earbuds with 2-way dynamic speakers, Active Noise Cancellation, and customizable fit test.",
         {"driver": "2-way dynamic", "battery": "5 hours (ANC on), 20 hours with case", "connectivity": "Bluetooth 5.2", "extras": "ANC, 3-mic system, IPX2"}),
        ("A014", "Samsung Galaxy Buds Pro", "accessory", 9999, 12, "2021-01",
         "Professional-grade studio earbuds with intelligent ANC, 360 Audio, 2-way speakers by AKG, and IPX7 rating.",
         {"driver": "11mm woofer + 6.5mm tweeter", "battery": "5 hours (ANC on), 18 hours with case", "connectivity": "Bluetooth 5.0", "extras": "IPX7 waterproof"}),
        ("A015", "Samsung Galaxy Buds Live", "accessory", 5999, 12, "2020-08",
         "Unique ergonomic bean-shaped earbuds with glossy metallic finish, 12mm speaker by AKG, and open-type Active Noise Cancellation.",
         {"driver": "12mm driver with bass duct by AKG", "battery": "6 hours (ANC on), 21 hours with case", "connectivity": "Bluetooth 5.0", "extras": "Open-type ANC, Jewel case design"}),

        # Power & Tracking Accessories (2020 - 2026)
        ("A016", "Samsung Galaxy SmartTag2 (4-Pack)", "accessory", 8999, 12, "2023-10",
         "Smart Bluetooth and Ultra-Wideband (UWB) tracker with Compass View, IP67 water resistance, and 500-day battery life.",
         {"connectivity": "Bluetooth 5.3 + Ultra-Wideband (UWB)", "battery": "CR2032 replaceable battery (up to 500 days)", "durability": "IP67 dust and water resistant", "features": "Compass View, Lost Mode with NFC, Ring Phone"}),
        ("A017", "Samsung 65W Trio Power Adapter", "accessory", 3999, 12, "2022-01",
         "Multi-port fast charger with 65W USB-C PD 3.0, 25W USB-C, and 15W USB-A outputs to fast-charge laptops, phones and watches simultaneously.",
         {"ports": "2x USB-C (65W Max + 25W Max) + 1x USB-A (15W Max)", "power_delivery": "USB PD 3.0, PPS (Programmable Power Supply)", "compatibility": "Galaxy Book laptops, Galaxy S25/S24/S23, Tablets, Watches"}),
        ("A018", "Samsung 45W Super Fast Power Adapter", "accessory", 2999, 12, "2022-02",
         "Official 45W GaN fast charger with 5A Type-C to Type-C cable for Galaxy S25 Ultra, S24 Ultra, and Galaxy Tab S9.",
         {"output": "45W Super Fast Charging 2.0 (PPS)", "cable": "Includes 1.8m 5A USB-C to USB-C cable", "technology": "GaN (Gallium Nitride) cool operation"}),
        ("A019", "Samsung 25W Travel Power Adapter", "accessory", 1499, 12, "2020-02",
         "Standard 25W USB-C fast charger for Galaxy smartphones, tablets, and wireless charger pads.",
         {"output": "25W Super Fast Charging (USB PD 3.0)", "connector": "USB Type-C"}),
        ("A020", "Samsung 10,000mAh 25W Wireless Power Bank", "accessory", 3499, 12, "2020-08",
         "Portable battery pack with 25W wired fast charging and 7.5W Qi wireless charging pad for simultaneous charging of two devices.",
         {"capacity": "10,000 mAh", "output": "25W Wired Fast Charge + 7.5W Qi Wireless Pad", "ports": "2x USB-C ports, LED power indicators"}),
    ]

    for item in wearables_data:
        p_id, name, cat, price, war, ldate, desc, specs = item
        products.append({
            "shop_id": "S001",
            "id": p_id,
            "name": name,
            "brand": "Samsung",
            "category": cat,
            "price": price,
            "stock": "In stock",
            "warranty_months": war,
            "description": desc,
            "specs": specs,
            "created_at": NOW_ISO,
            "support_url": f"https://www.samsung.com/in/support/model/{p_id}/",
            "launch_date": ldate,
            "video_review_url": make_yt_search(f"{name} review unboxing"),
            "video_review_title": f"{name} Review & Setup",
        })

    # Save to catalog.json
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated catalog with {len(products)} products across 5 categories.")
    cats = {}
    for p in products:
        c = p.get('category')
        cats[c] = cats.get(c, 0) + 1
    print("Category Breakdown:", cats)

if __name__ == "__main__":
    generate_catalog()
