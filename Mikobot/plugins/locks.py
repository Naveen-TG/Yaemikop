from telegram import (
    Update,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MessageEntity,
)
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.error import TelegramError, BadRequest
from alphabet_detector import AlphabetDetector
from Itachi import application, LOGGER
from Itachi.modules.funcs.decorators import check_admin, user_not_admin

ACTIVE_LOCKS = {}
LOCK_SEL = {}
UNL_SEL = {}
ad = AlphabetDetector()

VALID = {
    "can_send_messages",
    "can_send_polls",
    "can_add_web_page_previews",
    "can_change_info",
    "can_invite_users",
    "can_pin_messages",
    "can_manage_topics",
    "can_send_audios",
    "can_send_documents",
    "can_send_photos",
    "can_send_videos",
    "can_send_video_notes",
    "can_send_voice_notes",
}
vf = lambda d: {k: v for k, v in d.items() if k in VALID}

PERM = {
    "text":   {"can_send_messages": False},
    "poll":   {"can_send_polls": False},
    "prev":   {"can_add_web_page_previews": False},
    "info":   {"can_change_info": False},
    "invite": {"can_invite_users": False},
    "pin":    {"can_pin_messages": False},
    "topic":  {"can_manage_topics": False},
    "audio":  {"can_send_audios": False},
    "doc":    {"can_send_documents": False},
    "photo":  {"can_send_photos": False},
    "video":  {"can_send_videos": False},
    "vnote":  {"can_send_video_notes": False},
    "voice":  {"can_send_voice_notes": False},
}

FILT = {
    "audio":   filters.AUDIO,
    "voice":   filters.VOICE,
    "document":filters.Document.ALL,
    "video":   filters.VIDEO,
    "contact": filters.CONTACT,
    "photo":   filters.PHOTO,
    "url":     filters.Entity(MessageEntity.URL)|filters.CaptionEntity(MessageEntity.URL),
    "bots":    filters.StatusUpdate.NEW_CHAT_MEMBERS,
    "forward": filters.FORWARDED,
    "game":    filters.GAME,
    "location":filters.LOCATION,
    "egame":   filters.Dice.ALL,
    "rtl":     "rtl",
    "button":  "button",
    "inline":  "inline",
    "phone":   filters.Entity(MessageEntity.PHONE_NUMBER)|filters.CaptionEntity(MessageEntity.PHONE_NUMBER),
    "command": filters.COMMAND,
    "email":   filters.Entity(MessageEntity.EMAIL)|filters.CaptionEntity(MessageEntity.EMAIL),
    "anonch":  "anonchannel",
    "fwdch":   "forwardchannel",
    "fwdbot":  "forwardbot",
    "videon":  filters.VIDEO_NOTE,
    "emojic":  filters.Entity(MessageEntity.CUSTOM_EMOJI)|filters.CaptionEntity(MessageEntity.CUSTOM_EMOJI),
    "stkpre":  filters.Sticker.PREMIUM,
    "stkana":  filters.Sticker.ANIMATED,
}

ALL = sorted(PERM) + sorted(FILT)

def mk_markup(picked: set[str], uid: int, tag: str):
    btns=[]
    for k in ALL:
        label = k.upper().ljust(9) + ("✅" if k in picked else "")
        btns.append(InlineKeyboardButton(label, callback_data=f"{tag}_tg_{k}|{uid}"))
    rows=[btns[i:i+3] for i in range(0,len(btns),3)]
    rows.append([InlineKeyboardButton("✅ APPLY", callback_data=f"{tag}_ap|{uid}")])
    return InlineKeyboardMarkup(rows)

