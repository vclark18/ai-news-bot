from keep_alive import keep_alive
import os
import discord
import requests
import datetime
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Start the web server to keep the bot alive
keep_alive()

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
CHANNEL_NAME = "general"

# Set up bot intents and prefix
intents = discord.Intents.default()
intents.message_content = True  # Make sure this is enabled in the Discord Developer Portal
bot = commands.Bot(command_prefix="!", intents=intents)

# Helper to summarize news
def summarize_article(article):
    return f"📰 **{article['title']}**\n{article['description']}\n<{article['url']}>"

# Fetch daily AI/tech news
def fetch_ai_news():
    response = requests.get(f"https://gnews.io/api/v4/search?q=AI+OR+technology&lang=en&token={GNEWS_API_KEY}")
    print("Daily news fetch:", response.status_code, response.text)  # Debugging
    if response.status_code == 200:
        articles = response.json().get("articles", [])[:3]
        return [summarize_article(article) for article in articles] if articles else ["⚠️ No news articles found."]
    return ["⚠️ Failed to fetch news."]

# Fetch weekly digest
def fetch_weekly_digest():
    topics = ["climate OR environment", "global politics OR geopolitics"]
    summaries = []
    for topic in topics:
        response = requests.get(f"https://gnews.io/api/v4/search?q={topic}&lang=en&token={GNEWS_API_KEY}")
        print(f"Weekly digest fetch for {topic}:", response.status_code, response.text)  # Debugging
        if response.status_code == 200:
            articles = response.json().get("articles", [])[:3]
            if articles:
                summaries.append(f"🌍 **{topic.title()}**")
                summaries.extend([summarize_article(article) for article in articles])
            else:
                summaries.append(f"⚠️ No news found for {topic}.")
        else:
            summaries.append(f"⚠️ Failed to fetch news for {topic}.")
    return summaries

# Send messages when bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected.')
    send_daily_news.start()
    send_weekly_digest.start()

# Daily AI/tech news loop
@tasks.loop(time=datetime.time(hour=20, minute=12))  # 5 AM EST
async def send_daily_news():
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
        if channel:
            news = fetch_ai_news()
            await channel.send("🗞️ **Daily AI/Tech Brief:**")
            for item in news:
                await channel.send(item)

# Weekly digest loop (Mondays)
@tasks.loop(time=datetime.time(hour=20, minute=12))  # 5 AM EST
async def send_weekly_digest():
    if datetime.datetime.today().weekday() == 0:  # Monday
        for guild in bot.guilds:
            channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
            if channel:
                digest = fetch_weekly_digest()
                await channel.send("📅 **Weekly Global Digest:**")
                for item in digest:
                    await channel.send(item)

# Manual test command
@bot.command()
async def test(ctx):
    await ctx.send("✅ Bot is up and running!")

# Start bot
bot.run(DISCORD_TOKEN)


