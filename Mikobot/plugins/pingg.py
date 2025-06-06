import time
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes

from Mikobot import StartTime, function
from Mikobot.plugins.helper_funcs.chat_status import check_admin

# <============================================== Fancy Fonts & Small Caps ========================================>
def fancy_number_format(value):
    """Returns digits in fancy Unicode format."""
    fancy_digits = {'0': '𝟘', '1': '𝟙', '2': '𝟚', '3': '𝟛', '4': '𝟜', 
                    '5': '𝟝', '6': '𝟞', '7': '𝟟', '8': '𝟠', '9': '𝟡'}
    return ''.join(fancy_digits.get(char, char) for char in str(value))

def small_caps(text):
    """Converts regular text to small caps."""
    return ''.join({
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ',
        'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
        'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ',
        'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
    }.get(char, char) for char in text.lower())

def format_datetime():
    """Returns current UTC and IST date-time as strings."""
    now_utc = datetime.now(timezone.utc)
    utc_now = now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')
    ist_now = (now_utc + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S IST')
    return utc_now, ist_now

def get_readable_time(seconds: int) -> str:
    """Convert seconds into a human-readable string."""
    periods = [('day', 86400), ('hour', 3600), ('minute', 60), ('second', 1)]
    result = []
    for name, count in periods:
        value = seconds // count
        if value:
            result.append(f"{value} {name}{'s' if value > 1 else ''}")
            seconds %= count
    return ', '.join(result) if result else '0 seconds'

# <============================================== Ping Command =====================================================>
@check_admin(only_dev=True)
async def ptb_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.perf_counter()
    message = await update.effective_message.reply_text("🏓 Pinging...")

    elapsed_time = time.perf_counter() - start_time
    uptime = get_readable_time(int(time.time() - StartTime))
    utc_now, ist_now = format_datetime()

    response = (
        f"🏓 <b>{small_caps('pong')}</b>\n\n"
        f"⏱ <b>{small_caps('ping time')}:</b> <code>{fancy_number_format(f'{elapsed_time:.3f}')} s</code>\n"
        f"🕒 <b>{small_caps('ping in ms')}:</b> <code>{fancy_number_format(f'{elapsed_time * 1000:.1f}')} ms</code>\n"
        f"⏳ <b>{small_caps('uptime')}:</b> <code>{uptime}</code>\n\n"
        f"🗓 <b>{small_caps('date/time (utc)')}:</b> <code>{utc_now}</code>\n"
        f"🗓 <b>{small_caps('date/time (ist)')}:</b> <code>{ist_now}</code>"
    )

    await message.edit_text(response, parse_mode=ParseMode.HTML)

function(CommandHandler("ping", ptb_ping, block=False))
