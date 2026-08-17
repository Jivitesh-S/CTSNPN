import os
import sys
import requests
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def run_telegram_diagnostic():
    print("=" * 65)
    print("🤖 TELEGRAM BOT & CHAT ID DIAGNOSTIC TOOL")
    print("=" * 65)

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    # Allow command line overrides if provided
    if len(sys.argv) > 1:
        bot_token = sys.argv[1].strip()
    if len(sys.argv) > 2:
        chat_id = sys.argv[2].strip()

    print(f"\n[1] Configuration Check:")
    print(f"  • Bot Token in .env : '{bot_token}'")
    print(f"  • Chat ID in .env   : '{chat_id}'")

    # -------------------------------------------------------------
    # Step 1: Check Bot Token Format & API Validity
    # -------------------------------------------------------------
    print(f"\n[2] Testing Bot Token with Telegram API (getMe)...")
    
    if not bot_token:
        print("  ❌ ERROR: TELEGRAM_BOT_TOKEN is empty in .env!")
        return

    if ":" not in bot_token:
        print("  ⚠️ FORMAT WARNING:")
        print(f"     Your token '{bot_token}' only has the numerical Bot ID prefix.")
        print("     Telegram Bot tokens from @BotFather always have a colon ':' followed by a hash.")
        print("     Example format: 8792380665:AAHqZabc1234567890XYZ_abcdefg")
        print("     👉 Please open Telegram, go to @BotFather -> /mybots -> API Token to copy the FULL token.\n")

    get_me_url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        r = requests.get(get_me_url, timeout=8)
        if r.status_code == 200:
            bot_info = r.json().get("result", {})
            print(f"  ✅ Bot Token is VALID!")
            print(f"     • Bot Name     : {bot_info.get('first_name')}")
            print(f"     • Bot Username : @{bot_info.get('username')}")
            print(f"     • Bot ID       : {bot_info.get('id')}")
        elif r.status_code == 404:
            print(f"  ❌ Telegram API returned 404 Not Found.")
            print(f"     Reason: The token '{bot_token}' is not recognized as a full valid bot token by Telegram.")
            print(f"     Fix: Get the complete token string from @BotFather in Telegram.")
            return
        elif r.status_code == 401:
            print(f"  ❌ Telegram API returned 401 Unauthorized (Invalid Token).")
            return
        else:
            print(f"  ❌ Telegram API returned {r.status_code}: {r.text}")
            return
    except Exception as e:
        print(f"  ❌ Network error connecting to Telegram: {e}")
        return

    # -------------------------------------------------------------
    # Step 2: Testing Chat ID delivery (sendMessage)
    # -------------------------------------------------------------
    print(f"\n[3] Testing Chat ID message delivery (sendMessage)...")
    if not chat_id:
        print("  ❌ ERROR: TELEGRAM_CHAT_ID is empty in .env!")
        return

    send_msg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": (
            "🔔 *TechStore Telegram Verification Successful!*\n\n"
            "Your Telegram Bot and Chat ID are configured correctly and ready to receive 2FA OTP codes! 🎉"
        ),
        "parse_mode": "Markdown"
    }

    try:
        r2 = requests.post(send_msg_url, json=payload, timeout=8)
        if r2.status_code == 200:
            print(f"  ✅ Message DELIVERED to Chat ID: {chat_id}!")
            print(f"     Check your Telegram app — you should have received a test ping message right now.")
        else:
            err = r2.json()
            print(f"  ❌ Failed to send message to Chat ID {chat_id}.")
            print(f"     Telegram error {r2.status_code}: {err.get('description', r2.text)}")
            print("\n  💡 Common Fixes for Chat ID issues:")
            print("     1. If Chat ID is a user: Make sure you clicked 'START' or sent a message to the bot first.")
            print("     2. If Chat ID is a group/channel: Make sure your bot has been added as a member/admin to the group.")
            print("     3. For supergroups/channels, Chat IDs usually start with -100 (e.g. -1005325037472).")
    except Exception as e:
        print(f"  ❌ Error sending test message: {e}")

    print("\n" + "=" * 65)

if __name__ == "__main__":
    run_telegram_diagnostic()
