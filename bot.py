import telebot
import random
import json
import os
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get("BOT_TOKEN").strip()

INVITE_LINKS = [
    "https://t.me/+Iv-zATHGpRgzMWE0",
    "https://t.me/+hxZ4s8z11-xjODY0",
    "https://t.me/+YrXJzzRL3CJkZGFk"
]

SHORT_LINKS = [
    "https://shrinkme.click/HjpVb4",
    "https://shrinkme.click/TFNr",
    "https://shrinkme.click/7dlJNh",
    "https://shrinkme.click/aqio",
    "https://shrinkme.click/eT5dD",
    "https://shrinkme.click/QVq7ORA",
    "https://shrinkme.click/DIDgTgj",
    "https://shrinkme.click/knFsUK",
    "https://shrinkme.click/RB8A",
    "https://shrinkme.click/GLq1LvB",
    "https://shrinkme.click/QZmEvz",
    "https://shrinkme.click/PFozE",
    "https://shrinkme.click/DYK4sCoZ",
    "https://shrinkme.click/JehWnx",
    "https://shrinkme.click/VyGwD0",
    "https://shrinkme.click/0QyuKRxG",
    "https://shrinkme.click/KFof1MLu",
    "https://shrinkme.click/RM4lYp",
    "https://shrinkme.click/H5mXYrOx",
    "https://shrinkme.click/U4K1Yr"
]

TIMEBUCKS_REF_LINK = "https://timebucks.com/?refID=229160569"
PEERPURPSE_CODE = "360366"

ADMIN_ID = None
user_data = {}
DATA_FILE = "data.json"
WITHDRAW_MIN = 3000

# This will hold the real chat IDs after the bot joins the channels.
CHAT_IDS = []

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        user_data = json.load(f)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f)

bot = telebot.TeleBot(TOKEN)

def join_and_get_chat_ids():
    """Make the bot join each private channel and store its chat ID."""
    global CHAT_IDS
    for link in INVITE_LINKS:
        try:
            # The bot joins the channel via the invite link.
            chat = bot.join_chat_by_invite_link(link)
            CHAT_IDS.append(chat.id)
        except Exception as e:
            print(f"Failed to join {link}: {e}")

# Call the join function once at startup.
join_and_get_chat_ids()

def check_channels(user_id):
    """Check if user is a member of all joined channels using stored chat IDs."""
    for chat_id in CHAT_IDS:
        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status in ['left', 'kicked', 'banned']:
                return False
        except:
            return False
    return True

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(msg):
    global ADMIN_ID
    if not ADMIN_ID:
        ADMIN_ID = msg.chat.id
    if not check_channels(msg.from_user.id):
        markup = InlineKeyboardMarkup()
        for ch in INVITE_LINKS:
            markup.add(InlineKeyboardButton("Join Channel", url=ch))
        bot.send_message(msg.chat.id, "🚫 You must join all our channels to use this bot.", reply_markup=markup)
        return
    bot.send_message(msg.chat.id, "✅ Welcome! Use /clicktask to earn ₦20 per click.\n/balance – check balance\n/withdraw – cash out at ₦" + str(WITHDRAW_MIN) + "\n/referral – get your referral link\n/jointask1 – earn bonus\n/jointask2 – earn bonus")

# ---------- CLICK TASK ----------
@bot.message_handler(commands=['clicktask'])
def clicktask(msg):
    if not check_channels(msg.from_user.id):
        markup = InlineKeyboardMarkup()
        for ch in INVITE_LINKS:
            markup.add(InlineKeyboardButton("Join Channel", url=ch))
        bot.send_message(msg.chat.id, "🚫 You must join all channels first.", reply_markup=markup)
        return

    link = random.choice(SHORT_LINKS)
    sent = bot.send_message(msg.chat.id, f"🔗 Click this link and wait 30 seconds for the page to load:\n\n{link}")
    def add_done_button():
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("DONE ✅", callback_data=f"done_{msg.from_user.id}_{link}"))
        try:
            bot.edit_message_text(
                f"🔗 Link: {link}\n\n⌛️ Press DONE after you have seen the page.",
                chat_id=msg.chat.id,
                message_id=sent.message_id,
                reply_markup=markup
            )
        except:
            pass
    threading.Timer(30, add_done_button).start()

@bot.callback_query_handler(func=lambda call: call.data.startswith('done_'))
def done_callback(call):
    uid = str(call.from_user.id)
    if random.random() < 0.5:
        bot.answer_callback_query(call.id, "❌ This link did not count. Try another.")
        bot.edit_message_text("❌ Link not counted. Try /clicktask again.", call.message.chat.id, call.message.message_id)
        return

    if uid not in user_data:
        user_data[uid] = {"balance": 0, "clicks": 0, "referrer": None, "ref_credited": False}
    user_data[uid]["balance"] += 20
    user_data[uid]["clicks"] += 1

    if user_data[uid].get("referrer") and not user_data[uid].get("ref_credited"):
        if user_data[uid]["clicks"] >= 10:
            ref_uid = user_data[uid]["referrer"]
            if ref_uid in user_data:
                user_data[ref_uid]["balance"] += 100
                save_data()
                user_data[uid]["ref_credited"] = True
                bot.send_message(int(ref_uid), "🎉 Your referral completed 10 click tasks! ₦100 added.")
    save_data()

    bot.answer_callback_query(call.id, f"₦20 added! Balance: ₦{user_data[uid]['balance']}")
    bot.edit_message_text(f"✅ ₦20 added! Your balance: ₦{user_data[uid]['balance']}\nUse /clicktask for another link.", call.message.chat.id, call.message.message_id)

