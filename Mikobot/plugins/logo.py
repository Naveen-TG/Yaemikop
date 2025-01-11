import io, os, random
import requests
from PIL import Image, ImageDraw, ImageFont
from Mikobot import app as QuantamBot
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatAction

__MODULE__ = "Lᴏɢᴏ"
__HELP__ = f"""
@{QuantamBot.username} ᴄᴀɴ ᴄʀᴇᴀᴛᴇ sᴏᴍᴇ ʙᴇᴀᴜᴛɪғᴜʟ ᴀɴᴅ ᴀᴛᴛʀᴀᴄᴛɪᴠᴇ ʟᴏɢᴏ ғᴏʀ ʏᴏᴜʀ ᴘʀᴏғɪʟᴇ ᴘɪᴄs.

๏ /logo (Text) *:* ᴄʀᴇᴀᴛᴇ ᴀ ʟᴏɢᴏ ᴏғ ʏᴏᴜʀ ɢɪᴠᴇɴ ᴛᴇxᴛ ᴡɪᴛʜ ʀᴀɴᴅᴏᴍ ᴠɪᴇᴡ.
"""

LOGO_LINKS = [
    "https://graph.org//file/85b028860a806850691fe.jpg",
    "https://graph.org//file/ea05097695dc1986e93b2.jpg",
    "https://graph.org//file/ffc0129562d2d0f020ea6.jpg",
    "https://graph.org//file/80973e756ba2a8ee92a63.jpg",
    "https://graph.org//file/6d9c7033e6c81dfdaf727.jpg"
]

@QuantamBot.on_message(filters.command("logo"))
async def LOGO_(b, m):
    if len(m.command) < 2:
        return await m.reply_text(
            "ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴄʀᴇᴀᴛᴇ ʟᴏɢᴏ ʙᴀʙᴇ !`\nExample `/logo mukesh`")
    
    text = m.text.split(None, 1)[1]
    pesan = await m.reply("**ᴄʀᴇᴀᴛɪɴɢ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛᴇᴅ ʟᴏɢᴏ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ sᴇᴄ...**")
    try:
        await b.send_chat_action(m.chat.id, ChatAction.UPLOAD_PHOTO)
        randc = random.choice(LOGO_LINKS)
        img = Image.open(io.BytesIO(requests.get(randc).content))
        draw = ImageDraw.Draw(img)
        image_widthz, image_heightz = img.size
        fnt = "Merisa/utils/BebasNeue.otf"
        font = ImageFont.truetype(fnt, 120)
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        h += int(h * 0.21)
        draw.text(
            ((image_widthz - w) / 2, (image_heightz - h) / 2),
            text,
            font=font,
            fill=(255, 255, 255),
        )
        x = (image_widthz - w) / 2
        y = (image_heightz - h) / 2 + 6
        draw.text(
            (x, y), text, font=font, fill="white", stroke_width=1, stroke_fill="black"
        )
        fname = "logo_result.png"
        img.save(fname)
        await m.reply_photo(
            photo=fname,
            caption=f"""━━━━━━━{QuantamBot.name}━━━━━━━

☘️ ʟᴏɢᴏ ᴄʀᴇᴀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ☘️
◈──────────────◈
🔥 ᴄʀᴇᴀᴛᴇᴅ ʙʏ : @{QuantamBot.username}
━━━━━━━{QuantamBot.name}━━━━━━━""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("➕ Aᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕", url=f"http://t.me/{QuantamBot.username}?startgroup=true")]
                ]
            ),
        )
        os.remove(fname)
        await pesan.delete()
    except Exception as e:
        await pesan.edit(f"🚫 **Error**: {e}")
