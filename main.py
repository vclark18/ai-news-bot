from keep_alive import keep_alive
import os
import discord
import requests
import datetime
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import time
from zoneinfo import ZoneInfo

keep_alive()

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_NAME = "general"

intents = discord.Intents.default()
intents.message_content = True  # <-- CRITICAL for command handling
bot = commands.Bot(command_prefix="!", intents=intents)

def summarize_article(article):
    return f"📰 **{article['title']}**\n{article['description']}\n<{article['url']}>"

def fetch_ai_news():
    response = requests.get("https://gnews.io/api/v4/search?q=AI+OR+technology&lang=en&token=demo")
    if response.status_code == 200:
        articles = response.json().get("articles", [])[:3]
        return [summarize_article(article) for article in articles]
    return ["⚠️ Failed to fetch news."]

def fetch_weekly_digest():
    topics = ["climate OR environment", "global politics OR geopolitics"]
    summaries = []
    for topic in topics:
        response = requests.get(f"https://gnews.io/api/v4/search?q={topic}&lang=en&token=demo")
        if response.status_code == 200:
            articles = response.json().get("articles", [])[:3]
            summaries.append(f"🌍 **{topic.title()}**")
            summaries.extend([summarize_article(article) for article in articles])
    return summaries

@bot.event
async def on_ready():
    print(f'{bot.user} has connected.')
    send_daily_news.start()
    send_weekly_digest.start()

@tasks.loop(time=datetime.time(hour=19, minute=52, tzinfo=ZoneInfo("America/New_York")))  # 5 AM EST
async def send_daily_news():
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
        if channel:
            news = fetch_ai_news()
            await channel.send("🗞️ **Daily AI/Tech Brief:**")
            for item in news:
                await channel.send(item)

@tasks.loop(time=datetime.time(hour=19, minute=52, tzinfo=ZoneInfo("America/New_York")))  # 5 AM EST
async def send_weekly_digest():
    if datetime.datetime.today().weekday() == 0:  # Monday only
        for guild in bot.guilds:
            channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
            if channel:
                digest = fetch_weekly_digest()
                await channel.send("📅 **Weekly Global Digest:**")
                for item in digest:
                    await channel.send(item)

@bot.command()
async def test(ctx):
    await ctx.send("✅ Bot is up and running!")

bot.run(DISCORD_TOKEN)

