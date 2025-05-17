from telegram import (
    Update,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MessageEntity,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,        # only needed if you build the app here
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.error import TelegramError, BadRequest
from alphabet_detector import AlphabetDetector
from Itachi import application            # your global Application object
from Itachi.modules.funcs.decorators import check_admin, user_not_admin

ACTIVE_LOCKS: dict[int, set[str]] = {}
LOCK_SEL, UNL_SEL = {}, {}
ad = AlphabetDetector()

VALID = {
    "can_send_messages", "can_send_polls", "can_add_web_page_previews",
    "can_change_info", "can_invite_users", "can_pin_messages",
    "can_manage_topics", "can_send_audios", "can_send_documents",
    "can_send_photos", "can_send_videos", "can_send_video_notes",
    "can_send_voice_notes",
}
vf = lambda d: {k: v for k, v in d.items() if k in VALID}

PERM = {
    "text":  {"can_send_messages": False},
    "poll":  {"can_send_polls": False},
    "prev":  {"can_add_web_page_previews": False},
    "info":  {"can_change_info": False},
    "invite":{"can_invite_users": False},
    "pin":   {"can_pin_messages": False},
    "topic": {"can_manage_topics": False},
    "audio": {"can_send_audios": False},
    "doc":   {"can_send_documents": False},
    "photo": {"can_send_photos": False},
    "video": {"can_send_videos": False},
    "vnote": {"can_send_video_notes": False},
    "voice": {"can_send_voice_notes": False},
}

FILT = {
    "audio":      filters.AUDIO,
    "voice":      filters.VOICE,
    "document":   filters.Document.ALL,
    "video":      filters.VIDEO,
    "contact":    filters.CONTACT,
    "photo":      filters.PHOTO,
    "gif":        filters.ANIMATION,           # <-- PTB v22 constant
    "url":        filters.Entity(MessageEntity.URL) | filters.CaptionEntity(MessageEntity.URL),
    "bots":       filters.StatusUpdate.NEW_CHAT_MEMBERS,
    "forward":    filters.FORWARDED,
    "game":       filters.GAME,
    "location":   filters.LOCATION,
    "egame":      filters.Dice.ALL,
    "rtl":        "rtl",
    "button":     "button",
    "inline":     "inline",
    "phone":      filters.Entity(MessageEntity.PHONE_NUMBER) | filters.CaptionEntity(MessageEntity.PHONE_NUMBER),
    "command":    filters.COMMAND,
    "email":      filters.Entity(MessageEntity.EMAIL) | filters.CaptionEntity(MessageEntity.EMAIL),
    "anonch":     "anonchannel",
    "fwdch":      "forwardchannel",
    "fwdbot":     "forwardbot",
    "videon":     filters.VIDEO_NOTE,
    "emojic":     filters.Entity(MessageEntity.CUSTOM_EMOJI) | filters.CaptionEntity(MessageEntity.CUSTOM_EMOJI),
    "sticker":    filters.Sticker.ALL,
    "stkpre":     filters.Sticker.PREMIUM,
    "stkana":     filters.Sticker.ANIMATED,
}

ALL = sorted(PERM) + sorted(FILT)

def ui(picked:set[str], uid:int, tag:str)->InlineKeyboardMarkup:
    btn=[]
    for k in ALL:
        lab=k.upper().ljust(9)+("✅" if k in picked else "")
        btn.append(InlineKeyboardButton(lab, callback_data=f"{tag}_tg_{k}|{uid}"))
    rows=[btn[i:i+3] for i in range(0,len(btn),3)]
    rows.append([InlineKeyboardButton("✅ APPLY", callback_data=f"{tag}_ap|{uid}")])
    return InlineKeyboardMarkup(rows)

@check_admin(permission="can_change_info", is_both=True)
async def lock_cmd(u:Update,c:ContextTypes.DEFAULT_TYPE):
    chat,uid=u.effective_chat.id,u.effective_user.id
    if c.args and c.args[0].lower()!="custom":
        await lock_one(chat,c.args[0].lower(),u,c); return
    LOCK_SEL[(chat,uid)]=set()
    await u.message.reply_text("Pick to *lock*:", parse_mode=ParseMode.MARKDOWN,
                               reply_markup=ui(set(),uid,"lk"))

@check_admin(permission="can_change_info", is_both=True)
async def unlock_cmd(u:Update,c:ContextTypes.DEFAULT_TYPE):
    chat,uid=u.effective_chat.id,u.effective_user.id
    if c.args and c.args[0].lower()!="custom":
        await unlock_one(chat,c.args[0].lower(),u,c); return
    UNL_SEL[(chat,uid)]=set()
    await u.message.reply_text("Pick to *unlock*:", parse_mode=ParseMode.MARKDOWN,
                               reply_markup=ui(set(),uid,"ul"))

async def lock_one(chat:int,key:str,u:Update,c:ContextTypes.DEFAULT_TYPE):
    perms=(await c.bot.get_chat(chat)).permissions.to_dict()
    if key=="all":
        for p in PERM: perms.update(PERM[p])
        ACTIVE_LOCKS[chat]=set(FILT)
    elif key in PERM: perms.update(PERM[key])
    elif key in FILT: ACTIVE_LOCKS.setdefault(chat,set()).add(key)
    await c.bot.set_chat_permissions(chat, ChatPermissions(**vf(perms)))
    await u.message.reply_text(f"✅ Locked *{key}*", parse_mode=ParseMode.MARKDOWN)

async def unlock_one(chat:int,key:str,u:Update,c:ContextTypes.DEFAULT_TYPE):
    perms=(await c.bot.get_chat(chat)).permissions.to_dict()
    if key=="all":
        for p in PERM: perms.update({f:True for f in PERM[p]})
        ACTIVE_LOCKS[chat]=set()
    elif key in PERM:
        for f in PERM[key]: perms[f]=True
    elif key in FILT:
        ACTIVE_LOCKS.setdefault(chat,set()).discard(key)
    await c.bot.set_chat_permissions(chat, ChatPermissions(**vf(perms)))
    await u.message.reply_text(f"✅ Unlocked *{key}*", parse_mode=ParseMode.MARKDOWN)

async def cb_toggle(u:Update,c:ContextTypes.DEFAULT_TYPE):
    q=u.callback_query; data,uid=q.data.split("|")
    tag,_,key=data.partition("_tg_"); uid=int(uid)
    if q.from_user.id!=uid: return await q.answer("Not yours",show_alert=True)
    store=LOCK_SEL if tag=="lk" else UNL_SEL
    sel=store.setdefault((q.message.chat.id,uid),set())
    sel.symmetric_difference_update([key])
    await q.edit_message_reply_markup(reply_markup=ui(sel,uid,tag))

async def cb_apply(u:Update,c:ContextTypes.DEFAULT_TYPE):
    q=u.callback_query; tag="lk" if q.data.startswith("lk") else "ul"
    uid=int(q.data.split("|")[1])
    if q.from_user.id!=uid: return await q.answer("Not yours",show_alert=True)
    store=LOCK_SEL if tag=="lk" else UNL_SEL
    picked=store.pop((q.message.chat.id,uid),set())
    chat=q.message.chat.id
    perms=(await c.bot.get_chat(chat)).permissions.to_dict()
    for k in picked:
        if k in PERM:
            perms.update(PERM[k]) if tag=="lk" else perms.update({f:True for f in PERM[k]})
        elif k in FILT:
            ACTIVE_LOCKS.setdefault(chat,set()).add(k) if tag=="lk" else ACTIVE_LOCKS.setdefault(chat,set()).discard(k)
    await c.bot.set_chat_permissions(chat, ChatPermissions(**vf(perms)))
    await q.edit_message_text("✅ Done")

@check_admin(permission="can_change_info", is_both=True)
async def locks_status(u:Update,c:ContextTypes.DEFAULT_TYPE):
    chat=u.effective_chat.id
    perms=(await c.bot.get_chat(chat)).permissions.to_dict()
    act=ACTIVE_LOCKS.get(chat,set())
    txt=["*LOCK STATUS:*",""]
    for k in ALL:
        good=(all(perms.get(f,True) for f in PERM[k]) if k in PERM else k not in act)
        txt.append(f"{k.upper():<9} {'✅' if good else '❌'}")
    await u.message.reply_text("\n".join(txt), parse_mode=ParseMode.MARKDOWN)

@user_not_admin
@check_admin(is_bot=True)
async def del_blocked(u:Update,c:ContextTypes.DEFAULT_TYPE):
    chat=u.effective_chat.id; msg=u.effective_message
    for k in ACTIVE_LOCKS.get(chat,set()):
        try:
            if k=="rtl" and (t:=msg.text or msg.caption) and "ARABIC" in ad.detect_alphabet(t):
                return await msg.delete()
            if k=="inline" and msg.via_bot: return await msg.delete()
            if k=="button" and msg.reply_markup and msg.reply_markup.inline_keyboard: return await msg.delete()
            if k in FILT and isinstance(FILT[k],filters.BaseFilter) and FILT[k].check_update(u):
                return await msg.delete()
        except BadRequest: pass

application.add_handler(CommandHandler("lock",    lock_cmd))
application.add_handler(CommandHandler("unlock",  unlock_cmd))
application.add_handler(CommandHandler("locks",   locks_status))
application.add_handler(CallbackQueryHandler(cb_toggle, pattern=r"^(lk|ul)_tg_"))
application.add_handler(CallbackQueryHandler(cb_apply,  pattern=r"^(lk|ul)_ap"))
application.add_handler(MessageHandler(filters.ALL & filters.ChatType.GROUPS, del_blocked), group=1)

