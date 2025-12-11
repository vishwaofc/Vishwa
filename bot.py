import os
import requests
import asyncio
import random
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import phonenumbers

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8483482984:AAHjgwqeoMV0Z84Ti6v2MmaJmTR4oCeSlQM")
CHANNEL_ID = "@otpclgs"

USERNAME = os.environ.get("IVASMS_USERNAME", "ruchiyeahanna@gmail.com")
PASSWORD = os.environ.get("IVASMS_PASSWORD", "#Vishwa123")
LOGIN_URL = "https://www.ivasms.com/portal/live/my_sms"

ADS_LINKS = [
    "https://otieu.com/4/10239172",
    "https://otieu.com/4/10208217",
    "https://otieu.com/4/9964203",
    "https://otieu.com/4/9964213"
]

MAIN_CHANNEL_LINK = "https://t.me/otpclgs"
NUMBER_GROUP_LINK = "https://t.me/your_number_group"
BOT_OWNER_LINK = "https://t.me/your_owner"

bot = None

def get_country_info(number):
    try:
        parsed_number = phonenumbers.parse(number)
        country_code = phonenumbers.region_code_for_number(parsed_number)
        if not country_code:
            return "🌍 Unknown"

        flag = "".join(chr(127397 + ord(c)) for c in country_code)
        return f"{flag} {country_code}"
    except:
        return "🌍 Unknown"

def login_and_fetch():
    session = requests.Session()
    login_data = {
        "email": USERNAME,
        "password": PASSWORD
    }
    session.post(LOGIN_URL, data=login_data)

    response = session.get("https://www.ivasms.com/portal/live/my_sms")
    return response.text

def parse_messages(html):
    return [
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "number": "+22999123456",
            "service": "WhatsApp",
            "otp": "391-766",
            "msg": "391-766 هو رمز التحقق الخاص بك"
        }
    ]

def get_random_ads_link():
    return random.choice(ADS_LINKS)

async def send_to_telegram(teaser_msg, otp_msg):
    ads_link = get_random_ads_link()
    
    keyboard = [
        [InlineKeyboardButton("🔓 WATCH ADS TO VIEW OTP", url=ads_link)],
        [
            InlineKeyboardButton("📢 Main Channel", url=MAIN_CHANNEL_LINK),
            InlineKeyboardButton("📋 Number Group", url=NUMBER_GROUP_LINK)
        ],
        [InlineKeyboardButton("👨‍💻 BOT OWNER", url=BOT_OWNER_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        main_message = await bot.send_message(
            chat_id=CHANNEL_ID,
            text=teaser_msg,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=otp_msg,
            reply_to_message_id=main_message.message_id,
            parse_mode="HTML"
        )
        print(f"Message sent successfully to channel {CHANNEL_ID}")
    except Exception as e:
        print(f"Failed to send message: {e}")

def format_teaser_message(msg):
    country_info = get_country_info(msg["number"])
    return f"""
✨<b>New OTP Received</b>✨

🕒 <b>Time:</b> {msg['time']}
📞 <b>Number:</b> {msg['number']}
🌍 <b>Country:</b> {country_info}
🛠️ <b>Service:</b> {msg['service']}

🔐 <b>OTP Code:</b> ******
📝 <b>Message:</b> ******

⚠️ <b>WATCH ADS BELOW TO UNLOCK OTP CODE!</b>
""".strip()

def format_otp_message(msg):
    return f"""
🔓 <b>OTP UNLOCKED</b> 🔓

🔐 <b>OTP Code:</b> <code>{msg['otp']}</code>
📝 <b>Full Message:</b> {msg['msg']}
""".strip()

async def main():
    global bot
    
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set!")
        return
    if not USERNAME or not PASSWORD:
        print("Error: IVASMS_USERNAME or IVASMS_PASSWORD not set!")
        return
    
    bot = Bot(TOKEN)
    sent_otps = set()
    print("Bot started! Monitoring for new OTPs...")
    print(f"Sending messages to: {CHANNEL_ID}")

    while True:
        try:
            html = login_and_fetch()
            messages = parse_messages(html)

            for msg in messages:
                if msg['otp'] not in sent_otps:
                    teaser = format_teaser_message(msg)
                    otp_text = format_otp_message(msg)
                    await send_to_telegram(teaser, otp_text)
                    sent_otps.add(msg['otp'])
        except Exception as e:
            print(f"Error in main loop: {e}")

        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
