from pyrogram import filters
from pyrogram.enums import ParseMode
from variables import Config
from Mikobot import app


# Define a handler for the /bug command
@app.on_message(filters.command("bug", prefixes="/"))
async def bug_command_handler(client, message):
    # Check if the command is a reply
    if message.reply_to_message:
        # Get the message being replied to
        replied_message = message.reply_to_message

        # Extract message content
        content = replied_message.text or replied_message.caption or "No text content."

        # Check if there is media content
        media_type = (
            "**Media content included**"
            if replied_message.photo
            or replied_message.document
            or replied_message.video
            or replied_message.audio
            or replied_message.animation
            else "**No media content included**"
        )

        # Prepare the report message with message link and media content info
        report_message = (
            f"**Bug reported by @{message.from_user.username}:**\n\n"
            f"{content}\n\n"
            f"{media_type}\n\n"
            f"**Message Link:** {replied_message.link}"
        )

        # Send the report message
        await client.send_message(
            Config.SUPPORT_ID, report_message, parse_mode=ParseMode.MARKDOWN
        )
    else:
        # If not a reply, send a message to reply with /bug command to report a bug
        await client.send_message(
            message.chat.id,
            "To report a bug, please reply to the message with **/bug** command.",
            parse_mode=ParseMode.MARKDOWN,
        )
