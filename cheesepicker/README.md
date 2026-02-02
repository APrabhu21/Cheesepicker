# 🧀 Cheesepicker - Dota 2 Counter Picker Bot

A Discord bot that helps you find the best Dota 2 hero counters against enemy team compositions using OpenDota API data.

## 📋 Setup Instructions

### 1. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** and give it a name (e.g., "Cheesepicker")
3. Go to the **"Bot"** section in the left sidebar
4. Click **"Add Bot"** and confirm
5. Under **"Privileged Gateway Intents"**, enable:
   - ✅ Message Content Intent
6. Click **"Reset Token"** and copy your bot token (keep it secret!)

### 2. Invite Bot to Your Server

1. Go to **"OAuth2"** → **"URL Generator"** in the left sidebar
2. Select these scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Select these bot permissions:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ Use External Emojis
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### 3. Install Dependencies

```powershell
# Install required packages
pip install -r requirements.txt
```

### 4. Set Bot Token

**Option A: Environment Variable (Recommended)**
```powershell
# Windows PowerShell
$env:DISCORD_BOT_TOKEN="your_bot_token_here"

# Or set permanently
[System.Environment]::SetEnvironmentVariable('DISCORD_BOT_TOKEN', 'your_token_here', 'User')
```

**Option B: .env File**
```powershell
# Create .env file
copy .env.example .env
# Then edit .env and add your token
```

### 5. Run the Bot

```powershell
python discord_bot.py
```

You should see: `Cheesepicker#1234 has connected to Discord!`

## 🎮 Bot Commands

### `!counter hero1 hero2 hero3 hero4`
Find the best counter heroes against an enemy team.

**Example:**
```
!counter "Anti-Mage" Invoker Pudge "Crystal Maiden"
```

Returns the top 10 heroes with:
- Average winrate against all 4 enemies
- Individual winrates vs each enemy

### `!heroes [search]`
List all available Dota 2 heroes or search for specific ones.

**Examples:**
```
!heroes
!heroes spirit
!heroes phantom
```

### `!ping`
Check if the bot is online and responsive.

### `!help_cheesepicker`
Show detailed help about all commands.

## 📊 How It Works

1. Takes 4 enemy hero names as input
2. Fetches matchup data from OpenDota API for each hero
3. Calculates win percentages against each enemy
4. Computes a "win product" (multiplicative effectiveness)
5. Returns heroes sorted by overall effectiveness against the entire team

The multiplicative approach gives higher weight to heroes that perform well against ALL enemies, not just some.

## 🔧 Troubleshooting

### Bot doesn't respond
- Check that Message Content Intent is enabled in Discord Developer Portal
- Verify bot has permission to read/send messages in the channel

### "DISCORD_BOT_TOKEN not set" error
- Make sure you set the environment variable correctly
- Try restarting your terminal after setting it

### "Hero not found" error
- Hero names are case-insensitive
- Multi-word names need quotes: `"Anti-Mage"` not `Anti-Mage`
- Use `!heroes` to see all available hero names

### API errors
- OpenDota API might be temporarily down
- Check your internet connection
- Try again in a few moments

## 📝 Files

- `discord_bot.py` - Discord bot with commands
- `Basic Logic.py` - Original CLI version
- `requirements.txt` - Python dependencies
- `.env.example` - Template for bot token

## 🌐 API

Data provided by [OpenDota API](https://www.opendota.com/)

## 📄 License

Free to use and modify!
