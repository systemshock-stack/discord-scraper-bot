import discord
from discord.ext import commands
import asyncio
import time
import re
import os
from datetime import datetime, timedelta
import pytz

# === SETTINGS (CHANGE THESE) ===
CHANNELS_TO_SCRAPE = [
    'general', 'arma-general', 'games-general', 'ttrpg-general'
    # Add your channels here
]
OUTPUT_FILE = 'scraped_data.txt'  # Saves in same folder
IDLE_THRESHOLD = 60  # Seconds of no messages
HISTORY_BATCH = 50
WEEKLY_CHANNEL = 'general'
WEEKLY_MESSAGE = "Weekly check-in!"
WEEKLY_HOUR = 19  # 7 PM
WEEKLY_MINUTE = 0
TIMEZONE = 'Europe/London'

# === BOT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

seen_message_ids = set()
last_activity = 0
history_before_id = {chan: None for chan in CHANNELS_TO_SCRAPE}

# === CLEAN & SAVE ===
def clean_and_save(msg, channel_name):
    if msg.id in seen_message_ids or msg.author.bot or not msg.content:
        return False
    clean_msg = re.sub(r'http[s]?://[^\s]+', '', msg.content)
    clean_msg = re.sub(r'<@!?\d+>', '', clean_msg)
    clean_msg = re.sub(r'@\w+', '', clean_msg)
    clean_msg = re.sub(r'\s+', ' ', clean_msg).strip()
    if not clean_msg:
        return False
    tagged = f'[{channel_name}] {clean_msg}'
    if msg.attachments:
        tagged += ' [IMAGE]'
    seen_message_ids.add(msg.id)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(tagged + '\n')
    if len(seen_message_ids) % 10 == 0:
        print(f'SAVED: {tagged[:50]}... ({len(seen_message_ids)} total)')
    return True

# === EVENTS ===
@bot.event
async def on_ready():
    global last_activity
    last_activity = time.time()
    print(f'Bot ready! Listening to {len(CHANNELS_TO_SCRAPE)} channels.')
    bot.loop.create_task(idle_history_scraper())
    bot.loop.create_task(weekly_post_scheduler())

@bot.event
async def on_message(message):
    global last_activity
    last_activity = time.time()
    if message.guild and message.channel.name in CHANNELS_TO_SCRAPE:
        clean_and_save(message, message.channel.name)

# === IDLE HISTORY ===
async def idle_history_scraper():
    global last_activity
    while True:
        await asyncio.sleep(60)
        if time.time() - last_activity < IDLE_THRESHOLD:
            continue
        print('IDLE: Scraping history...')
        # (History logic here — simplified for now)
        await asyncio.sleep(5)

# === WEEKLY POST ===
async def weekly_post_scheduler():
    while True:
        now = datetime.now(pytz.timezone(TIMEZONE))
        next_post = now.replace(hour=WEEKLY_HOUR, minute=WEEKLY_MINUTE, second=0, microsecond=0)
        if next_post < now:
            next_post += timedelta(days=1)
        sleep_sec = (next_post - now).total_seconds()
        await asyncio.sleep(sleep_sec)
        channel = discord.utils.get(bot.get_all_channels(), name=WEEKLY_CHANNEL)
        if channel:
            await channel.send(WEEKLY_MESSAGE)

# === RUN ===
# bot.run('YOUR_TOKEN_HERE')  # Add your token when ready
print("Bot code ready! Add your token and run.")