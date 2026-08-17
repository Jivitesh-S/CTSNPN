# scripts/generate_product_manuals.py
"""
Generates comprehensive official manuals, technical reference guides, brochures,
operating instructions, and maintenance guides for ALL 113 products in catalog.json.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = PROJECT_ROOT / "data" / "shop" / "catalog.json"
DOCS_DIR = PROJECT_ROOT / "data" / "shop" / "product_docs"

DOCS_DIR.mkdir(parents=True, exist_ok=True)

def generate_manual_text(product: dict) -> str:
    p_id = product.get("id", "")
    name = product.get("name", "")
    brand = product.get("brand", "Samsung")
    category = product.get("category", "")
    price = product.get("price", 0)
    stock = product.get("stock", "In stock")
    warranty = product.get("warranty_months", 12)
    desc = product.get("description", "")
    specs = product.get("specs", {})
    launch_date = product.get("launch_date", "2024")
    support_url = product.get("support_url", "")

    specs_formatted = "\n".join([f"- **{k.replace('_', ' ').title()}:** {v}" for k, v in specs.items()])

    # Category-specific instructions & troubleshooting
    cat_content = ""
    if category == "phone":
        cat_content = f"""
### 📱 Mobile Operating & Setup Guide
1. **Initial Setup & SIM Insertion:**
   - Use the SIM ejector tool to insert Nano-SIM or activate eSIM.
   - Power on by holding the Side Power Key for 3 seconds.
   - Use Samsung Smart Switch to transfer contacts, photos, and apps from your old device.
2. **Key Software & AI Features:**
   - **Galaxy AI (Circle to Search, Live Translate, Note Assist):** Access via Galaxy AI settings.
   - **Samsung DeX:** Connect wirelessly to any PC or monitor for a desktop workstation experience.
   - **Samsung Knox Vault:** Hardware-isolated security protecting PIN, biometric, and cryptographic keys.
   - **Camera Modes:** Expert RAW, 8K Video Recording, Nightography, Astro-hyperlapse, and Single Take.
3. **Battery & Device Care:**
   - Protect Battery feature limits charging to 80% to maximize long-term lithium-ion lifespan.
   - Supports 25W/45W Super Fast Charging with certified USB PD 3.0 PPS adapters.
4. **Phone Troubleshooting & Diagnostics:**
   - **Force Restart:** Press and hold Volume Down + Side Key simultaneously for 10-15 seconds.
   - **Screen Freeze:** Clear cache partition in Android Recovery Mode or use Device Care auto-optimization.
   - **Moisture Detected Warning:** Dry the USB-C port thoroughly before plugging in a charger.
"""
    elif category == "laptop":
        cat_content = f"""
### 💻 Galaxy Book Laptop Manual & Technical Reference
1. **First-Time Setup & Windows 11 Activation:**
   - Connect the included USB-C Fast Charger before turning on for the first time.
   - Press the Power Button with integrated Fingerprint Sensor for instant Windows Hello login.
   - Run Samsung Update and Windows Update to install latest Intel/NVIDIA graphics drivers.
2. **Samsung Ecosystem Integration:**
   - **Second Screen:** Use your Galaxy Tab S9/S8 as a wireless secondary display.
   - **Multi Control:** Use laptop keyboard and touchpad to control your Galaxy smartphone seamlessly.
   - **Quick Share:** High-speed peer-to-peer file transfer between Samsung devices.
   - **Samsung Studio:** AI-powered video editing and subtitle generation.
3. **Performance & Cooling Modes:**
   - Press Fn + F11 to toggle Performance Modes: Silent, Optimized, and High Performance.
   - Dual-fan vapor chamber thermal management prevents CPU/GPU throttling during 4K video rendering.
4. **Laptop Maintenance & Care:**
   - Clean the 3K AMOLED screen only with a dry microfiber cloth (avoid alcohol sprays).
   - Keep air intake vents on the bottom panel clear of dust and fabric.
"""
    elif category == "tv":
        cat_content = f"""
### 📺 Smart TV Installation, Calibration & User Guide
1. **Unboxing & Mounting Instructions:**
   - Handle panel from the outer metal bezels; do not apply pressure to the center glass screen.
   - Supports standard VESA Wall Mounts and Samsung Slim-Fit No-Gap Wall Mounts.
   - Connect external HDMI sources to HDMI 2.1 ports (Port 3 is dedicated for eARC soundbars).
2. **Tizen OS & SmartThings Hub:**
   - Built-in SmartThings Hub allows direct control of Matter and Zigbee smart home appliances.
   - **Gaming Hub:** Play Xbox Cloud Gaming, GeForce NOW, and PlayStation titles directly without a console at up to 144Hz VRR.
   - **Q-Symphony:** Simultaneously synchronizes TV speakers with Samsung Soundbars for 3D surround sound.
