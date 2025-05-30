import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import UserNotParticipant, FloodWait
from database import add_user, add_group, all_users, all_groups, remove_user
from configs import cfg

app = Client(
    "approver",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

# Handle new chat join requests
@app.on_chat_join_request(filters.group | filters.channel)
async def approve(client, message: Message):
    chat = message.chat
    user = message.from_user
    try:
        add_group(chat.id)
        await client.approve_chat_join_request(chat.id, user.id)
        await client.send_message(user.id, f"**Hello {user.mention}!\nWelcome to {chat.title}\n\n__Powered By: @Acecricketpro__**")
        add_user(user.id)
    except UserNotParticipant:
        invite_link = await client.create_chat_invite_link(chat.id)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🍿 Join Update Channel 🍿", url=invite_link.invite_link),
             InlineKeyboardButton("🍀 Check Again 🍀", callback_data="chk")]
        ])
        await message.reply_text(
            f"**⚠️ Access Denied! ⚠️\n\nPlease join my update channel to use me. If you've joined, click 'Check Again'.**",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Error: {e}")

# Handle /start command
@app.on_message(filters.private & filters.command("start"))
async def start(client, message: Message):
    try:
        await client.get_chat_member(cfg.CHID, message.from_user.id)
    except UserNotParticipant:
        invite_link = await client.create_chat_invite_link(int(cfg.CHID))
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🍿 Join Update Channel 🍿", url=invite_link.invite_link),
             InlineKeyboardButton("🍀 Check Again 🍀", callback_data="chk")]
        ])
        await message.reply_text(
            f"**⚠️ Access Denied! ⚠️\n\nPlease join my update channel to use me. If you've joined, click 'Check Again'.**",
            reply_markup=keyboard
        )
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗯 Channel", url="https://t.me/+5BKtrpoVBTo2M2Y1"),
         InlineKeyboardButton("💬 Support", url="https://t.me/+5BKtrpoVBTo2M2Y1")]
    ])
    add_user(message.from_user.id)
    await message.reply_photo(
        "https://graph.org/file/d57d6f83abb6b8d0efb02.jpg",
        caption=f"**🦊 Hello {message.from_user.mention}!\nI'm an auto-approve bot.\n\nPowered By: @Acecricketpro**",
        reply_markup=keyboard
    )

# Handle callback query for checking subscription
@app.on_callback_query(filters.regex("chk"))
async def check_subscription(client, callback_query: CallbackQuery):
    try:
        await client.get_chat_member(cfg.CHID, callback_query.from_user.id)
    except UserNotParticipant:
        await callback_query.answer("⚠️ You are not joined to my channel. Please join to proceed.", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗯 Channel", url="https://t.me/+5BKtrpoVBTo2M2Y1"),
         InlineKeyboardButton("💬 Support", url="https://t.me/+5BKtrpoVBTo2M2Y1")]
    ])
    await callback_query.edit_message_text(
        f"**🦊 Hello {callback_query.from_user.mention}!\nI'm an auto-approve bot.\n\nPowered By: @Acecricketpro**",
        reply_markup=keyboard
    )

# Handle /users command for stats
@app.on_message(filters.command("users") & filters.user(cfg.SUDO))
async def dbtool(client, message: Message):
    xx = all_users()
    x = all_groups()
    tot = xx + x
    await message.reply_text(f"""
🍀 Chats Stats 🍀
🙋‍♂️ Users: `{xx}`
👥 Groups: `{x}`
🚧 Total users & groups: `{tot}`
""")

# Handle /bcast command for broadcasting messages
@app.on_message(filters.command("bcast") & filters.user(cfg.SUDO))
async def bcast(client, message: Message):
    allusers = users
    lel = await message.reply_text("`⚡️ Processing...`")
    success = 0
    failed = 0
    deactivated = 0
    blocked = 0
    for usrs in allusers.find():
        try:
            userid = usrs["user_id"]
            await message.reply_to_message.copy(int(userid))
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            await message.reply_to_message.copy(int(userid))
            success += 1
        except Exception as e:
            print(e)
            failed += 1

    await lel.edit(f"✅ Success: `{success}`\n❌ Failed: `{failed}`\n👾 Blocked: `{blocked}`\n👻 Deactivated: `{deactivated}`")

# Handle /fcast command for forwarding messages
@app.on_message(filters.command("fcast") & filters.user(cfg.SUDO))
async def fcast(client, message: Message):
    allusers = users
    lel = await message.reply_text("`⚡️ Processing...`")
    success = 0
    failed = 0
    deactivated = 0
    blocked = 0
    for usrs in allusers.find():
        try:
            userid = usrs["user_id"]
            await message.reply_to_message.forward(int(userid))
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            await message.reply_to_message.forward(int(userid))
            success += 1
        except Exception as e:
            print(e)
            failed += 1

    await lel.edit(f"✅ Success: `{success}`\n❌ Failed: `{failed}`\n👾 Blocked: `{blocked}`\n👻 Deactivated: `{deactivated}`")

print("Bot is running...")
app.run()
