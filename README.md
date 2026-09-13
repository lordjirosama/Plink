# 🤖 Advanced File Share Bot

## Setup Guide

### Step 1 — Bot Token
1. Open Telegram → search `@BotFather`
2. Send `/newbot`
3. Copy the token

### Step 2 — Owner ID
1. Open `@userinfobot` on Telegram
2. Send any message → copy your numeric ID

### Step 3 — Storage Channel
1. Create a **private** Telegram channel
2. Add your bot as **admin** with post permissions
3. Forward any message from that channel to `@userinfobot` → get the channel ID (starts with `-100...`)

### Step 4 — MongoDB
1. Go to [mongodb.com/atlas](https://mongodb.com/atlas) → Free tier
2. Create cluster → Get connection string
3. Replace `user:password` in MONGO_URI

### Step 5 — Install & Run
```bash
git clone <your-repo>
cd bot

cp .env.example .env
# Fill in .env with your values

pip install -r requirements.txt

python main.py
```

---

## Commands Reference

| Command | Access | Description |
|---------|--------|-------------|
| `/start` | All | Welcome message + file retrieval |
| `/glink` | Admin | Generate single file link |
| `/plink` | Admin | Generate poster + file link |
| `/batch` | Admin | Start batch file collection |
| `/batchdone` | Admin | Finish batch and get link |
| `/help` | All | Command list |
| `/status` | Admin | Bot statistics |
| `/admin <id>` | Owner | Add admin |
| `/deladmin <id>` | Owner | Remove admin |
| `/admins` | Admin | List all admins |
| `/ban <id> [reason]` | Admin | Ban user |
| `/unban <id>` | Admin | Unban user |
| `/banned` | Admin | List banned users |
| `/broadcast` | Admin | Broadcast to all users |
| `/shortener` | Admin | Manage URL shorteners |
| `/cancel` | Admin | Cancel active operation |

---

## File Structure
```
bot/
├── main.py              ← Entry point
├── config.py            ← Settings from .env
├── requirements.txt
├── .env.example
├── database/
│   └── db.py            ← MongoDB operations
├── handlers/
│   ├── start.py         ← /start, /help, deep links
│   ├── files.py         ← /glink, /plink
│   ├── batch.py         ← /batch
│   ├── admin.py         ← /admin, /status
│   ├── broadcast.py     ← /broadcast
│   ├── ban.py           ← /ban, /unban
│   └── shortener.py     ← /shortener panel
└── utils/
    └── helpers.py       ← Shared utilities
```

---

## How File Links Work
- Files are **forwarded** to your private storage channel
- Bot saves the `message_id` in MongoDB
- A unique 8-char `file_uid` is generated → becomes the deep link
- When user opens `t.me/botname?start=XXXX`, bot forwards the file from storage channel to user

## Deploy on VPS / Railway / Render
- Set all `.env` variables as environment variables
- Run: `python main.py`
- For 24/7 uptime use `screen`, `pm2`, or Docker
