import os
import random
import time
import requests
import re
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

# In-memory OTP store: order_id -> {"otp": "1234", "expires_at": timestamp, "last_sent_at": timestamp, "action": "cancel", "attempts": 0}
_otp_store: Dict[str, dict] = {}

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()


def mask_phone_number(phone: str) -> str:
    """Format phone number as '+91 *****<last_3_digits>'."""
    if not phone:
        return "+91 *****000"
    digits = re.sub(r"[^\d]", "", phone)
    last_three = digits[-3:] if len(digits) >= 3 else digits
    return f"+91 *****{last_three}"


def generate_otp(order_id: str, action: str = "cancellation") -> str:
    """Generate a 4-digit OTP valid for 5 minutes (300 seconds)."""
    otp = f"{random.randint(1000, 9999)}"
    now = time.time()
    expires_at = now + 300
    _otp_store[order_id.upper()] = {
        "otp": otp,
        "expires_at": expires_at,
        "last_sent_at": now,
        "action": action,
        "attempts": 0
    }
    return otp


def can_resend_otp(order_id: str) -> Tuple[bool, int]:
    """
    Checks if 30 seconds have elapsed since the last OTP was sent.
    Returns (can_resend, seconds_remaining).
    """
    record = _otp_store.get(order_id.upper())
    if not record:
        return True, 0
    elapsed = time.time() - record.get("last_sent_at", 0)
    if elapsed < 30:
        return False, int(30 - elapsed)
    return True, 0


def get_active_otp(order_id: str) -> Optional[dict]:
    """Retrieve active OTP record for an order if not expired."""
    record = _otp_store.get(order_id.upper())
    if not record:
        return None
    if time.time() > record["expires_at"]:
        _otp_store.pop(order_id.upper(), None)
        return None
    return record


def send_telegram_otp(order: dict, action_type: str = "cancellation") -> Tuple[bool, str, str]:
    """
    Sends OTP via Telegram Bot API.
    Returns (telegram_sent, otp_code, message).
    Falls back gracefully if Telegram token is unreachable or invalid.
    """
    order_id = order.get("order_id", "").upper()
    customer_name = order.get("customer_name", "Customer")
    model_name = order.get("model_bought", "Device")
    chat_id = order.get("telegram_chat_id") or TELEGRAM_CHAT_ID
    bot_token = TELEGRAM_BOT_TOKEN

    otp = generate_otp(order_id, action_type)

    msg_text = (
        f"🔐 *TechStore Security Verification*\n\n"
        f"Hello *{customer_name}*,\n"
        f"Your One-Time Password (OTP) to authenticate *{action_type.capitalize()}* for Order *#{order_id}* ({model_name}) is:\n\n"
        f"👉 *`{otp}`*\n\n"
        f"⚠️ Valid for *5 minutes*. Do not share this OTP with anyone."
    )

    telegram_sent = False
    if bot_token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": msg_text,
                "parse_mode": "Markdown"
            }
            resp = requests.post(url, json=payload, timeout=6)
            if resp.status_code == 200:
                telegram_sent = True
                print(f"[Telegram OTP] Successfully delivered OTP {otp} to Telegram chat {chat_id}")
            else:
                print(f"[Telegram OTP API Warning] Telegram responded with {resp.status_code}: {resp.text}")
        except Exception as ex:
            print(f"[Telegram OTP Error] Failed to reach Telegram API: {ex}")

    # Fallback log output
    print(f"==================================================")
    print(f" [AUTH OTP] Order: {order_id} | Name: {customer_name}")
    print(f" [AUTH OTP] Phone: {mask_phone_number(order.get('phone', ''))}")
    print(f" [AUTH OTP] Code: {otp} (Action: {action_type})")
    print(f" [AUTH OTP] Telegram Delivered: {telegram_sent}")
    print(f"==================================================")

    return telegram_sent, otp, f"OTP {'sent to your Telegram' if telegram_sent else 'generated'}"


def send_telegram_reservation_otp(phone: str, customer_name: str, product_name: str) -> Tuple[bool, str, str]:
    """
    Sends OTP for in-store Click & Collect reservation authentication.
    """
    key = f"RES_{re.sub(r'[^0-9]', '', phone)}"
    otp = generate_otp(key, "reservation")
    chat_id = TELEGRAM_CHAT_ID
    bot_token = TELEGRAM_BOT_TOKEN

    msg_text = (
        f"🏷️ *TechStore 24-Hour Hold Verification*\n\n"
        f"Hello *{customer_name}*,\n"
        f"Your One-Time Password (OTP) to confirm your 24-Hour In-Store Hold for *{product_name}* is:\n\n"
        f"👉 *`{otp}`*\n\n"
        f"⚠️ Valid for *5 minutes*. Present your digital QR token at store pickup."
    )

    telegram_sent = False
    if bot_token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": msg_text,
                "parse_mode": "Markdown"
            }
            resp = requests.post(url, json=payload, timeout=6)
            if resp.status_code == 200:
                telegram_sent = True
        except Exception as ex:
            print(f"[Telegram Reservation OTP Error]: {ex}")

    print(f"==================================================")
    print(f" [RESERVATION OTP] Phone: {phone} | Name: {customer_name}")
    print(f" [RESERVATION OTP] Product: {product_name} | Code: {otp}")
    print(f"==================================================")

    return telegram_sent, otp, f"OTP {'sent to Telegram' if telegram_sent else 'ready'}"



