import os
import asyncio
import aiohttp
import random
import requests
import html
from telethon import events
from .client import client
from utils.logger import logger, LOG_FILE
from .config import WEATHER_API_KEY
from .config import GROQ_API_KEY
from datetime import datetime
from groq import AsyncGroq

COMMAND_HANDLERS = {}
groq_client = AsyncGroq(api_key=GROQ_API_KEY)
START_TIME = datetime.now()
SUBREDDITS = ['ruAsska', 'uamemesit', 'Pikabu', 'ukraine', 'ProgrammerHumor']
MEME_CACHE = []
GIF_CACHE = []
SELF_USER = "me"
def command(name):
    """A decorator to register a command handler."""
    def wrapper(func):
        COMMAND_HANDLERS[name] = func
        return func
    return wrapper

@client.on(events.NewMessage(from_users=SELF_USER))
async def handle_message(event):
    msg = (event.raw_text or "").strip()
    if not msg:
        return
    chat = await event.get_chat()
    chat_name = getattr(chat, "title", "Saved Messages")
    logger.info(f"[{chat_name}] Your message: {msg}")

    parts = msg.split()
    cmd = parts[0].lower()
    args = parts[1:]

    handler = COMMAND_HANDLERS.get(cmd)
    if handler:
        await handler(event, *args)

@command(".help")
async def handle_help(event):
    help_text = """
    <b>Commands:</b>
    
<code>.help</code> - get help
<code>.ping</code> - ping
<code>.mem</code> - send random meme
<code>.gif</code> - send random GIF
<code>.cat</code> - send cat
<code>.qweather</code> - send weather without API
<code>.weather</code> - send weather with API
<code>.uptime</code> - working time
<code>.time</code> - send time 
<code>.spin</code> - gambling
<code>.rbuser</code> - send info about roblox user
<code>.cat</code> - send random cat image
<code>.lizard</code> - send random lizard image
<code>.dog</code> - send random dog image
<code>.turtle</code> - send random turtle image
<code>.fox</code> - send random fox image
    """
    await event.reply(help_text, parse_mode="html" )
    
@command(".ping")
async def handle_ping(event):
    await event.reply("pong 🏓")
    
@command(".mem")
async def handle_mem_universal(event):
    global MEME_CACHE
    

    if not MEME_CACHE:
        selected_source = random.choice(SUBREDDITS)
        url = f"https://meme-api.com/gimme/{selected_source}/50"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        MEME_CACHE = [m for m in data.get("memes", []) if m.get("url")]
                        random.shuffle(MEME_CACHE)
                        logger.info(f"[mem] Cache refilled with 50 memes from r/{selected_source}")
                    else:
                        await event.reply(f"Помилка API (r/{selected_source}): {response.status}")
                        return
        except Exception as e:
            await event.reply(f"Не вдалося підключитися до сервера: {e}")
            return

    if not MEME_CACHE:
        await event.reply("Не вдалося знайти нових мемов. Спробуй ще раз.")
        return

    meme = MEME_CACHE.pop()
    meme_url = meme.get("url")
    title = meme.get("title", "Мем")
    sub = meme.get("subreddit", "unknown")

    try:
        await client.send_file(
            event.chat_id, 
            meme_url, 
            caption=f"<b>{title}</b>\n<i>Source: r/{sub}</i>", 
            parse_mode="html"
        )
        await event.delete()
    except Exception as e:
        logger.warning(f"[mem] Failed to send meme from {meme_url}: {e}")
        await handle_mem_universal(event)
        
@command(".gif")
async def handle_gif_cached(event):
    global GIF_CACHE
    
    if not GIF_CACHE:
        gif_subs = [ 'GifsThatStartTooLate', 'aivideo']
        selected_sub = random.choice(gif_subs)
        url = f"https://meme-api.com/gimme/{selected_sub}/50"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        GIF_CACHE = [m for m in data.get("memes", []) if m.get("url")]
                        random.shuffle(GIF_CACHE)
                        logger.info(f"[gif] Кеш оновлено: 50 гіфок з r/{selected_sub}")
                    else:
                        await event.reply("Не вдалося отримати гіфки з сервера.")
                        return
        except Exception as e:
            await event.reply(f"Помилка мережі: {e}")
            return

    if not GIF_CACHE:
        await event.reply("Гіфки закінчилися.")
        return

    gif_item = GIF_CACHE.pop()
    gif_url = gif_item.get("url")
    title = gif_item.get("title", "Random GIF")
    sub = gif_item.get("subreddit", "unknown")

    try:
        await client.send_file(
            event.chat_id, 
            gif_url, 
            caption=f" <b>{title}</b>\n<i>Source: r/{sub}</i>",
            parse_mode="html"
        )
        await event.delete()
    except Exception as e:
        logger.warning(f"[gif] Не вдалося відправити {gif_url}: {e}")
        await handle_gif_cached(event)
