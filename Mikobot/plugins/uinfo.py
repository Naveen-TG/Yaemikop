import os
from PIL import Image, ImageChops, ImageDraw, ImageFont
from unidecode import unidecode
from pyrogram import filters
from pyrogram.enums import ParseMode
from Mikobot import app, OWNER_ID, DEV_USERS, DRAGONS, DEMONS, TIGERS, WOLVES

async def circle(pfp, size=(900, 900)):
    pfp = pfp.resize(size, Image.LANCZOS).convert("RGBA")
    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.LANCZOS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp

async def download_and_process_pfp(user):
    try:
        pic = await app.download_media(user.photo.big_file_id, file_name=f"pp{user.id}.png")
        if pic:
            pfp = Image.open(pic).convert("RGBA")
            return await circle(pfp, size=(900, 900))
    except Exception as e:
        print(e)
    finally:
        if "pic" in locals() and pic:
            os.remove(pic)
    return None

async def userinfopic(user, user_x, user_y, user_id_x, user_id_y, pfp_x_offset=0, pfp_y_offset=0, pfp_size=(1218, 1385)):
    user_name = unidecode(user.first_name)
    background = Image.open("Extra/user.jpg")
    background = background.resize((background.size[0], background.size[1]), Image.LANCZOS)
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("Extra/default.ttf", 100)

    try:
        pfp = await download_and_process_pfp(user)
        if pfp:
            pfp_x = 927 + pfp_x_offset
            pfp_y = (background.size[1] - pfp.size[1]) // 2 - 290 + pfp_y_offset
            pfp = await circle(pfp, size=pfp_size)
            background.paste(pfp, (pfp_x, pfp_y), pfp)
        user_name_bbox = draw.textbbox((user_x, user_y), user_name, font=font)
        user_id_bbox = draw.textbbox((user_id_x, user_id_y), str(user.id), font=font)
        draw.text((user_x, user_y), user_name, font=font, fill="white")
        draw.text((user_id_x, user_id_y), str(user.id), font=font, fill="white")
        userinfo = f"downloads/userinfo_{user.id}.png"
        background.save(userinfo)
    except Exception as e:
        print(f"Error: {e}")
        userinfo = None
    return userinfo

@app.on_message(filters.command("uinfo"))
async def userinfo_command(client, message):
    user = message.from_user
    user_x, user_y = 1035, 2885
    user_id_x, user_id_y = 1035, 2755
    try:
        processing_message = await message.reply("Processing user information...")
        image_path = await userinfopic(user, user_x, user_y, user_id_x, user_id_y)
        await processing_message.delete()
        if image_path:
            caption = (f"「 **According to the Mikos analogy, the userinfo is...** : 」\n\n"
                       f"❐  𝗜𝗗: {user.id}\n"
                       f"❐  𝗙𝗶𝗿𝘀𝘁 𝗡𝗮𝗺𝗲: {user.first_name}\n"
                       f"❐  𝗟𝗮𝘀𝘁 𝗡𝗮𝗺𝗲: {user.last_name}\n"
                       f"❐  𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: {user.username}\n"
                       f"❐  𝗨𝘀𝗲𝗿𝗹𝗶𝗻𝗸: [link](https://t.me/{user.username})\n")
            if user.id == OWNER_ID:
                caption += "\n\n〄 The disaster level of this user is **Owner**.\n"
            elif user.id in DEV_USERS:
                caption += "\n\n〄 This user is a member of **Developer**.\n"
            elif user.id in DRAGONS:
                caption += "\n\n〄 The disaster level of this user is **Sudo**.\n"
            elif user.id in DEMONS:
                caption += "\n\n〄 The disaster level of this user is **Demon**.\n"
            elif user.id in TIGERS:
                caption += "\n\n〄 The disaster level of this user is **Tiger**.\n"
            elif user.id in WOLVES:
                caption += "\n\n〄 The disaster level of this user is **Wolf**.\n"
            if (user.id == OWNER_ID or user.id in DEV_USERS or user.id in DRAGONS or user.id in DEMONS or user.id in TIGERS or user.id in WOLVES):
                caption += "\n\n〄 𝗥𝗮𝗻𝗸: "
                if user.id == OWNER_ID:
                    caption += "**CREATOR**"
                elif user.id in DEV_USERS:
                    caption += "**DEVELOPER**"
                elif user.id in DRAGONS:
                    caption += "**DRAGON**"
                elif user.id in DEMONS:
                    caption += "**DEMON**"
                elif user.id in TIGERS:
                    caption += "**TIGER**"
                elif user.id in WOLVES:
                    caption += "**WOLF**"
                caption += "\n"
            await message.reply_photo(photo=image_path, caption=caption, parse_mode=ParseMode.MARKDOWN)
            os.remove(image_path)
    except Exception as e:
        print(e)