def verify_otp(order_id: str, entered_otp: str) -> Tuple[bool, str]:
    """
    Verifies entered OTP against the active record for the order.
    Returns (is_valid, message).
    """
    order_id_clean = order_id.upper().strip()
    record = _otp_store.get(order_id_clean)

    if not record:
        return False, "No active OTP found for this order. Please request a new verification code."

    if time.time() > record["expires_at"]:
        _otp_store.pop(order_id_clean, None)
        return False, "The OTP has expired. Please request a new verification code."

    if record["attempts"] >= 3:
        _otp_store.pop(order_id_clean, None)
        return False, "Too many incorrect attempts. Please initiate the request again."

    if entered_otp.strip() == record["otp"]:
        _otp_store.pop(order_id_clean, None)
        return True, "OTP verified successfully."
    else:
        record["attempts"] += 1
        remaining = 3 - record["attempts"]
        return False, f"Incorrect OTP. {remaining} attempt(s) remaining."


def send_telegram_rejection_notice(order: dict, rejection_reason: str) -> bool:
    """
    Dispatches customer rejection notice via Telegram:
    'Hey <Name>, your order cancellation for #<OrderID> was rejected due to: <Reason>. Contact us for further information. Thank you.'
    """
    customer_name = order.get("customer_name") or "Customer"
    first_name = customer_name.split()[0] if customer_name else "Customer"
    order_id = order.get("order_id", "")
    
    # Required message text format
    msg_text = (
        f"Hey {first_name}, your order cancellation for #{order_id} was rejected due to: {rejection_reason}. "
        f"Contact us for further information. Thank you."
    )

    chat_id = order.get("telegram_chat_id") or os.getenv("TELEGRAM_CHAT_ID", "").strip() or TELEGRAM_CHAT_ID
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip() or TELEGRAM_BOT_TOKEN

    if not bot_token or not chat_id:
        print(f"[Telegram Notice Warning] Bot token or Chat ID is missing.")
        return False

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": msg_text,
        }
        resp = requests.post(url, json=payload, timeout=8)
        if resp.status_code == 200:
            print(f"[Telegram Notice] Dispatched rejection notice to {chat_id}: {msg_text}")
            return True
        else:
            print(f"[Telegram Notice API Warning] Status {resp.status_code}: {resp.text}")
            return False
    except Exception as ex:
        print(f"[Telegram Notice Error] Failed to send rejection notice: {ex}")
        return False


def send_telegram_status_update(order: dict, new_status: str, admin_notes: str = "") -> bool:
    """
    Dispatches automated order status update via Telegram when store manager changes status.
    """
    customer_name = order.get("customer_name") or "Customer"
    order_id = order.get("order_id", "")
    model_name = order.get("model_bought", "Device")
    
    status_emojis = {
        "Processing": "⏳",
        "Confirmed": "✅",
        "Shipped": "🚚",
        "Out for Delivery": "🛵",
        "Delivered": "🎉",
        "Cancelled": "🛑",
        "Returned": "🔄",
    }
    emoji = status_emojis.get(new_status, "📦")
    
    msg_text = (
        f"{emoji} *TechStore Order Status Update*\n\n"
        f"Hello *{customer_name}*,\n"
        f"Your Order *#{order_id}* for *{model_name}* is now:\n\n"
        f"👉 *Status:* `{new_status.upper()}`\n"
    )
    if admin_notes:
        msg_text += f"\n📝 *Note:* {admin_notes}\n"
    
    if new_status.lower() == "shipped":
        msg_text += "\n📍 *Delivery ETA:* 24–48 Business Hours. Keep your phone handy for courier delivery."
    elif new_status.lower() == "delivered":
        msg_text += "\n🛡️ Your 12-Month Official TechStore Brand Warranty is now active."

    chat_id = order.get("telegram_chat_id") or os.getenv("TELEGRAM_CHAT_ID", "").strip() or TELEGRAM_CHAT_ID
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip() or TELEGRAM_BOT_TOKEN

    if not bot_token or not chat_id:
        return False

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": msg_text,
            "parse_mode": "Markdown"
        }
        resp = requests.post(url, json=payload, timeout=8)
        return resp.status_code == 200
    except Exception as ex:
        print(f"[Telegram Status Update Error]: {ex}")
        return False



