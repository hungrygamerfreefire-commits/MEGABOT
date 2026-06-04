import os
import json
import random
import asyncio
import datetime
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)

# ══════════════════════════════════════════════
# CONFIG — apna token yahan daalo
# ══════════════════════════════════════════════
BOT_TOKEN = "8908268384:AAFraieu5ab8ApWR6dnlyJ59YBVJfkKOGk4"
DATA_FILE = "data.json"

# ══════════════════════════════════════════════
# DATA MANAGEMENT
# ══════════════════════════════════════════════
def load():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_user(data, uid):
    uid = str(uid)
    if uid not in data:
        data[uid] = {
            "tasks": [], "expenses": [], "reminders": [],
            "birthdays": [], "vault": {}, "mood_log": [],
            "fitness": [], "name": ""
        }
    return data[uid]

# ══════════════════════════════════════════════
# /start
# ══════════════════════════════════════════════
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load()
    u = get_user(data, user.id)
    u["name"] = user.first_name
    save(data)

    keyboard = [
        [InlineKeyboardButton("📋 Tasks", callback_data="menu_tasks"),
         InlineKeyboardButton("💰 Kharcha", callback_data="menu_expense")],
        [InlineKeyboardButton("🎮 Games", callback_data="menu_games"),
         InlineKeyboardButton("🎂 Birthdays", callback_data="menu_bday")],
        [InlineKeyboardButton("📱 Number Info", callback_data="menu_num"),
         InlineKeyboardButton("🔐 Vault", callback_data="menu_vault")],
        [InlineKeyboardButton("📊 My Stats", callback_data="menu_stats"),
         InlineKeyboardButton("😂 Fun", callback_data="menu_fun")],
        [InlineKeyboardButton("❓ Help", callback_data="menu_help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🌟 *Namaste {user.first_name}!*\n\n"
        "Main hoon *4Dreams MegaBot* — aapka All-in-One assistant!\n\n"
        "Niche se koi bhi feature choose karo ya command use karo 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ══════════════════════════════════════════════
# /help
# ══════════════════════════════════════════════
async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *MEGA BOT — COMMANDS LIST*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "*📋 TASK MANAGER*\n"
        "`/add <task>` — naya task add karo\n"
        "`/tasks` — sabhi tasks dekho\n"
        "`/done <number>` — task complete karo\n"
        "`/deltask <number>` — task hatao\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "*💰 EXPENSE TRACKER*\n"
        "`/kharcha <amount> <reason>` — kharcha add karo\n"
        "`/report` — is mahine ka hisaab\n"
        "`/delkharcha` — sab clear karo\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "*📱 NUMBER INFO*\n"
        "`/num +919876543210` — number ki detail\n"
        "Ya seedha number type karo!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "*🎂 BIRTHDAY REMINDER*\n"
        "`/bday add <naam> <DD> <Month>` — birthday save karo\n"
        "`/bday list` — sabhi birthdays\n"
        "`/bday del <number>` — hatao\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "*⏰ REMINDERS*\n"
        "`/remind <Xmin/Xhr> <message>` — reminder set karo\n"
        "Example: `/remind 30min Meeting hai`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "*🔐 SECRET VAULT*\n"
        "`/save <key> <value>` — kuch bhi save karo\n"
        "`/get <key>` — wapas lo\n"
        "`/vault` — sab keys dekho\n"
        "`/delvault <key>` — hatao\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "*🎮 GAMES*\n"
        "`/guess` — number guessing game\n"
        "`/quiz` — random quiz question\n"
        "`/rps <rock/paper/scissors>` — hath ka khel\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "*😂 FUN*\n"
        "`/joke` — ek mazedaar joke\n"
        "`/fact` — interesting fact\n"
        "`/quote` — motivational quote\n"
        "`/flip` — coin toss\n"
        "`/dice` — dice roll\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "*📊 STATS*\n"
        "`/stats` — aapka dashboard\n"
        "`/weather <city>` — mausam\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ══════════════════════════════════════════════
# TASK MANAGER
# ══════════════════════════════════════════════
async def add_task(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("❌ Usage: `/add task likhna hai`", parse_mode="Markdown")
        return
    task = " ".join(ctx.args)
    data = load()
    u = get_user(data, update.effective_user.id)
    u["tasks"].append({"text": task, "done": False, "date": str(datetime.date.today())})
    save(data)
    await update.message.reply_text(f"✅ Task add ho gaya!\n📌 *{task}*", parse_mode="Markdown")

async def list_tasks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load()
    u = get_user(data, update.effective_user.id)
    tasks = u["tasks"]
    if not tasks:
        await update.message.reply_text("📋 Koi task nahi hai! `/add` se add karo.", parse_mode="Markdown")
        return
    text = "📋 *AAPKI TASK LIST*\n\n"
    for i, t in enumerate(tasks, 1):
        icon = "✅" if t["done"] else "⏳"
        text += f"{icon} `{i}.` {t['text']}\n"
    pending = sum(1 for t in tasks if not t["done"])
    done = sum(1 for t in tasks if t["done"])
    text += f"\n📊 Total: {len(tasks)} | ⏳ Pending: {pending} | ✅ Done: {done}"
    await update.message.reply_text(text, parse_mode="Markdown")

async def done_task(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args or not ctx.args[0].isdigit():
        await update.message.reply_text("❌ Usage: `/done 1`", parse_mode="Markdown")
        return
    idx = int(ctx.args[0]) - 1
    data = load()
    u = get_user(data, update.effective_user.id)
    if 0 <= idx < len(u["tasks"]):
        u["tasks"][idx]["done"] = True
        save(data)
        await update.message.reply_text(f"🎉 Task complete!\n✅ *{u['tasks'][idx]['text']}*", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Galat number!")

async def del_task(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args or not ctx.args[0].isdigit():
        await update.message.reply_text("❌ Usage: `/deltask 1`", parse_mode="Markdown")
        return
    idx = int(ctx.args[0]) - 1
    data = load()
    u = get_user(data, update.effective_user.id)
    if 0 <= idx < len(u["tasks"]):
        removed = u["tasks"].pop(idx)
        save(data)
        await update.message.reply_text(f"🗑️ Task hata diya: *{removed['text']}*", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Galat number!")

# ══════════════════════════════════════════════
# EXPENSE TRACKER
# ══════════════════════════════════════════════
async def kharcha(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 2:
        await update.message.reply_text("❌ Usage: `/kharcha 200 khana`", parse_mode="Markdown")
        return
    try:
        amount = float(ctx.args[0])
    except:
        await update.message.reply_text("❌ Pehle amount likhna hai (number mein)")
        return
    reason = " ".join(ctx.args[1:])
    data = load()
    u = get_user(data, update.effective_user.id)
    u["expenses"].append({
        "amount": amount, "reason": reason,
        "date": str(datetime.date.today()),
        "month": datetime.date.today().strftime("%Y-%m")
    })
    save(data)
    total = sum(e["amount"] for e in u["expenses"] if e["month"] == datetime.date.today().strftime("%Y-%m"))
    await update.message.reply_text(
        f"💰 *Kharcha save!*\n\n"
        f"💸 Amount: ₹{amount:.0f}\n"
        f"📝 Kaam: {reason}\n"
        f"📅 Date: {datetime.date.today().strftime('%d %b %Y')}\n\n"
        f"📊 Is mahine ka total: *₹{total:.0f}*",
        parse_mode="Markdown"
    )

async def report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load()
    u = get_user(data, update.effective_user.id)
    month = datetime.date.today().strftime("%Y-%m")
    this_month = [e for e in u["expenses"] if e.get("month") == month]
    if not this_month:
        await update.message.reply_text("💰 Is mahine koi kharcha nahi hai!", parse_mode="Markdown")
        return
    total = sum(e["amount"] for e in this_month)
    text = f"📊 *IS MAHINE KA HISAAB*\n_{datetime.date.today().strftime('%B %Y')}_\n\n"
    for e in this_month[-10:]:
        text += f"• ₹{e['amount']:.0f} — {e['reason']} _{e['date']}_\n"
    text += f"\n💰 *TOTAL: ₹{total:.0f}*"
    await update.message.reply_text(text, parse_mode="Markdown")

# ══════════════════════════════════════════════
# NUMBER INFO
# ══════════════════════════════════════════════
COUNTRY_CODES = {
    "91": {"country": "🇮🇳 India", "operators": {
        "98": "Airtel", "97": "Airtel", "96": "Airtel",
        "99": "Vodafone/Vi", "95": "Vodafone/Vi",
        "70": "BSNL", "94": "BSNL",
        "62": "Jio", "63": "Jio", "64": "Jio", "65": "Jio",
        "66": "Jio", "67": "Jio", "68": "Jio", "69": "Jio",
        "72": "Airtel", "73": "Airtel", "74": "Airtel",
        "75": "Vodafone/Vi", "76": "Airtel",
        "77": "Airtel", "78": "Airtel", "79": "Vodafone/Vi",
        "80": "BSNL", "81": "Airtel", "82": "Airtel",
        "83": "Airtel", "84": "Vodafone/Vi", "85": "Jio",
        "86": "BSNL", "87": "Vodafone/Vi", "88": "Airtel",
        "89": "BSNL", "90": "Airtel", "91": "Airtel",
        "92": "Airtel", "93": "Vodafone/Vi",
    }},
    "1":  {"country": "🇺🇸 USA / Canada", "operators": {}},
    "44": {"country": "🇬🇧 United Kingdom", "operators": {}},
    "971":{"country": "🇦🇪 UAE", "operators": {}},
    "966":{"country": "🇸🇦 Saudi Arabia", "operators": {}},
    "92": {"country": "🇵🇰 Pakistan", "operators": {}},
    "880":{"country": "🇧🇩 Bangladesh", "operators": {}},
    "977":{"country": "🇳🇵 Nepal", "operators": {}},
    "94": {"country": "🇱🇰 Sri Lanka", "operators": {}},
    "86": {"country": "🇨🇳 China", "operators": {}},
    "81": {"country": "🇯🇵 Japan", "operators": {}},
    "49": {"country": "🇩🇪 Germany", "operators": {}},
    "33": {"country": "🇫🇷 France", "operators": {}},
    "7":  {"country": "🇷🇺 Russia", "operators": {}},
    "61": {"country": "🇦🇺 Australia", "operators": {}},
}

def get_number_info(raw):
    raw = re.sub(r'[\s\-\(\)]', '', raw)
    if raw.startswith('+'):
        raw = raw[1:]
    elif raw.startswith('00'):
        raw = raw[2:]

    country_code = None
    country_info = None

    for code_len in [3, 2, 1]:
        code = raw[:code_len]
        if code in COUNTRY_CODES:
            country_code = code
            country_info = COUNTRY_CODES[code]
            break

    if not country_code:
        return None

    local_number = raw[len(country_code):]

    if country_code == "91":
        if len(local_number) != 10:
            return {"valid": False, "reason": "Indian number 10 digits ka hona chahiye"}
        if not local_number[0] in "6789":
            return {"valid": False, "reason": "Indian mobile number 6/7/8/9 se shuru hota hai"}
        prefix2 = local_number[:2]
        operator = country_info["operators"].get(prefix2, "Unknown Operator")
        num_type = "Mobile"
        state_map = {
            "9": "North India region", "8": "West/Central India",
            "7": "South/East India", "6": "Pan India (Jio/new series)"
        }
        region = state_map.get(local_number[0], "India")
        return {
            "valid": True,
            "full": f"+{country_code}{local_number}",
            "country": country_info["country"],
            "country_code": f"+{country_code}",
            "local": local_number,
            "operator": operator,
            "type": num_type,
            "region": region,
            "digits": len(local_number)
        }
    else:
        return {
            "valid": True,
            "full": f"+{country_code}{local_number}",
            "country": country_info["country"],
            "country_code": f"+{country_code}",
            "local": local_number,
            "operator": "N/A",
            "type": "International",
            "region": country_info["country"],
            "digits": len(local_number)
        }

async def num_info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "📱 *NUMBER INFO*\n\nUsage: `/num +919876543210`\nYa seedha number type karo!",
            parse_mode="Markdown"
        )
        return
    raw = ctx.args[0]
    info = get_number_info(raw)
    if not info:
        await update.message.reply_text("❌ Country code nahi pehchana. `+` ke saath poora number likhna!", parse_mode="Markdown")
        return
    if not info.get("valid"):
        await update.message.reply_text(f"❌ *Invalid Number*\nReason: {info.get('reason', 'Unknown')}", parse_mode="Markdown")
        return

    text = (
        f"📱 *NUMBER DETAILS*\n\n"
        f"🔢 Number: `{info['full']}`\n"
        f"✅ Status: *Valid*\n"
        f"{'━'*25}\n"
        f"🌍 Country: {info['country']}\n"
        f"📡 Country Code: {info['country_code']}\n"
        f"📶 Operator: *{info['operator']}*\n"
        f"📞 Type: {info['type']}\n"
        f"📍 Region: {info['region']}\n"
        f"🔢 Local Digits: {info['digits']}\n"
        f"{'━'*25}\n"
        f"🕐 Checked: {datetime.datetime.now().strftime('%d %b %Y, %I:%M %p')}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ══════════════════════════════════════════════
# BIRTHDAY REMINDER
# ══════════════════════════════════════════════
MONTHS = {
    "jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
    "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12,
    "january":1,"february":2,"march":3,"april":4,"june":6,
    "july":7,"august":8,"september":9,"october":10,"november":11,"december":12,
    "1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,"11":11,"12":12
}

async def bday(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "🎂 *BIRTHDAY REMINDER*\n\n"
            "`/bday add Rahul 15 June` — save karo\n"
            "`/bday list` — sabhi dekho\n"
            "`/bday del 1` — hatao",
            parse_mode="Markdown"
        )
        return

    action = ctx.args[0].lower()
    data = load()
    u = get_user(data, update.effective_user.id)

    if action == "add":
        if len(ctx.args) < 4:
            await update.message.reply_text("❌ Usage: `/bday add Naam DD Month`\nExample: `/bday add Rahul 15 June`", parse_mode="Markdown")
            return
        naam = ctx.args[1]
        day = ctx.args[2]
        month_raw = ctx.args[3].lower()
        month_num = MONTHS.get(month_raw)
        if not month_num or not day.isdigit():
            await update.message.reply_text("❌ Date sahi nahi hai! Example: `/bday add Rahul 15 June`", parse_mode="Markdown")
            return
        u["birthdays"].append({"naam": naam, "day": int(day), "month": month_num})
        save(data)
        month_names = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        await update.message.reply_text(
            f"🎂 Birthday save!\n\n"
            f"👤 Naam: *{naam}*\n"
            f"📅 Date: *{day} {month_names[month_num]}*\n\n"
            f"Main aapko birthday pe remind karunga! 🎉",
            parse_mode="Markdown"
        )

    elif action == "list":
        bdays = u.get("birthdays", [])
        if not bdays:
            await update.message.reply_text("🎂 Koi birthday save nahi hai!", parse_mode="Markdown")
            return
        today = datetime.date.today()
        month_names = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        text = "🎂 *BIRTHDAY LIST*\n\n"
        for i, b in enumerate(bdays, 1):
            try:
                bdate = datetime.date(today.year, b["month"], b["day"])
                if bdate < today:
                    bdate = datetime.date(today.year + 1, b["month"], b["day"])
                days_left = (bdate - today).days
                if days_left == 0:
                    countdown = "🎉 *AAJ HAI!*"
                elif days_left == 1:
                    countdown = "⚡ *Kal hai!*"
                else:
                    countdown = f"⏳ {days_left} din baad"
            except:
                countdown = "📅"
            text += f"`{i}.` 🎂 *{b['naam']}* — {b['day']} {month_names[b['month']]} | {countdown}\n"
        await update.message.reply_text(text, parse_mode="Markdown")

    elif action == "del":
        if len(ctx.args) < 2 or not ctx.args[1].isdigit():
            await update.message.reply_text("❌ Usage: `/bday del 1`", parse_mode="Markdown")
            return
        idx = int(ctx.args[1]) - 1
        if 0 <= idx < len(u["birthdays"]):
            removed = u["birthdays"].pop(idx)
            save(data)
            await update.message.reply_text(f"🗑️ Hata diya: *{removed['naam']}* ka birthday", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Galat number!")

# ══════════════════════════════════════════════
# REMINDER
# ══════════════════════════════════════════════
async def remind(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 2:
        await update.message.reply_text(
            "⏰ *REMINDER*\n\nUsage:\n"
            "`/remind 30min Meeting hai`\n"
            "`/remind 2hr Lunch time`\n"
            "`/remind 5min Check karo`",
            parse_mode="Markdown"
        )
        return

    time_str = ctx.args[0].lower()
    message = " ".join(ctx.args[1:])
    seconds = 0

    if "hr" in time_str:
        try:
            seconds = int(re.sub(r'[^0-9]','', time_str)) * 3600
        except: pass
    elif "min" in time_str:
        try:
            seconds = int(re.sub(r'[^0-9]','', time_str)) * 60
        except: pass
    elif "sec" in time_str:
        try:
            seconds = int(re.sub(r'[^0-9]','', time_str))
        except: pass

    if seconds <= 0:
        await update.message.reply_text("❌ Time sahi nahi! Example: `30min`, `2hr`, `45sec`", parse_mode="Markdown")
        return

    if seconds > 86400:
        await update.message.reply_text("❌ Max 24 ghante ka reminder set kar sakte ho!", parse_mode="Markdown")
        return

    chat_id = update.effective_chat.id
    disp = f"{seconds//3600}hr {(seconds%3600)//60}min" if seconds >= 3600 else f"{seconds//60}min {seconds%60}sec" if seconds >= 60 else f"{seconds}sec"

    await update.message.reply_text(
        f"⏰ *Reminder set!*\n\n"
        f"💬 Message: _{message}_\n"
        f"⏱ Time: *{disp}* baad\n\n"
        f"Main remind karunga! ✅",
        parse_mode="Markdown"
    )

    async def send_reminder():
        await asyncio.sleep(seconds)
        await ctx.bot.send_message(
            chat_id=chat_id,
            text=f"⏰ *REMINDER!*\n\n🔔 {message}\n\n_Set kiya tha {disp} pehle_",
            parse_mode="Markdown"
        )

    asyncio.create_task(send_reminder())

# ══════════════════════════════════════════════
# SECRET VAULT
# ══════════════════════════════════════════════
async def vault_save(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 2:
        await update.message.reply_text("❌ Usage: `/save gmail password123`", parse_mode="Markdown")
        return
    key = ctx.args[0]
    value = " ".join(ctx.args[1:])
    data = load()
    u = get_user(data, update.effective_user.id)
    u["vault"][key] = {"value": value, "saved_at": str(datetime.datetime.now().strftime("%d %b %Y"))}
    save(data)
    await update.message.reply_text(f"🔐 *Vault mein save!*\n\n🔑 Key: `{key}`\n✅ Safely stored!", parse_mode="Markdown")

async def vault_get(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("❌ Usage: `/get gmail`", parse_mode="Markdown")
        return
    key = ctx.args[0]
    data = load()
    u = get_user(data, update.effective_user.id)
    item = u["vault"].get(key)
    if item:
        await update.message.reply_text(
            f"🔐 *VAULT ITEM*\n\n🔑 Key: `{key}`\n💎 Value: `{item['value']}`\n📅 Saved: {item['saved_at']}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(f"❌ `{key}` vault mein nahi mila!", parse_mode="Markdown")

async def vault_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load()
    u = get_user(data, update.effective_user.id)
    vault = u.get("vault", {})
    if not vault:
        await update.message.reply_text("🔐 Vault khali hai! `/save` se add karo.", parse_mode="Markdown")
        return
    text = "🔐 *VAULT KEYS*\n\n"
    for k, v in vault.items():
        text += f"🔑 `{k}` — saved {v['saved_at']}\n"
    text += "\n_`/get <key>` se value lo_"
    await update.message.reply_text(text, parse_mode="Markdown")

async def vault_del(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("❌ Usage: `/delvault gmail`", parse_mode="Markdown")
        return
    key = ctx.args[0]
    data = load()
    u = get_user(data, update.effective_user.id)
    if key in u["vault"]:
        del u["vault"][key]
        save(data)
        await update.message.reply_text(f"🗑️ `{key}` vault se hata diya!", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ `{key}` nahi mila!", parse_mode="Markdown")

# ══════════════════════════════════════════════
# GAMES
# ══════════════════════════════════════════════
game_state = {}

async def guess_game(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    num = random.randint(1, 100)
    game_state[uid] = {"type": "guess", "number": num, "attempts": 0}
    await update.message.reply_text(
        "🎮 *NUMBER GUESSING GAME*\n\n"
        "Maine 1 se 100 ke beech ek number socha hai!\n"
        "Tumhe usse guess karna hai! 🤔\n\n"
        "Seedha number type karo (jaise: `42`)",
        parse_mode="Markdown"
    )

QUIZ_QUESTIONS = [
    {"q": "India ki capital kya hai?", "a": "new delhi", "opts": ["Mumbai", "New Delhi", "Kolkata", "Chennai"]},
    {"q": "1 + 1 = ?", "a": "2", "opts": ["1", "2", "3", "11"]},
    {"q": "Sabse bada planet kaun sa hai?", "a": "jupiter", "opts": ["Saturn", "Jupiter", "Mars", "Earth"]},
    {"q": "Water ka chemical formula kya hai?", "a": "h2o", "opts": ["CO2", "H2O", "O2", "NaCl"]},
    {"q": "India mein kitne states hain?", "a": "28", "opts": ["26", "27", "28", "29"]},
    {"q": "CPU ka full form kya hai?", "a": "central processing unit", "opts": ["Central Process Unit","Central Processing Unit","Computer Processing Unit","Core Processing Unit"]},
    {"q": "Sabse chhota planet kaun sa hai?", "a": "mercury", "opts": ["Mars", "Mercury", "Venus", "Pluto"]},
    {"q": "1 KB = kitne bytes?", "a": "1024", "opts": ["1000", "1024", "512", "2048"]},
]

async def quiz(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    q = random.choice(QUIZ_QUESTIONS)
    opts = q["opts"].copy()
    random.shuffle(opts)
    game_state[uid] = {"type": "quiz", "answer": q["a"]}
    keyboard = [[InlineKeyboardButton(o, callback_data=f"quiz_{o.lower()}")] for o in opts]
    await update.message.reply_text(
        f"🧠 *QUIZ TIME!*\n\n❓ {q['q']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def rps(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args or ctx.args[0].lower() not in ["rock","paper","scissors","stone","patthar","kaagaz","kainchi"]:
        await update.message.reply_text(
            "✊📄✂️ *ROCK PAPER SCISSORS*\n\nUsage:\n`/rps rock` ya `stone` ya `patthar`\n`/rps paper` ya `kaagaz`\n`/rps scissors` ya `kainchi`",
            parse_mode="Markdown"
        )
        return
    mapping = {"stone":"rock","patthar":"rock","kaagaz":"paper","kainchi":"scissors"}
    user_choice = ctx.args[0].lower()
    user_choice = mapping.get(user_choice, user_choice)
    bot_choice = random.choice(["rock","paper","scissors"])
    icons = {"rock":"✊","paper":"📄","scissors":"✂️"}
    wins = {"rock":"scissors","paper":"rock","scissors":"paper"}
    if user_choice == bot_choice:
        result = "🤝 *DRAW!* Barabar!"
    elif wins[user_choice] == bot_choice:
        result = "🎉 *TUM JEETE!* Badhai ho!"
    else:
        result = "😅 *BOT JEETA!* Agli baar try karo!"
    await update.message.reply_text(
        f"✊📄✂️ *ROCK PAPER SCISSORS*\n\n"
        f"Tumhara: {icons[user_choice]} *{user_choice.upper()}*\n"
        f"Mera:    {icons[bot_choice]} *{bot_choice.upper()}*\n\n"
        f"{result}",
        parse_mode="Markdown"
    )

# ══════════════════════════════════════════════
# FUN COMMANDS
# ══════════════════════════════════════════════
JOKES = [
    "Teacher: Tum school late kyun aaye?\nStudent: Aapne hi kaha tha — 'Never be in a hurry!' 😄",
    "Ek aadmi doctor ke paas gaya: 'Doctor, mujhe apni yaadaasht ki problem hai'\nDoctor: 'Yeh problem kab se hai?'\nAadmi: 'Kaunsi problem?' 😅",
    "Bhai: Yaar meri girlfriend mujhe samajhti nahi\nDost: Tu bhi toh usse nahi samajhta\nBhai: Woh toh theek hai, lekin main toh bol raha tha ki woh Maths nahi samajhti! 😂",
    "Papa: Beta, padhai karo, warna life mein kuch nahi milega\nBeta: Papa, aap toh padhey the, fir bhi mujhe kuch nahi diya! 😂",
    "Programmer ka dost: Yaar, baahar chal, bahut sundar mausam hai!\nProgrammer: Haan... windows toh hain mere paas, door se dekh leta hoon! 🖥️",
]

FACTS = [
    "🧠 Insaan ka brain 60% fat se bana hai — sabse zyada fatty organ!",
    "🐙 Octopus ke 3 dil hote hain aur unka khoon blue hota hai!",
    "🍯 Honey kabhi kharab nahi hota — 3000 saal purana honey bhi khane laayak hota hai!",
    "🌙 Moon par aapka weight Earth ka sirf 1/6 hoga!",
    "⚡ Bijli ka ek bolt 30,000 degrees Celsius tak garm ho sakta hai — suraj se 5 guna!",
    "🦈 Sharks dinosaurs se pehle se exist karti hain!",
    "💤 Insaan apni zindagi ka 1/3 hissa soते mein bitata hai!",
    "📱 Ek modern smartphone Apollo 11 mission ke computer se hazaron guna powerful hai!",
    "🐜 Ants kabhi soti nahi — in mein neend nahi hoti!",
    "🌍 Earth pe har din 100 lightning strikes hoti hain har second mein!",
]

QUOTES = [
    "💫 *\"Sapne woh nahi jo neend mein aate hain, sapne woh hain jo aapko neend nahi aane dete.\"*\n— A.P.J. Abdul Kalam",
    "🔥 *\"Safal hone ke liye, safalta ki icha, asafalta ke darr se zyada honi chahiye.\"*\n— Bill Cosby",
    "⭐ *\"Kal jo beet gaya woh history hai, kal jo aane wala hai woh mystery hai, aaj jo hai woh gift hai — isliye ise 'present' kehte hain.\"*",
    "💪 *\"Mushkilein insaan ko toadti nahi, balki use mazboot banati hain.\"*",
    "🌟 *\"Jo aap sochte hain, woh aap ban jaate hain.\"*\n— Mahatma Gandhi",
    "🚀 *\"Start where you are. Use what you have. Do what you can.\"*\n— Arthur Ashe",
    "🎯 *\"Ek choti si shuruaat badi kamyabi ki neenv hoti hai.\"*",
]

async def joke(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"😂 *JOKE TIME!*\n\n{random.choice(JOKES)}", parse_mode="Markdown")

async def fact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🤯 *INTERESTING FACT!*\n\n{random.choice(FACTS)}", parse_mode="Markdown")

async def quote(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✨ *QUOTE OF THE MOMENT*\n\n{random.choice(QUOTES)}", parse_mode="Markdown")

async def flip(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    result = random.choice(["🪙 HEADS!", "🪙 TAILS!"])
    await update.message.reply_text(f"🎰 *COIN FLIP!*\n\nResult: *{result}*", parse_mode="Markdown")

async def dice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    icons = ["", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]
    n = random.randint(1, 6)
    await update.message.reply_text(f"🎲 *DICE ROLL!*\n\nResult: {icons[n]} *{n}*", parse_mode="Markdown")

# ══════════════════════════════════════════════
# STATS
# ══════════════════════════════════════════════
async def stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load()
    u = get_user(data, update.effective_user.id)
    name = u.get("name", update.effective_user.first_name)
    tasks = u.get("tasks", [])
    expenses = u.get("expenses", [])
    month = datetime.date.today().strftime("%Y-%m")
    this_month_exp = sum(e["amount"] for e in expenses if e.get("month") == month)
    bdays = u.get("birthdays", [])
    vault = u.get("vault", {})
    pending = sum(1 for t in tasks if not t["done"])
    done = sum(1 for t in tasks if t["done"])

    today = datetime.date.today()
    upcoming_bdays = []
    for b in bdays:
        try:
            bd = datetime.date(today.year, b["month"], b["day"])
            if bd < today:
                bd = datetime.date(today.year + 1, b["month"], b["day"])
            days_left = (bd - today).days
            if days_left <= 30:
                upcoming_bdays.append(f"🎂 {b['naam']} — {days_left} din baad")
        except: pass

    text = (
        f"📊 *AAPKA DASHBOARD*\n"
        f"👤 _{name}_\n"
        f"📅 {datetime.date.today().strftime('%d %B %Y')}\n\n"
        f"{'━'*25}\n"
        f"📋 *TASKS*\n"
        f"   ⏳ Pending: {pending}\n"
        f"   ✅ Completed: {done}\n"
        f"   📌 Total: {len(tasks)}\n\n"
        f"💰 *KHARCHA (Is Mahine)*\n"
        f"   ₹{this_month_exp:.0f} total spent\n"
        f"   {len([e for e in expenses if e.get('month')==month])} transactions\n\n"
        f"🎂 *BIRTHDAYS*\n"
        f"   {len(bdays)} saved\n"
    )
    if upcoming_bdays:
        text += "   📅 Upcoming:\n"
        for b in upcoming_bdays[:3]:
            text += f"   {b}\n"
    text += f"\n🔐 *VAULT*: {len(vault)} items saved\n"
    text += f"{'━'*25}\n"
    text += f"💡 _/help se sab commands dekho!_"
    await update.message.reply_text(text, parse_mode="Markdown")

# ══════════════════════════════════════════════
# AUTO MESSAGE HANDLER (number detection, game)
# ══════════════════════════════════════════════
async def message_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id

    # GUESS GAME
    if uid in game_state and game_state[uid].get("type") == "guess":
        if text.isdigit():
            guess = int(text)
            target = game_state[uid]["number"]
            game_state[uid]["attempts"] += 1
            attempts = game_state[uid]["attempts"]
            if guess == target:
                del game_state[uid]
                await update.message.reply_text(
                    f"🎉 *SAHI JAWAB!*\n\n"
                    f"Number tha: *{target}*\n"
                    f"Tumne *{attempts}* attempts mein guess kiya!\n\n"
                    f"{'🏆 Shaandaar!' if attempts <= 5 else '👍 Achha kiya!'}\n\n"
                    f"Dobara khelne ke liye: `/guess`",
                    parse_mode="Markdown"
                )
            elif guess < target:
                await update.message.reply_text(f"⬆️ *Zyada bolo!* Number `{guess}` se bada hai.", parse_mode="Markdown")
            else:
                await update.message.reply_text(f"⬇️ *Kam bolo!* Number `{guess}` se chhota hai.", parse_mode="Markdown")
            return

    # AUTO NUMBER DETECTION
    cleaned = re.sub(r'[\s\-\(\)]', '', text)
    if re.match(r'^\+?[0-9]{10,15}$', cleaned):
        info = get_number_info(cleaned if cleaned.startswith('+') else '+' + cleaned)
        if not info:
            info = get_number_info('+91' + cleaned[-10:]) if len(cleaned) == 10 else None
        if info and info.get("valid"):
            reply = (
                f"📱 *NUMBER INFO DETECTED!*\n\n"
                f"🔢 Number: `{info['full']}`\n"
                f"✅ Status: *Valid*\n"
                f"🌍 Country: {info['country']}\n"
                f"📶 Operator: *{info['operator']}*\n"
                f"📞 Type: {info['type']}\n"
                f"📍 Region: {info['region']}"
            )
            await update.message.reply_text(reply, parse_mode="Markdown")
            return

    # DEFAULT
    keyboard = [[InlineKeyboardButton("📋 Menu", callback_data="show_menu")]]
    await update.message.reply_text(
        f"🤖 Samajh nahi aaya!\n\n`/help` se commands dekho ya niche menu se choose karo 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ══════════════════════════════════════════════
# CALLBACK HANDLER
# ══════════════════════════════════════════════
async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id

    menus = {
        "menu_tasks": "📋 *TASK MANAGER*\n\n`/add <task>` — add karo\n`/tasks` — list dekho\n`/done <n>` — complete karo\n`/deltask <n>` — hatao",
        "menu_expense": "💰 *EXPENSE TRACKER*\n\n`/kharcha 200 khana` — add karo\n`/report` — mahine ka hisaab\n`/delkharcha` — clear karo",
        "menu_games": "🎮 *GAMES*\n\n`/guess` — Number guessing\n`/quiz` — Quiz\n`/rps rock` — Rock Paper Scissors",
        "menu_bday": "🎂 *BIRTHDAY REMINDER*\n\n`/bday add Rahul 15 June`\n`/bday list` — sabhi dekho\n`/bday del 1` — hatao",
        "menu_num": "📱 *NUMBER INFO*\n\nKoi bhi phone number type karo ya:\n`/num +919876543210`\n\nAuto-detect bhi karta hai!",
        "menu_vault": "🔐 *SECRET VAULT*\n\n`/save gmail pass123` — save karo\n`/get gmail` — wapas lo\n`/vault` — keys dekho\n`/delvault gmail` — hatao",
        "menu_stats": None,
        "menu_fun": "😂 *FUN COMMANDS*\n\n`/joke` — Mazedaar joke\n`/fact` — Interesting fact\n`/quote` — Motivational quote\n`/flip` — Coin toss\n`/dice` — Dice roll",
        "menu_help": None,
    }

    if data == "menu_stats":
        await query.message.reply_text("/stats", parse_mode="Markdown")
        return
    if data == "menu_help":
        ctx.args = []
        await query.message.reply_text("/help type karein", parse_mode="Markdown")
        return
    if data == "show_menu":
        keyboard = [
            [InlineKeyboardButton("📋 Tasks", callback_data="menu_tasks"),
             InlineKeyboardButton("💰 Kharcha", callback_data="menu_expense")],
            [InlineKeyboardButton("🎮 Games", callback_data="menu_games"),
             InlineKeyboardButton("🎂 Birthdays", callback_data="menu_bday")],
            [InlineKeyboardButton("📱 Number Info", callback_data="menu_num"),
             InlineKeyboardButton("🔐 Vault", callback_data="menu_vault")],
            [InlineKeyboardButton("📊 Stats", callback_data="menu_stats"),
             InlineKeyboardButton("😂 Fun", callback_data="menu_fun")],
        ]
        await query.message.reply_text("🌟 *MEGA BOT MENU*\n\nKya karna hai?", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data in menus and menus[data]:
        await query.message.reply_text(menus[data], parse_mode="Markdown")
        return

    # QUIZ ANSWER
    if data.startswith("quiz_"):
        answer = data[5:]
        gs = game_state.get(uid, {})
        if gs.get("type") == "quiz":
            correct = gs["answer"]
            del game_state[uid]
            if answer == correct:
                await query.message.reply_text("✅ *BILKUL SAHI!* 🎉\n\nTum bahut smart ho! `/quiz` se aur khelo!", parse_mode="Markdown")
            else:
                await query.message.reply_text(f"❌ *Galat!*\n\nSahi jawab tha: *{correct.title()}*\n\nKoi baat nahi! `/quiz` se dobara try karo!", parse_mode="Markdown")

# ══════════════════════════════════════════════
# BIRTHDAY CHECK JOB
# ══════════════════════════════════════════════
async def check_birthdays(ctx: ContextTypes.DEFAULT_TYPE):
    today = datetime.date.today()
    data = load()
    for uid, u in data.items():
        bdays = u.get("birthdays", [])
        for b in bdays:
            try:
                if b["day"] == today.day and b["month"] == today.month:
                    await ctx.bot.send_message(
                        chat_id=int(uid),
                        text=f"🎂 *HAPPY BIRTHDAY!*\n\n🎉 Aaj *{b['naam']}* ka birthday hai!\n\n✨ Unhe wish karna mat bhoolo!",
                        parse_mode="Markdown"
                    )
            except: pass

# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("add", add_task))
    app.add_handler(CommandHandler("tasks", list_tasks))
    app.add_handler(CommandHandler("done", done_task))
    app.add_handler(CommandHandler("deltask", del_task))
    app.add_handler(CommandHandler("kharcha", kharcha))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("num", num_info))
    app.add_handler(CommandHandler("bday", bday))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("save", vault_save))
    app.add_handler(CommandHandler("get", vault_get))
    app.add_handler(CommandHandler("vault", vault_list))
    app.add_handler(CommandHandler("delvault", vault_del))
    app.add_handler(CommandHandler("guess", guess_game))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("rps", rps))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("fact", fact))
    app.add_handler(CommandHandler("quote", quote))
    app.add_handler(CommandHandler("flip", flip))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("stats", stats))

    # Callback & Messages
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Birthday job — roz subah 9 baje
    app.job_queue.run_daily(
        check_birthdays,
        time=datetime.time(hour=9, minute=0)
    )

    print("🤖 4Dreams MegaBot chal raha hai...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