@command(".cat")
async def handle_cat(event):
    await event.reply('''/\_/\
( o.o )
 > ^ <''')

@command(".weather")
async def handle_weather(event, *args):
    """
    Погода через OpenWeatherMap API.
    Використання: .weather Київ
    """
    # Встав свій ключ сюди або додай у config.py
    API_KEY = WEATHER_API_KEY
    
    city = " ".join(args) if args else "Ghent"
    
    # URL: units=metric (Цельсій), lang=uk (Українська мова)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=uk"

    await event.edit(f"☁️ Отримую дані для <b>{city}</b>...", parse_mode="html")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 401:
                    await event.edit("❌ <b>Помилка:</b> API ключ ще не активований. Зачекайте годину.")
                    return
                if response.status != 200:
                    await event.edit(f"❌ Місто <b>{city}</b> не знайдено.")
                    return

                data = await response.json()
                
                # Основні дані
                temp = round(data['main']['temp'])
                feels_like = round(data['main']['feels_like'])
                desc = data['weather'][0]['description'].capitalize()
                humidity = data['main']['humidity']
                wind = data['wind']['speed']
                city_name = data['name']
                
                # Емодзі залежно від погоди
                icon = data['weather'][0]['icon']
                emoji_map = {
                    "01": "☀️", "02": "⛅", "03": "☁️", "04": "☁️",
                    "09": "🌧️", "10": "🌦️", "11": "⛈️", "13": "❄️", "50": "🌫️"
                }
                emoji = emoji_map.get(icon[:2], "🌡️")

                res = (
                    f"{emoji} <b>Погода: {city_name}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"📝 {desc}\n"
                    f"🌡 Температура: <code>{temp}°C</code>\n"
                    f"🤔 Відчувається як: <code>{feels_like}°C</code>\n"
                    f"💧 Вологість: <code>{humidity}%</code>\n"
                    f"💨 Вітер: <code>{wind} м/с</code>"
                )
                await event.edit(res, parse_mode="html")

        except Exception as e:
            logger.error(f"[weather] Помилка: {e}")
            await event.edit("❌ Сталася внутрішня помилка при запиті.")

@command(".qweather")
async def handle_quick_weather(event, *args):
    """Погода без API-ключа через wttr.in"""
    city = args[0] if args else "Ghent"
    # Формат ?format=3 видає один рядок: "City: ⛅️ +12°C"
    url = f"https://wttr.in/{city}?format=3"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                text = await response.text()
                await event.edit(f"<code>{text}</code>", parse_mode="html")
            else:
                await event.edit("❌ Не вдалося отримати погоду.")
@command(".uptime")
async def handle_uptime(event):
    uptime = datetime.now() - START_TIME
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    await event.reply(f"⏳ Uptime: {hours}h {minutes}m")
@command(".time")
async def handle_time(event):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await event.reply(f"🕒 Current time:\n<code>{now}</code>", parse_mode="html")

@command(".spin")
async def handle_spin(event): 
    emojis = ["🍎", "🍋", "🍒", "💎", "🔔"]
    for  _ in range(3):
        res = [random.choice(emojis) for _ in range(3)]
        await event.edit(f"║ {' | '.join(res)} ║" )
        await asyncio.sleep(0.4)
    
    final = [random.choice(emojis) for _ in range(3)]
    win = "— YOU WIN! 🎉 —" if len(set(final)) == 1 else "— Try again! —"
    await event.edit(f"║ {' | '.join(final)} ║\n{win}")
    
    
    