# ---------- BALANCE ----------
@bot.message_handler(commands=['balance'])
def balance(msg):
    uid = str(msg.from_user.id)
    bal = user_data.get(uid, {}).get("balance", 0)
    bot.send_message(msg.chat.id, f"💰 Your balance: ₦{bal}")

# ---------- WITHDRAWAL ----------
@bot.message_handler(commands=['withdraw'])
def withdraw(msg):
    uid = str(msg.from_user.id)
    bal = user_data.get(uid, {}).get("balance", 0)
    if bal < WITHDRAW_MIN:
        bot.send_message(msg.chat.id, f"🏧 Minimum withdrawal is ₦{WITHDRAW_MIN}. Your balance: ₦{bal}")
        return
    bot.send_message(msg.chat.id, "📝 To withdraw, please send your **bank name** and **account number**. We process payouts every Friday.")
    if ADMIN_ID:
        bot.forward_message(ADMIN_ID, msg.chat.id, msg.message_id)

# ---------- REFERRAL ----------
@bot.message_handler(commands=['referral'])
def referral(msg):
    bot_name = bot.get_me().username
    bot.send_message(msg.chat.id, f"🔗 Your referral link:\nhttps://t.me/{bot_name}?start=ref_{msg.from_user.id}\n\nShare it. When someone joins and completes 10 click tasks, you get ₦100.")

@bot.message_handler(commands=['start'], func=lambda msg: msg.text and msg.text.startswith('/start ref_'))
def start_ref(msg):
    ref_id = msg.text.split()[1].replace('ref_', '')
    uid = str(msg.from_user.id)
    if uid not in user_data:
        user_data[uid] = {"balance": 0, "clicks": 0, "referrer": ref_id, "ref_credited": False}
    else:
        user_data[uid]["referrer"] = ref_id
    save_data()
    start(msg)

# ---------- EXTRA TASK 1 ----------
@bot.message_handler(commands=['jointask1'])
def jointask1(msg):
    if not check_channels(msg.from_user.id):
        return
    uid = str(msg.from_user.id)
    if uid not in user_data:
        user_data[uid] = {"balance": 0, "clicks": 0, "referrer": None, "ref_credited": False}
    bot.send_message(msg.chat.id,
        f"📌 **Task: Sign up on TimeBucks**\n\n"
        f"1. Click this link and sign up **using only your Google account**:\n{TIMEBUCKS_REF_LINK}\n"
        f"2. After successful registration, perform 1 task and press the button below to claim ₦100.\n\n"
        f"⚠️ You must use Google sign‑up and perform at least one task, otherwise the reward won't be credited.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("I've signed up ✅", callback_data=f"timebucks_{uid}"))
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('timebucks_'))
def timebucks_done(call):
    uid = str(call.from_user.id)
    if uid not in user_data:
        user_data[uid] = {"balance": 0, "clicks": 0, "referrer": None, "ref_credited": False}
    user_data[uid]["balance"] += 200
    save_data()
    bot.answer_callback_query(call.id, "₦200 added!")
    bot.edit_message_text("✅ ₦200 added to your balance. Check /balance.", call.message.chat.id, call.message.message_id)

# ---------- EXTRA TASK 2 ----------
@bot.message_handler(commands=['jointask2'])
def jointask2(msg):
    if not check_channels(msg.from_user.id):
        return
    uid = str(msg.from_user.id)
    if uid not in user_data:
        user_data[uid] = {"balance": 0, "clicks": 0, "referrer": None, "ref_credited": False}
    bot.send_message(msg.chat.id,
        f"📌 **Task: Sign up on PeerPurple**\n\n"
        f"1. Use this referral code during signup: **{PEERPURPSE_CODE}**\n"
        f"2. Complete your **KYC verification** (ID upload).\n"
        f"3. Once done, press the button below to claim ₦150.\n\n"
        f"⚠️ You must complete KYC to qualify.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("I've completed KYC ✅", callback_data=f"peerpurple_{uid}"))
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('peerpurple_'))
def peerpurple_done(call):
    uid = str(call.from_user.id)
    if uid not in user_data:
        user_data[uid] = {"balance": 0, "clicks": 0, "referrer": None, "ref_credited": False}
    user_data[uid]["balance"] += 150
    save_data()
    bot.answer_callback_query(call.id, "₦150 added!")
    bot.edit_message_text("✅ ₦150 added. Check /balance.", call.message.chat.id, call.message.message_id)

print("Bot running 24/7...")
bot.polling(none_stop=True)
