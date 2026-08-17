# backend/video_catalog.py
"""
Curated YouTube Video & Benchmark Hub Generator
Generates dynamic, tag-based YouTube search & benchmark hubs EXCLUSIVELY for Product Recommendations & Specs.
"""

import urllib.parse
from typing import Optional, Dict

def make_yt_search(query: str) -> str:
    return f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"

def get_video_hub(product_name: str) -> Optional[Dict]:
    """
    Returns YouTube Video Hub ONLY for product recommendations and specifications.
    Returns None for troubleshooting, diagnostic or support queries.
    """
    if not product_name:
        return None
    
    q_lower = product_name.lower().strip()
    
    # Strictly ignore troubleshooting terms
    if any(w in q_lower for w in ["flicker", "won't start", "not starting", "dead", "shut down", "not charging", "overheat", "heating", "fix", "issue", "problem", "broken", "repair", "troubleshoot", "not working", "drain"]):
        return None


    # 1. Flagship Phones (S25, S24, S23)
    if "s25" in q_lower:
        device_name = "Samsung Galaxy S25 Ultra" if "ultra" in q_lower else "Samsung Galaxy S25"
        return {
            "type": "product",
            "title": f"{device_name} Video Hub",
            "subtitle": "Explore verified 4K reviews, real-world camera tests, gaming benchmarks & teardowns",
            "main_url": make_yt_search(f"{device_name} full review MKBHD Mrwhosetheboss"),
            "tags": [
                {"label": "📷 200MP Camera & Zoom Test", "url": make_yt_search(f"{device_name} camera test 4K sample zoom")},
                {"label": "🎮 Snapdragon 8 Elite Gaming", "url": make_yt_search(f"{device_name} gaming test FPS thermals")},
                {"label": "🎙️ MKBHD Review", "url": make_yt_search(f"{device_name} Marques Brownlee MKBHD review")},
                {"label": "🔥 Mrwhosetheboss Review", "url": make_yt_search(f"{device_name} Mrwhosetheboss review")},
                {"label": "📦 Unboxing & First Look", "url": make_yt_search(f"{device_name} unboxing accessories first look")},
                {"label": "🔋 Battery Endurance Test", "url": make_yt_search(f"{device_name} battery drain test vs iPhone")}
            ]
        }

    if "s24" in q_lower:
        device_name = "Samsung Galaxy S24 Ultra" if "ultra" in q_lower else "Samsung Galaxy S24"
        return {
            "type": "product",
            "title": f"{device_name} Video Hub",
            "subtitle": "Explore titanium durability, 100x zoom cameras, AI features & reviews",
            "main_url": make_yt_search(f"{device_name} review MKBHD Dave2D"),
            "tags": [
                {"label": "📷 100x Space Zoom Test", "url": make_yt_search(f"{device_name} 100x zoom camera test")},
                {"label": "🎙️ MKBHD Review", "url": make_yt_search(f"{device_name} MKBHD titanium review")},
                {"label": "🎮 Gaming & Thermals", "url": make_yt_search(f"{device_name} Genshin Impact gaming benchmark")},
                {"label": "✨ Galaxy AI Features Demo", "url": make_yt_search(f"{device_name} Galaxy AI live translate circle to search")},
                {"label": "📦 Unboxing & Setup", "url": make_yt_search(f"{device_name} retail unboxing")}
            ]
        }

    # 2. Foldables (Fold / Flip)
    if "fold" in q_lower:
        return {
            "type": "product",
            "title": "Galaxy Z Fold6 Video Hub",
            "subtitle": "Watch multitasking benchmarks, hinge durability tests & productivity reviews",
            "main_url": make_yt_search("Samsung Galaxy Z Fold 6 review MKBHD Mrwhosetheboss"),
            "tags": [
                {"label": "📐 Dual Screen Multitasking", "url": make_yt_search("Galaxy Z Fold 6 multitasking productivity workflow")},
                {"label": "🎙️ MKBHD Review", "url": make_yt_search("Galaxy Z Fold 6 MKBHD review")},
                {"label": "🛡️ Hinge & Durability Drop Test", "url": make_yt_search("Galaxy Z Fold 6 JerryRigEverything durability test")},
                {"label": "🎮 Big Screen Gaming Test", "url": make_yt_search("Galaxy Z Fold 6 gaming benchmark")}
            ]
        }

    if "flip" in q_lower:
        return {
            "type": "product",
            "title": "Galaxy Z Flip6 Video Hub",
            "subtitle": "Watch FlexWindow cover screen tests, camera vlogging & compact reviews",
            "main_url": make_yt_search("Samsung Galaxy Z Flip 6 review Mrwhosetheboss"),
            "tags": [
                {"label": "📱 FlexWindow Cover Screen", "url": make_yt_search("Galaxy Z Flip 6 cover screen widgets apps")},
                {"label": "📸 Hands-Free Vlogging Test", "url": make_yt_search("Galaxy Z Flip 6 camera vlog test")},
                {"label": "🔥 Mrwhosetheboss Review", "url": make_yt_search("Galaxy Z Flip 6 Mrwhosetheboss review")},
                {"label": "🔋 Battery Life Review", "url": make_yt_search("Galaxy Z Flip 6 battery life test")}
            ]
        }

    # 3. Laptops (Galaxy Book)
    if any(w in q_lower for w in ["book", "laptop", "pc"]):
        return {
            "type": "product",
            "title": "Galaxy Book4 Pro & Ultra Video Hub",
            "subtitle": "Watch AMOLED display reviews, Intel Core Ultra benchmarks & video editing tests",
            "main_url": make_yt_search("Samsung Galaxy Book 4 Ultra Pro review Dave2D Just Josh"),
            "tags": [
                {"label": "💻 Dave2D Laptop Review", "url": make_yt_search("Galaxy Book 4 Ultra Dave2D review")},
                {"label": "🎨 3K AMOLED Display Test", "url": make_yt_search("Galaxy Book 4 Pro 3K Dynamic AMOLED display review")},
                {"label": "🎬 Premier Pro Video Editing", "url": make_yt_search("Galaxy Book 4 Ultra video editing 4K export test")},
                {"label": "🔋 Battery Life for College", "url": make_yt_search("Galaxy Book 4 battery life test for students")},
                {"label": "🔄 360 Touch & S-Pen Test", "url": make_yt_search("Galaxy Book 4 Pro 360 drawing S Pen test")}
            ]
        }

    # 4. Smart Televisions (Neo QLED, OLED, The Frame, QLED, Crystal 4K)
    if any(w in q_lower for w in ["tv", "television", "oled", "qled", "frame", "crystal 4k", "neo qled", "qn90", "qn80", "s95", "s90"]):
        tv_title = "Samsung Neo QLED & OLED Smart TV Hub"
        if "frame" in q_lower:
            tv_title = "Samsung The Frame 4K QLED Video Hub"
        elif "oled" in q_lower or "s95" in q_lower or "s90" in q_lower:
            tv_title = "Samsung OLED 4K (S95D / S90D) Video Hub"
        return {
            "type": "product",
            "title": tv_title,
            "subtitle": "Explore picture quality tests, 144Hz PS5 gaming benchmarks, sound demos & wall-mounting",
            "main_url": make_yt_search(f"{product_name} full review picture quality test RTINGS"),
            "tags": [
                {"label": "🎬 4K Picture Quality & Black Levels", "url": make_yt_search(f"{product_name} picture quality contrast test RTINGS")},
                {"label": "🎮 144Hz PS5 / PC Gaming Test", "url": make_yt_search(f"{product_name} PS5 Xbox gaming test VRR 120Hz")},
                {"label": "🔊 Dolby Atmos & Q-Symphony Sound", "url": make_yt_search(f"{product_name} sound test speakers Dolby Atmos")},
                {"label": "🖼️ Matte Display / Anti-Glare Demo", "url": make_yt_search(f"{product_name} glare test reflection bright room")},
                {"label": "📐 Unboxing & Wall Mount Setup", "url": make_yt_search(f"{product_name} unboxing wall mount setup")}
            ]
        }

    # 5. Washing Machines & Dryers (Bespoke AI, EcoBubble, Front Load, Top Load)
    if any(w in q_lower for w in ["washing machine", "washer", "dryer", "ecobubble", "laundry", "ww80", "ww90", "ww12", "wa10", "wa80", "wa65"]):
        wm_title = "Samsung AI EcoBubble Washing Machine Hub"
        if "top load" in q_lower or "wobble" in q_lower or "wa" in q_lower:
            wm_title = "Samsung Top Load EcoBubble Washer Hub"
        elif "bespoke" in q_lower or "combo" in q_lower:
            wm_title = "Samsung Bespoke AI Laundry Combo Hub"
        return {
            "type": "product",
            "title": wm_title,
            "subtitle": "Watch real wash cycle tests, stain removal demonstrations, noise benchmarks & SmartThings setup",
            "main_url": make_yt_search(f"{product_name} demo review wash test"),
            "tags": [
                {"label": "🧺 AI EcoBubble Wash & Stain Test", "url": make_yt_search(f"{product_name} stain removal wash cycle test")},
                {"label": "🔇 1400 RPM Spin & Vibration Noise", "url": make_yt_search(f"{product_name} spin noise vibration test decibel")},
                {"label": "⚡ Energy & Water Consumption", "url": make_yt_search(f"{product_name} power consumption water test")},
                {"label": "📱 SmartThings AI Control Setup", "url": make_yt_search(f"{product_name} SmartThings Wi-Fi mobile connection")},
                {"label": "💨 Hygiene Steam & Bedding Demo", "url": make_yt_search(f"{product_name} hygiene steam cycle demo")}
            ]
        }

    # 6. Audio (Galaxy Buds)
    if any(w in q_lower for w in ["bud", "buds", "earbud", "audio", "headphone"]):
        return {
            "type": "product",
            "title": "Galaxy Buds3 Pro Video Hub",
            "subtitle": "Watch Active Noise Cancellation tests, 24-bit Hi-Fi sound comparisons & microphone reviews",
            "main_url": make_yt_search("Samsung Galaxy Buds 3 Pro review MKBHD SoundGuys"),
            "tags": [
                {"label": "🎙️ MKBHD Blade Design Review", "url": make_yt_search("Galaxy Buds 3 Pro MKBHD review")},
                {"label": "🎧 ANC & Sound Quality Test", "url": make_yt_search("Galaxy Buds 3 Pro ANC noise cancelling test vs AirPods Pro")},
                {"label": "🎤 Microphone Call Quality", "url": make_yt_search("Galaxy Buds 3 Pro microphone call test in noisy street")},
                {"label": "📦 Unboxing & Fit Test", "url": make_yt_search("Galaxy Buds 3 Pro unboxing sound test")}
            ]
        }

    # 7. Default Generic Product Lookup (Only if looking like a product name)
    clean_title = product_name.title()
    return {
        "type": "product",
        "title": f"{clean_title} Video Hub",
        "subtitle": f"Watch unboxings, expert camera tests and verified reviews for {clean_title}",
        "main_url": make_yt_search(f"{product_name} review unboxing"),
        "tags": [
            {"label": "📦 Unboxing & Hands-on", "url": make_yt_search(f"{product_name} unboxing review")},
            {"label": "⭐ Top Tech Reviewers", "url": make_yt_search(f"{product_name} review MKBHD Beebom")},
            {"label": "📷 Camera & Performance", "url": make_yt_search(f"{product_name} camera gaming test")},
            {"label": "🔋 Battery & Charging Speed", "url": make_yt_search(f"{product_name} battery charging test")}
        ]
    }

