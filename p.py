# <============================================== IMPORTS =========================================================>
import time
from datetime import datetime, timezone, timedelta

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes

from Mikobot import StartTime, function
from Mikobot.main import get_readable_time
from Mikobot.plugins.helper_funcs.chat_status import check_admin

# <============================================== Fancy Fonts & Small Caps ========================================>  
def fancy_number_format(value):
    """Returns digits in fancy Unicode format."""
    fancy_digits = {'0': '𝟘', '1': '𝟙', '2': '𝟚', '3': '𝟛', '4': '𝟜', 
                    '5': '𝟝', '6': '𝟞', '7': '𝟟', '8': '𝟠', '9': '𝟡'}
    return ''.join(fancy_digits.get(char, char) for char in str(value))

def small_caps(text):
    """Converts regular text to small caps."""
    small_caps_map = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ',
        'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
        'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ',
        'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
    }
    return ''.join(small_caps_map.get(char, char) for char in text.lower())

def format_datetime():
    """Returns current UTC and IST date-time as strings."""
    utc_now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    ist_now = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S IST')
    return utc_now, ist_now

# <============================================== Ping Command =====================================================>
@check_admin(only_dev=True)
async def ptb_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message

    start_time = time.perf_counter()
    message = await msg.reply_text("🏓 Pinging...")
    elapsed_time = time.perf_counter() - start_time
    telegram_ping = f"{elapsed_time:.3f} seconds ({elapsed_time * 1000:.1f} ms)"

    uptime = get_readable_time(int(time.time() - StartTime))
    utc_now, ist_now = format_datetime()

    await message.edit_text(
        f"🏓 <b>{small_caps('pong')}</b>\n\n"
        f"⏱ <b>{small_caps('ping time')}:</b> <code>{fancy_number_format(elapsed_time):.3f} s</code>\n"
        f"🕒 <b>{small_caps('ping in ms')}:</b> <code>{fancy_number_format(elapsed_time * 1000):.1f} ms</code>\n"
        f"⏳ <b>{small_caps('uptime')}:</b> <code>{uptime}</code>\n\n"
        f"🗓 <b>{small_caps('date/time (utc)')}:</b> <code>{utc_now}</code>\n"
        f"🗓 <b>{small_caps('date/time (ist)')}:</b> <code>{ist_now}</code>",
        parse_mode=ParseMode.HTML,
    )

function(CommandHandler("ping", ptb_ping, block=False))