3. **Picture Calibration & Art Mode:**
   - Filmmaker Mode disables motion smoothing to present movies as intended by the director.
   - Art Store (The Frame / Neo QLED) provides 2,500+ museum-quality digital artworks with ambient brightness auto-dimming.
4. **TV Diagnostics & Troubleshooting:**
   - **Self Diagnosis:** Go to Settings > Support > Device Care > Picture Test / Sound Test.
   - **Cold Reboot:** Hold the Remote Power button for 5 seconds until the TV restarts.
   - **Red Light Blinking:** Power reset by unplugging from wall for 60 seconds to discharge static capacitors.
"""
    elif category == "washing_machine":
        cat_content = f"""
### 🧺 Washing Machine & Dryer Technical Manual & Maintenance Guide
1. **Installation & Leveling:**
   - **Transit Bolts:** Remove all 4 shipping bolts from the back panel before first wash to prevent severe vibration!
   - Level all 4 rubber feet using a spirit level and tighten locking nuts firmly.
   - Inlet water pressure must be between 50 kPa and 800 kPa (0.5 to 8.0 bar).
2. **Core Wash Technologies & Programs:**
   - **AI EcoBubble:** Injects air into detergent to create active bubbles that penetrate fabric 40x faster in cold water.
   - **Hygiene Steam:** In-built heater boils water to 60°C/90°C to eliminate 99.9% of bacteria and allergens.
   - **AI Wash (4 Sensors):** Auto-senses load weight, fabric softness, and water turbidity to dose optimal detergent.
   - **AirWash:** Deodorizes and refreshes suits and delicate fabrics without water or harsh chemicals.
3. **Error Code Reference & Rapid Solutions:**
   - **4C / 4E:** Water Supply Error. Check inlet tap is open, hose unkinked, and clean mesh filter at rear inlet.
   - **5C / 5E / Nd:** Drainage Fault. Clean bottom-right emergency pump filter of coins, lint, and debris.
   - **Ub / UE:** Unbalanced Load. Rearrange bulky items evenly across the drum and rerun spin cycle.
   - **dC / dE:** Door Latch Open. Ensure laundry is not trapped in rubber gasket and push door until it clicks.
   - **AC6 / 3C:** Motor Communication Fault. Power cycle machine at main switch for 15 minutes.
4. **Maintenance & Cleaning Cycles:**
   - Run **Drum Clean+** cycle every 40 washes (no bleach or detergent required) to remove soap scum and odor.
"""
    elif category == "accessory":
        cat_content = f"""
### ⌚ Wearable & Accessory Technical Guide
1. **Pairing & Galaxy Wearable App:**
   - Open charging case or power on watch next to any Samsung phone for instant pop-up pairing.
   - Manage EQ presets, ANC noise control, gesture touch shortcuts, and widget layouts.
2. **Health Tracking & Sensor Calibration:**
   - BioActive sensor tracks ECG, blood pressure, BIA body composition, and sleep apnea metrics.
   - Dual-frequency GPS provides centimeter-accurate tracking for outdoor runs and cycling.
3. **Charging & Battery Longevity:**
   - Fast wireless charging cradle reaches 50% in 30 minutes.
   - Power Saving mode extends battery life up to 100 hours by disabling always-on display.
"""

    manual = f"""# {name} ({p_id}) - Official Product Manual & Technical Reference Sheet
**Brand:** {brand}
**Category:** {category.upper()}
**Model ID:** {p_id}
**Store Pricing:** Rs. {price:,}
**Current Stock Status:** {stock}
**Official Warranty Coverage:** {warranty} Months Manufacturer Brand Warranty
**Launch Date:** {launch_date}
**Official Support Reference:** {support_url}

---

## 📖 Product Overview & Description
{desc}

---

## ⚙️ Detailed Technical Specifications
{specs_formatted}

---

{cat_content}

---

## 🛡️ Warranty Terms & TechStore Service Desk Support
- **Warranty Period:** {warranty} Months from date of purchase.
- **Genuine Replacement:** 100% free parts and labor for manufacturing and hardware defects.
- **Service Center Support:** TechStore Walk-in Service Center:
  - **Address:** Ambattur Red Hills Rd, Velammal Nagar, Surapet, Chennai, Tamil Nadu 600066
  - **Hours:** 10:00 AM – 9:00 PM Daily (Monday to Sunday)
  - **Helpline Phone:** +91 9087086182
  - **WhatsApp Support:** Instant technician assistance available online.
"""
    return manual

def main():
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        products = json.load(f)

    print(f"Generating comprehensive manuals for {len(products)} products...")
    
    count = 0
    for p in products:
        p_id = p.get("id")
        content = generate_manual_text(p)
        doc_path = DOCS_DIR / f"{p_id}.txt"
        with open(doc_path, "w", encoding="utf-8") as out:
            out.write(content)
        count += 1

    print(f"Successfully generated {count} rich product manuals in {DOCS_DIR}")

if __name__ == "__main__":
    main()