@command(".rbuser")
async def handle_rb_user(event, username=None):
    """Отримує інформацію про гравця Roblox за нікнеймом."""
    if not username:
        return await event.edit("❌ Введіть нікнейм: <code>.rbuser Builderman</code>", parse_mode="html")

    await event.edit(f"🔍 Шукаю <b>{username}</b> у базі Roblox...", parse_mode="html")

    try:
        # 1. Отримуємо ID за нікнеймом
        user_req = requests.post("https://users.roblox.com/v1/usernames/users", 
                               json={"usernames": [username], "excludeBannedUsers": False}).json()
        
        if not user_req.get("data"):
            return await event.edit(f"❌ Користувача <b>{username}</b> не знайдено.", parse_mode="html")

        user_id = user_req["data"][0]["id"]
        display_name = user_req["data"][0]["displayName"]

        # 2. Отримуємо детальну інфу
        info = requests.get(f"https://users.roblox.com/v1/users/{user_id}").json()
        created_at = datetime.strptime(info["created"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d.%m.%Y")
        
        # 3. Перевіряємо статус (онлайн/офлайн)
        presence = requests.post("https://presence.roblox.com/v1/presence/users", 
                               json={"userIds": [user_id]}).json()
        status_code = presence["userPresences"][0]["userPresenceType"]
        status_map = {0: "Offline 🔴", 1: "Online 🟢", 2: "In Game 🎮", 3: "In Studio 🛠"}
        status = status_map.get(status_code, "Unknown ❓")

        res = (
            f"🟥 <b>Roblox Profile: {username}</b>\n"
            f"────────────────────\n"
            f"👤 <b>Display Name:</b> {display_name}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"📅 <b>Registered:</b> <code>{created_at}</code>\n"
            f"🌐 <b>Status:</b> {status}\n"
            f"🔗 <a href='https://www.roblox.com/users/{user_id}/profile'>Link to Profile</a>"
        )
        await event.edit(res, parse_mode="html", link_preview=False)

    except Exception as e:
        await event.edit(f"❌ Помилка API: <code>{e}</code>", parse_mode="html")
        


@command(".gpt")
async def handle_gpt(event, *args):
    user_args = " ".join(args).strip()
    reply = await event.get_reply_message()
    reply_text = reply.raw_text.strip() if reply and reply.raw_text else ""

    if user_args and reply_text:
        full_prompt = f"{user_args}\n\nКонтекст:\n{reply_text}"
    elif user_args:
        full_prompt = user_args
    elif reply_text:
        full_prompt = reply_text
    else:
        await event.edit("<b>Напишіть запит або зробіть реплай!</b>", parse_mode="html")
        return

    await event.edit("         .")

    try:
        chat_completion = await groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Ти — швидкий та лаконічний асистент. Відповідай українською мовою."
                },
                {
                    "role": "user",
                    "content": full_prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )

        answer = chat_completion.choices[0].message.content

        header = f"<b>Запит:</b> <i>{html.escape(full_prompt[:50])}...</i>\n\n"
        await event.edit(f"{answer}", parse_mode="html")

    except Exception as e:
        logger.error(f"[groq] Error: {e}")
        await event.edit(f" <b>Помилка Groq:</b>\n<code>{html.escape(str(e))}</code>", parse_mode="html")
@command(".fox")
async def handle_fox(event):
    await event.edit("foxy 🦊")
    async with aiohttp.ClientSession() as session:
        async with session.get("https://randomfox.ca/floof/") as r:
            data = await r.json()
            await client.send_file(event.chat_id, data["image" ], force_document=False)
    await event.delete()
    
@command(".dog")
async def handle_dog(event):
    await event.edit("gaf 🐶")
    async with aiohttp.ClientSession() as session:
        async with session.get("https://dog.ceo/api/breeds/image/random") as r:
            data = await r.json()
            await client.send_file(event.chat_id, data["message" ], force_document=False)
    await event.delete()
    
@command(".turtle")
async def handle_turtle(event):
    await event.edit("turtle 🐢")
    url = f"https://loremflickr.com/1280/720/turtle?lock={random.randint(1, 10000)}"
    await client.send_file(event.chat_id, url, force_document=False)
    await event.delete()
    
@command(".lizard")
async def handle_lizard(event):
    await event.edit("lizard 🐶")
    async with aiohttp.ClientSession() as session:
        async with session.get("https://nekos.life/api/v2/img/lizard") as r:
            data = await r.json()
            await client.send_file(event.chat_id, data["url" ], force_document=False)
    await event.delete()