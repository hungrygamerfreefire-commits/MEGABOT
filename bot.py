import json
import random
import asyncio
import datetime
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

BOT_TOKEN = "8908268384:AAFraieu5ab8ApWR6dnlyJ59YBVJfkKOGk4"
DATA_FILE = "data.json"

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
        data[uid] = {"tasks": [], "expenses": [], "birthdays": [], "vault": {}, "name": ""}
    return data[uid]

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load()
    u = get_user(data, user.id)
    u["name"] = user.first_name
    save(data)
    keyboard = [
        [InlineKeyboardButton("📋 Tasks", callback_data="m_tasks"), InlineKeyboardButton("💰 Kharcha", callback_data="m_exp")],
        [InlineKeyboardButton("🎮 Games", callback_data="m_games"), InlineKeyboardButton("🎂 Birthdays", callback_data="m_bday")],
        [InlineKeyboardButton("📱 Number Info", callback_data="m_num"), InlineKeyboardButton("🔐 Vault", callback_data="m_vault")],
        [InlineKeyboardButton("📊 Stats", callback_data="m_stats"), InlineKeyboardButton("😂 Fun", callback_data="m_fun")],
        [InlineKeyboardButton("❓ Help", callback_data="m_help")],
    ]
    await update.message.reply_text(
        f"🌟 *Namaste {user.first_name}!*\n\n"
        "Main hoon *4Dreams MegaBot!*\n"
        "Niche se feature choose karo 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *COMMANDS LIST*\n\n"
        "*📋 TASKS*\n`/add task` `/tasks` `/done 1` `/deltask 1`\n\n"
        "*💰 KHARCHA*\n`/kharcha 200 khana` `/report`\n\n"
        "*📱 NUMBER INFO*\n`/num +919876543210`\n\n"
        "*🎂 BIRTHDAY*\n`/bday add Rahul 15 June`\n`/bday list` `/bday del 1`\n\n"
        "*⏰ REMINDER*\n`/remind 30min Meeting`\n\n"
        "*🔐 VAULT*\n`/save key value` `/get key` `/vault`\n\n"
        "*🎮 GAMES*\n`/guess` `/quiz` `/rps rock`\n\n"
        "*😂 FUN*\n`/joke` `/fact` `/quote` `/flip` `/dice`\n\n"
        "*📊 STATS*\n`/stats`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# TASKS
async def add_task(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("❌ Usage: `/add Meeting karna hai`", parse_mode="Markdown"); return
    data = load(); u = get_user(data, update.effective_user.id)
    task = " ".join(ctx.args)
    u["tasks"].append({"text": task, "done": False, "date": str(datetime.date.today())})
    save(data)
    await update.message.reply_text(f"✅ Task add!\n📌 *{task}*", parse_mode="Markdown")

async def list_tasks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load(); u = get_user(data, update.effective_user.id)
    tasks = u["tasks"]
    if not tasks:
        await update.message.reply_text("📋 Koi task nahi! `/add` se add karo.", parse_mode="Markdown"); return
    text = "📋 *TASK LIST*\n\n"
    for i, t in enumerate(tasks, 1):
        text += f"{'✅' if t['done'] else '⏳'} `{i}.` {t['text']}\n"
    pending = sum(1 for t in tasks if not t["done"])
    text += f"\n⏳ Pending: {pending} | ✅ Done: {len(tasks)-pending}"
    await update.message.reply_text(text, parse_mode="Markdown")

async def done_task(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args or not ctx.args[0].isdigit():
        await update.message.reply_text("❌ Usage: `/done 1`", parse_mode="Markdown"); return
    data = load(); u = get_user(data, update.effective_user.id)
    idx = int(ctx.args[0]) - 1
    if 0 <= idx < len(u["tasks"]):
        u["tasks"][idx]["done"] = True; save(data)
        await update.message.reply_text(f"🎉 Done! ✅ *{u['tasks'][idx]['text']}*", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Galat number!")

async def del_task(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args or not ctx.args[0].isdigit():
        await update.message.reply_text("❌ Usage: `/deltask 1`", parse_mode="Markdown"); return
    data = load(); u = get_user(data, update.effective_user.id)
    idx = int(ctx.args[0]) - 1
    if 0 <= idx < len(u["tasks"]):
        r = u["tasks"].pop(idx); save(data)
        await update.message.reply_text(f"🗑️ Hata diya: *{r['text']}*", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Galat number!")

# EXPENSE
async def kharcha(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 2:
        await update.message.reply_text("❌ Usage: `/kharcha 200 khana`", parse_mode="Markdown"); return
    try: amount = float(ctx.args[0])
    except:
        await update.message.reply_text("❌ Pehle amount likhna hai!"); return
    reason = " ".join(ctx.args[1:])
    data = load(); u = get_user(data, update.effective_user.id)
    month = datetime.date.today().strftime("%Y-%m")
    u["expenses"].append({"amount": amount, "reason": reason, "date": str(datetime.date.today()), "month": month})
    save(data)
    total = sum(e["amount"] for e in u["expenses"] if e.get("month") == month)
    await update.message.reply_text(
        f"💰 *Kharcha save!*\n💸 ₹{amount:.0f} — {reason}\n📊 Is mahine total: *₹{total:.0f}*",
        parse_mode="Markdown")

async def report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load(); u = get_user(data, update.effective_user.id)
    month = datetime.date.today().strftime("%Y-%m")
    exps = [e for e in u["expenses"] if e.get("month") == month]
    if not exps:
        await update.message.reply_text("💰 Is mahine koi kharcha nahi!", parse_mode="Markdown"); return
    total = sum(e["amount"] for e in exps)
    text = f"📊 *IS MAHINE KA HISAAB*\n_{datetime.date.today().strftime('%B %Y')}_\n\n"
    for e in exps[-10:]:
        text += f"• ₹{e['amount']:.0f} — {e['reason']}\n"
    text += f"\n💰 *TOTAL: ₹{total:.0f}*"
    await update.message.reply_text(text, parse_mode="Markdown")

# NUMBER INFO
COUNTRY_DB = {
    "91": {"name": "🇮🇳 India", "ops": {"62":"Jio","63":"Jio","64":"Jio","65":"Jio","66":"Jio","67":"Jio","68":"Jio","69":"Jio","70":"BSNL","72":"Airtel","73":"Airtel","74":"Airtel","75":"Vi","76":"Airtel","77":"Airtel","78":"Airtel","79":"Vi","80":"BSNL","81":"Airtel","82":"Airtel","83":"Airtel","84":"Vi","85":"Jio","86":"BSNL","87":"Vi","88":"Airtel","89":"BSNL","90":"Airtel","91":"Airtel","92":"Airtel","93":"Vi","94":"BSNL","95":"Vi","96":"Airtel","97":"Airtel","98":"Airtel","99":"Vi"}},
    "1":  {"name": "🇺🇸 USA/Canada", "ops": {}},
    "44": {"name": "🇬🇧 UK", "ops": {}},
    "971":{"name": "🇦🇪 UAE", "ops": {}},
    "92": {"name": "🇵🇰 Pakistan", "ops": {}},
    "880":{"name": "🇧🇩 Bangladesh", "ops": {}},
    "977":{"name": "🇳🇵 Nepal", "ops": {}},
    "86": {"name": "🇨🇳 China", "ops": {}},
    "81": {"name": "🇯🇵 Japan", "ops": {}},
    "49": {"name": "🇩🇪 Germany", "ops": {}},
    "61": {"name": "🇦🇺 Australia", "ops": {}},
}

def parse_number(raw):
    raw = re.sub(r'[\s\-\(\)]', '', raw).lstrip('+').lstrip('00')
    for length in [3, 2, 1]:
        code = raw[:length]
        if code in COUNTRY_DB:
            local = raw[length:]
            info = COUNTRY_DB[code]
            if code == "91":
                if len(local) != 10 or local[0] not in "6789":
                    return None
                op = info["ops"].get(local[:2], "Unknown")
                return {"full": f"+{code}{local}", "country": info["name"], "cc": f"+{code}", "local": local, "operator": op, "valid": True}
            return {"full": f"+{code}{local}", "country": info["name"], "cc": f"+{code}", "local": local, "operator": "N/A", "valid": True}
    if len(raw) == 10 and raw[0] in "6789":
        code = "91"; local = raw; info = COUNTRY_DB["91"]
        op = info["ops"].get(local[:2], "Unknown")
        return {"full": f"+91{local}", "country": info["name"], "cc": "+91", "local": local, "operator": op, "valid": True}
    return None

async def num_info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("📱 Usage: `/num +919876543210`", parse_mode="Markdown"); return
    info = parse_number(ctx.args[0])
    if not info:
        await update.message.reply_text("❌ Number valid nahi hai!", parse_mode="Markdown"); return
    await update.message.reply_text(
        f"📱 *NUMBER DETAILS*\n\n"
        f"🔢 Number: `{info['full']}`\n✅ Status: *Valid*\n"
        f"🌍 Country: {info['country']}\n"
        f"📡 Code: {info['cc']}\n"
        f"📶 Operator: *{info['operator']}*\n"
        f"🔢 Local: `{info['local']}`",
        parse_mode="Markdown")

# BIRTHDAY
MONTHS = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12,
          "january":1,"february":2,"march":3,"april":4,"june":6,"july":7,"august":8,"september":9,"october":10,"november":11,"december":12}
MN = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

async def bday(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("🎂 Usage:\n`/bday add Rahul 15 June`\n`/bday list`\n`/bday del 1`", parse_mode="Markdown"); return
    action = ctx.args[0].lower()
    data = load(); u = get_user(data, update.effective_user.id)
    if action == "add":
        if len(ctx.args) < 4:
            await update.message.reply_text("❌ `/bday add Naam DD Month`", parse_mode="Markdown"); return
        naam = ctx.args[1]; day = ctx.args[2]; month_num = MONTHS.get(ctx.args[3].lower())
        if not month_num or not day.isdigit():
            await update.message.reply_text("❌ Date sahi nahi! Example: `/bday add Rahul 15 June`", parse_mode="Markdown"); return
        u["birthdays"].append({"naam": naam, "day": int(day), "month": month_num}); save(data)
        await update.message.reply_text(f"🎂 Saved!\n👤 *{naam}* — {day} {MN[month_num]}", parse_mode="Markdown")
    elif action == "list":
        bdays = u.get("birthdays", [])
        if not bdays:
            await update.message.reply_text("🎂 Koi birthday save nahi!", parse_mode="Markdown"); return
        today = datetime.date.today()
        text = "🎂 *BIRTHDAY LIST*\n\n"
        for i, b in enumerate(bdays, 1):
            try:
                bd = datetime.date(today.year, b["month"], b["day"])
                if bd < today: bd = datetime.date(today.year+1, b["month"], b["day"])
                dl = (bd - today).days
                cnt = "🎉 *AAJ HAI!*" if dl == 0 else f"⏳ {dl} din baad"
            except: cnt = "📅"
            text += f"`{i}.` 🎂 *{b['naam']}* — {b['day']} {MN[b['month']]} | {cnt}\n"
        await update.message.reply_text(text, parse_mode="Markdown")
    elif action == "del":
        if len(ctx.args) < 2 or not ctx.args[1].isdigit():
            await update.message.reply_text("❌ `/bday del 1`", parse_mode="Markdown"); return
        idx = int(ctx.args[1]) - 1
        if 0 <= idx < len(u["birthdays"]):
            r = u["birthdays"].pop(idx); save(data)
            await update.message.reply_text(f"🗑️ Hata diya: *{r['naam']}*", parse_mode="Markdown")

# REMINDER
async def remind(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 2:
        await update.message.reply_text("⏰ Usage: `/remind 30min Meeting`\nYa `/remind 2hr Lunch`", parse_mode="Markdown"); return
    ts = ctx.args[0].lower(); msg = " ".join(ctx.args[1:]); secs = 0
    m = re.search(r'(\d+)', ts)
    if m:
        n = int(m.group(1))
        if "hr" in ts: secs = n * 3600
        elif "min" in ts: secs = n * 60
        elif "sec" in ts: secs = n
    if secs <= 0 or secs > 86400:
        await update.message.reply_text("❌ Time sahi nahi! (1sec se 24hr tak)", parse_mode="Markdown"); return
    chat_id = update.effective_chat.id
    disp = f"{secs//3600}hr {(secs%3600)//60}min" if secs >= 3600 else f"{secs//60}min" if secs >= 60 else f"{secs}sec"
    await update.message.reply_text(f"⏰ *Reminder set!*\n💬 _{msg}_\n⏱ *{disp}* baad remind karunga!", parse_mode="Markdown")
    async def fire():
        await asyncio.sleep(secs)
        await ctx.bot.send_message(chat_id=chat_id, text=f"⏰ *REMINDER!*\n\n🔔 {msg}", parse_mode="Markdown")
    asyncio.create_task(fire())

# VAULT
async def vault_save(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 2:
        await update.message.reply_text("❌ `/save gmail mypassword`", parse_mode="Markdown"); return
    data = load(); u = get_user(data, update.effective_user.id)
    key = ctx.args[0]; val = " ".join(ctx.args[1:])
    u["vault"][key] = {"value": val, "date": str(datetime.date.today())}; save(data)
    await update.message.reply_text(f"🔐 Saved!\n🔑 Key: `{key}`", parse_mode="Markdown")

async def vault_get(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("❌ `/get gmail`", parse_mode="Markdown"); return
    data = load(); u = get_user(data, update.effective_user.id)
    item = u["vault"].get(ctx.args[0])
    if item:
        await update.message.reply_text(f"🔐 *VAULT*\n🔑 `{ctx.args[0]}`\n💎 `{item['value']}`", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ `{ctx.args[0]}` nahi mila!", parse_mode="Markdown")

async def vault_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load(); u = get_user(data, update.effective_user.id)
    vault = u.get("vault", {})
    if not vault:
        await update.message.reply_text("🔐 Vault khali hai!", parse_mode="Markdown"); return
    text = "🔐 *VAULT KEYS*\n\n" + "\n".join(f"🔑 `{k}`" for k in vault) + "\n\n_/get key se value lo_"
    await update.message.reply_text(text, parse_mode="Markdown")

# GAMES
game_state = {}

async def guess_game(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    game_state[uid] = {"type": "guess", "number": random.randint(1, 100), "attempts": 0}
    await update.message.reply_text("🎮 *NUMBER GAME!*\n\n1 se 100 ke beech number socha hai!\nGuess karo — seedha number type karo!", parse_mode="Markdown")

QUIZ = [
    {"q": "India ki capital?", "a": "new delhi", "opts": ["Mumbai", "New Delhi", "Kolkata", "Chennai"]},
    {"q": "1+1=?", "a": "2", "opts": ["1", "2", "3", "11"]},
    {"q": "Sabse bada planet?", "a": "jupiter", "opts": ["Saturn", "Jupiter", "Mars", "Earth"]},
    {"q": "Water formula?", "a": "h2o", "opts": ["CO2", "H2O", "O2", "NaCl"]},
    {"q": "CPU full form?", "a": "central processing unit", "opts": ["Central Process Unit", "Central Processing Unit", "Computer Processing Unit", "Core Processing Unit"]},
    {"q": "1 KB = kitne bytes?", "a": "1024", "opts": ["1000", "1024", "512", "2048"]},
]

async def quiz(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    q = random.choice(QUIZ)
    opts = q["opts"].copy(); random.shuffle(opts)
    game_state[uid] = {"type": "quiz", "answer": q["a"]}
    kb = [[InlineKeyboardButton(o, callback_data=f"qz_{o.lower()}")] for o in opts]
    await update.message.reply_text(f"🧠 *QUIZ!*\n\n❓ {q['q']}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def rps(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("✊ `/rps rock` ya `paper` ya `scissors`", parse_mode="Markdown"); return
    mp = {"stone":"rock","patthar":"rock","kaagaz":"paper","kainchi":"scissors"}
    uc = mp.get(ctx.args[0].lower(), ctx.args[0].lower())
    if uc not in ["rock","paper","scissors"]:
        await update.message.reply_text("❌ rock / paper / scissors likhna hai!", parse_mode="Markdown"); return
    bc = random.choice(["rock","paper","scissors"])
    icons = {"rock":"✊","paper":"📄","scissors":"✂️"}
    wins = {"rock":"scissors","paper":"rock","scissors":"paper"}
    result = "🤝 *DRAW!*" if uc == bc else ("🎉 *TUM JEETE!*" if wins[uc] == bc else "😅 *BOT JEETA!*")
    await update.message.reply_text(f"✊📄✂️\nTum: {icons[uc]} | Bot: {icons[bc]}\n\n{result}", parse_mode="Markdown")

# FUN
JOKES = [
    "Teacher: Late kyun aaye?\nStudent: Aapne kaha — Never be in a hurry! 😄",
    "Doctor: Problem kab se hai?\nPaagal: Kaunsi problem? 😅",
    "Programmer ne girlfriend se bola: Main tumse zyada Python se pyaar karta hoon\nGirlfriend: Yeh koi baat hai?\nProgrammer: Haan — Python mein errors kam aate hain! 😂",
]
FACTS = [
    "🧠 Brain 60% fat se bana hai!",
    "🐙 Octopus ke 3 dil hote hain!",
    "🍯 Honey kabhi kharab nahi hota — 3000 saal purana bhi!",
    "⚡ Bijli suraj se 5 guna garam hoti hai!",
    "🐜 Ants kabhi soti nahi!",
]
QUOTES = [
    "💫 *\"Sapne woh nahi jo neend mein aate hain, sapne woh hain jo neend nahi aane dete.\"*\n— APJ Abdul Kalam",
    "🔥 *\"Start where you are. Use what you have. Do what you can.\"*",
    "⭐ *\"Kal history, kal mystery, aaj gift hai — isliye present kehte hain.\"*",
]

async def joke(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"😂 *JOKE!*\n\n{random.choice(JOKES)}", parse_mode="Markdown")

async def fact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🤯 *FACT!*\n\n{random.choice(FACTS)}", parse_mode="Markdown")

async def quote(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✨ *QUOTE*\n\n{random.choice(QUOTES)}", parse_mode="Markdown")

async def flip(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🪙 *{random.choice(['HEADS!', 'TAILS!'])}*", parse_mode="Markdown")

async def dice_roll(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    n = random.randint(1, 6)
    icons = ["","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣"]
    await update.message.reply_text(f"🎲 *{icons[n]} = {n}*", parse_mode="Markdown")

# STATS
async def stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load(); u = get_user(data, update.effective_user.id)
    tasks = u.get("tasks", []); expenses = u.get("expenses", [])
    month = datetime.date.today().strftime("%Y-%m")
    total_exp = sum(e["amount"] for e in expenses if e.get("month") == month)
    pending = sum(1 for t in tasks if not t["done"])
    await update.message.reply_text(
        f"📊 *DASHBOARD*\n👤 {u.get('name','')}\n📅 {datetime.date.today().strftime('%d %B %Y')}\n\n"
        f"📋 Tasks: {len(tasks)} total | ⏳ {pending} pending\n"
        f"💰 Is mahine kharcha: ₹{total_exp:.0f}\n"
        f"🎂 Birthdays saved: {len(u.get('birthdays',[]))}\n"
        f"🔐 Vault items: {len(u.get('vault',{}))}",
        parse_mode="Markdown")

# MESSAGE HANDLER
async def msg_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id

    # GUESS GAME
    if uid in game_state and game_state[uid].get("type") == "guess" and text.isdigit():
        guess = int(text); target = game_state[uid]["number"]
        game_state[uid]["attempts"] += 1; att = game_state[uid]["attempts"]
        if guess == target:
            del game_state[uid]
            await update.message.reply_text(f"🎉 *SAHI!* Number tha *{target}*\n{att} attempts mein jeete! `/guess` se dobara khelo!", parse_mode="Markdown")
        elif guess < target:
            await update.message.reply_text(f"⬆️ Zyada bolo! (`{guess}` se bada)", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"⬇️ Kam bolo! (`{guess}` se chhota)", parse_mode="Markdown")
        return

    # AUTO NUMBER DETECT
    clean = re.sub(r'[\s\-\(\)]', '', text)
    if re.match(r'^\+?[0-9]{10,15}$', clean):
        info = parse_number(clean)
        if info and info.get("valid"):
            await update.message.reply_text(
                f"📱 *NUMBER DETECTED!*\n\n🔢 `{info['full']}`\n✅ Valid\n🌍 {info['country']}\n📶 {info['operator']}",
                parse_mode="Markdown"); return

    await update.message.reply_text("🤖 `/help` se commands dekho!", parse_mode="Markdown")

# CALLBACK
async def cb_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    d = q.data; uid = q.from_user.id
    menus = {
        "m_tasks": "📋 *TASKS*\n`/add task` `/tasks` `/done 1` `/deltask 1`",
        "m_exp":   "💰 *KHARCHA*\n`/kharcha 200 khana` `/report`",
        "m_games": "🎮 *GAMES*\n`/guess` `/quiz` `/rps rock`",
        "m_bday":  "🎂 *BIRTHDAY*\n`/bday add Rahul 15 June`\n`/bday list` `/bday del 1`",
        "m_num":   "📱 *NUMBER INFO*\n`/num +919876543210`\nYa seedha number type karo!",
        "m_vault": "🔐 *VAULT*\n`/save key value` `/get key` `/vault`",
        "m_fun":   "😂 *FUN*\n`/joke` `/fact` `/quote` `/flip` `/dice`",
        "m_help":  "❓ `/help` type karo!",
    }
    if d == "m_stats":
        await q.message.reply_text("/stats", parse_mode="Markdown"); return
    if d in menus:
        await q.message.reply_text(menus[d], parse_mode="Markdown"); return
    if d.startswith("qz_"):
        ans = d[3:]; gs = game_state.get(uid, {})
        if gs.get("type") == "quiz":
            del game_state[uid]
            if ans == gs["answer"]:
                await q.message.reply_text("✅ *SAHI JAWAB!* 🎉 `/quiz` se aur khelo!", parse_mode="Markdown")
            else:
                await q.message.reply_text(f"❌ *Galat!*\nSahi tha: *{gs['answer'].title()}*", parse_mode="Markdown")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
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
    app.add_handler(CommandHandler("guess", guess_game))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("rps", rps))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("fact", fact))
    app.add_handler(CommandHandler("quote", quote))
    app.add_handler(CommandHandler("flip", flip))
    app.add_handler(CommandHandler("dice", dice_roll))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(cb_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))
    print("✅ 4Dreams MegaBot running!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