@check_admin(permission="can_change_info", is_both=True)
async def lock_cmd(upd: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat, uid = upd.effective_chat.id, upd.effective_user.id
    if ctx.args and ctx.args[0].lower()!="custom":
        await lock_single(chat, ctx.args[0].lower(), upd, ctx); return
    LOCK_SEL[(chat,uid)] = set()
    await upd.message.reply_text("Pick to *lock*:", parse_mode=ParseMode.MARKDOWN,
                                 reply_markup=mk_markup(set(), uid, "lk"))

@check_admin(permission="can_change_info", is_both=True)
async def unlock_cmd(upd: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat, uid = upd.effective_chat.id, upd.effective_user.id
    if ctx.args and ctx.args[0].lower()!="custom":
        await unlock_single(chat, ctx.args[0].lower(), upd, ctx); return
    UNL_SEL[(chat,uid)] = set()
    await upd.message.reply_text("Pick to *unlock*:", parse_mode=ParseMode.MARKDOWN,
                                 reply_markup=mk_markup(set(), uid, "ul"))

async def lock_single(chat_id, key, upd, ctx):
    perms=(await ctx.bot.get_chat(chat_id)).permissions.to_dict()
    if key=="all":
        for p in PERM: perms.update(PERM[p])
        ACTIVE_LOCKS[chat_id]=set(FILT)
    elif key in PERM:
        perms.update(PERM[key])
    elif key in FILT:
        ACTIVE_LOCKS.setdefault(chat_id,set()).add(key)
    await ctx.bot.set_chat_permissions(chat_id, ChatPermissions(**vf(perms)))
    await upd.message.reply_text(f"✅ Locked *{key}*", parse_mode=ParseMode.MARKDOWN)

async def unlock_single(chat_id, key, upd, ctx):
    perms=(await ctx.bot.get_chat(chat_id)).permissions.to_dict()
    if key=="all":
        for p in PERM:
            for f in PERM[p]: perms[f]=True
        ACTIVE_LOCKS[chat_id]=set()
    elif key in PERM:
        for f in PERM[key]: perms[f]=True
    elif key in FILT:
        ACTIVE_LOCKS.setdefault(chat_id,set()).discard(key)
    await ctx.bot.set_chat_permissions(chat_id, ChatPermissions(**vf(perms)))
    await upd.message.reply_text(f"✅ Unlocked *{key}*", parse_mode=ParseMode.MARKDOWN)

async def cb_toggle(upd:Update, ctx:ContextTypes.DEFAULT_TYPE):
    q=upd.callback_query; data,uid=q.data.split("|")
    tag,_,key=data.partition("_tg_"); uid=int(uid)
    if q.from_user.id!=uid: return await q.answer("Not yours",show_alert=True)
    store=LOCK_SEL if tag=="lk" else UNL_SEL
    pick=store.setdefault((q.message.chat.id,uid),set())
    pick.symmetric_difference_update([key])
    await q.edit_message_reply_markup(reply_markup=mk_markup(pick,uid,tag))

async def cb_apply(upd:Update, ctx:ContextTypes.DEFAULT_TYPE):
    q=upd.callback_query; tag="lk" if q.data.startswith("lk") else "ul"
    uid=int(q.data.split("|")[1])
    if q.from_user.id!=uid: return await q.answer("Not yours",show_alert=True)
    store=LOCK_SEL if tag=="lk" else UNL_SEL
    keys=store.pop((q.message.chat.id,uid),set()); chat=q.message.chat.id
    perms=(await ctx.bot.get_chat(chat)).permissions.to_dict()
    for k in keys:
        if k in PERM:
            if tag=="lk": perms.update(PERM[k])
            else: perms.update({f:True for f in PERM[k]})
        elif k in FILT:
            if tag=="lk": ACTIVE_LOCKS.setdefault(chat,set()).add(k)
            else: ACTIVE_LOCKS.setdefault(chat,set()).discard(k)
    await ctx.bot.set_chat_permissions(chat, ChatPermissions(**vf(perms)))
    await q.edit_message_text("✅ Done")

@check_admin(permission="can_change_info", is_both=True)
async def status_cmd(upd:Update, ctx:ContextTypes.DEFAULT_TYPE):
    chat=upd.effective_chat.id
    perms=(await ctx.bot.get_chat(chat)).permissions.to_dict()
    act=ACTIVE_LOCKS.get(chat,set())
    out=["*LOCK STATUS:*",""]
    for k in ALL:
        ok=(all(perms.get(f,True) for f in PERM[k]) if k in PERM else k not in act)
        out.append(f"{k.upper():<10} {'✅' if ok else '❌'}")
    await upd.message.reply_text("\n".join(out), parse_mode=ParseMode.MARKDOWN)

@user_not_admin
@check_admin(is_bot=True)
async def del_blocked(upd:Update, ctx:ContextTypes.DEFAULT_TYPE):
    chat=upd.effective_chat.id; msg=upd.effective_message
    for k in ACTIVE_LOCKS.get(chat,set()):
        try:
            if k=="rtl":
                t=msg.text or msg.caption
                if t and "ARABIC" in ad.detect_alphabet(t): return await msg.delete()
            if k=="inline" and msg.via_bot: return await msg.delete()
            if k=="button" and msg.reply_markup and msg.reply_markup.inline_keyboard: return await msg.delete()
            if k in FILT and isinstance(FILT[k],filters.BaseFilter) and FILT[k].check_update(upd):
                return await msg.delete()
        except BadRequest: pass

application.add_handler(CommandHandler("lock", lock_cmd))
application.add_handler(CommandHandler("unlock", unlock_cmd))
application.add_handler(CommandHandler("locks", status_cmd))
application.add_handler(CallbackQueryHandler(cb_toggle, pattern=r"^(lk|ul)_toggle_"))
application.add_handler(CallbackQueryHandler(cb_apply, pattern=r"^(lk|ul)_ap"))
application.add_handler(MessageHandler(filters.ALL & filters.ChatType.GROUPS, del_blocked), group=1)
