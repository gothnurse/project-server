import os
import io
import aiohttp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
from datetime import datetime, timezone, time as dtime
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import tasks
import random

load_dotenv()

# ─── Config ──────────────────────────────────────────────────────────────────
DISCORD_TOKEN        = os.getenv("DISCORD_TOKEN")
ALPHA_VANTAGE_KEY    = os.getenv("ALPHA_VANTAGE_KEY")
YOUTUBE_API_KEY      = os.getenv("YOUTUBE_API_KEY")
TWITCH_CLIENT_ID     = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
GENERAL_CHANNEL_ID   = int(os.getenv("GENERAL_CHANNEL_ID"))
YOUTUBE_HANDLE       = os.getenv("YOUTUBE_CHANNEL_HANDLE")
TWITCH_CHANNEL       = os.getenv("TWITCH_CHANNEL")
TWITCH_USER_TOKEN    = os.getenv("TWITCH_USER_TOKEN")
TWITCH_REFRESH_TOKEN = os.getenv("TWITCH_REFRESH_TOKEN")
YT_CLIENT_ID         = os.getenv("YOUTUBE_CLIENT_ID")
YT_CLIENT_SECRET     = os.getenv("YOUTUBE_CLIENT_SECRET")
YT_ACCESS_TOKEN      = os.getenv("YOUTUBE_ACCESS_TOKEN")
YT_REFRESH_TOKEN     = os.getenv("YOUTUBE_REFRESH_TOKEN")

# ─── Owner ───────────────────────────────────────────────────────────────────
OWNER_ID = 213687728347283456

# ─── Bot Setup ────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class Aku(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.last_youtube_video_id = None
        self.last_twitch_stream_id = None
        self.twitch_access_token   = None
        self.youtube_channel_id    = None
        self.listen_mode           = "all"
        self.listen_user_id        = None
        self.listen_role_id        = None
        self.allowed_channel_id    = None
        self.enabled               = True  # master on/off switch
        self.notification_channel_id = GENERAL_CHANNEL_ID  # can be overridden by /kanalpowoiadomien
        self.twitch_user_token       = TWITCH_USER_TOKEN
        self.yt_access_token         = YT_ACCESS_TOKEN

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Komendy slash zsynchronizowane")

bot = Aku()

# ─── Helpers ─────────────────────────────────────────────────────────────────
async def fetch_json(url, params=None, headers=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as res:
            return await res.json()

async def post_json(url, params=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as res:
            return await res.json()

def is_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.administrator

def can_use_bot(interaction: discord.Interaction) -> bool:
    if bot.listen_mode == "all":
        return True
    if bot.listen_mode == "user":
        return interaction.user.id == bot.listen_user_id
    if bot.listen_mode == "role":
        return any(r.id == bot.listen_role_id for r in interaction.user.roles)
    return True

def in_allowed_channel(interaction: discord.Interaction) -> bool:
    if bot.allowed_channel_id is None:
        return True
    return interaction.channel_id == bot.allowed_channel_id

async def guard(interaction: discord.Interaction) -> bool:
    if not bot.enabled:
        await interaction.response.send_message(
            "Aku śpi. Nie przeszkadzać.",
            ephemeral=True
        )
        return False
    if not in_allowed_channel(interaction):
        channel = bot.get_channel(bot.allowed_channel_id)
        mention = channel.mention if channel else "wyznaczonym kanale"
        await interaction.response.send_message(
            f"Rozkazuję ci udać się na {mention}. Tylko tam moje słowa mają moc.",
            ephemeral=True
        )
        return False
    if not can_use_bot(interaction):
        if bot.listen_mode == "user":
            who = f"<@{bot.listen_user_id}>"
        else:
            who = f"<@&{bot.listen_role_id}>"
        await interaction.response.send_message(
            f"Milcz. Aku słucha teraz tylko {who}.",
            ephemeral=True
        )
        return False
    return True

# ─── Rock Paper Scissors ──────────────────────────────────────────────────────
RPS_EMOJIS = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
RPS_NAMES  = {"rock": "kamień", "paper": "papier", "scissors": "nożyczki"}
RPS_WINS   = {"rock": "scissors", "paper": "rock", "scissors": "paper"}

WIN_MESSAGES = [
    "Tym razem mi się udało. Następnym razem nie będziesz miał tyle szczęścia.",
    "Moje ciemne moce zadziałały. Wygrałem.",
    "Aku nie przegrywa. No, prawie nigdy.",
]
LOSE_MESSAGES = [
    "Niemożliwe. Musiałeś oszukiwać.",
    "To był tylko test. Celowo przegrałem.",
    "Pamiętaj, że to jedyna rzecz, w której mnie pokonasz.",
]
DRAW_MESSAGES = [
    "Remis. Nawet Aku szanuje równowagę... czasem.",
    "Żadne z nas nie wygrywa. To mi odpowiada.",
    "Remis. Wróć i spróbuj znowu.",
]

def play_rps(user_choice: str) -> discord.Embed:
    bot_choice = random.choice(["rock", "paper", "scissors"])
    if user_choice == bot_choice:
        color, title, msg = 0xFFCC00, "🤝 Remis!", random.choice(DRAW_MESSAGES)
    elif RPS_WINS[user_choice] == bot_choice:
        color, title, msg = 0x00FF99, "🎉 Wygrałeś!", random.choice(LOSE_MESSAGES)
    else:
        color, title, msg = 0xFF4444, "😈 Aku wygrywa!", random.choice(WIN_MESSAGES)
    embed = discord.Embed(title=title, description=f"*{msg}*", color=color)
    embed.add_field(name="Twój wybór", value=f"{RPS_EMOJIS[user_choice]} {RPS_NAMES[user_choice]}", inline=True)
    embed.add_field(name="Mój wybór",  value=f"{RPS_EMOJIS[bot_choice]} {RPS_NAMES[bot_choice]}",   inline=True)
    embed.set_footer(text="Zagraj ponownie z /rps — jeśli masz odwagę")
    return embed

# ─── Stock Charts ─────────────────────────────────────────────────────────────
def build_line_chart(dates, closes, ticker, color="#00CC66"):
    fig, ax = plt.subplots(figsize=(8, 3), facecolor="#2b2d31")
    ax.set_facecolor("#2b2d31")
    ax.plot(dates, closes, color=color, linewidth=2)
    ax.fill_between(dates, closes, min(closes), alpha=0.15, color=color)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.tick_params(colors="#aaaaaa", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#444444")
    ax.set_title(f"{ticker} — ostatnie 24h", color="#ffffff", fontsize=11)
    ax.yaxis.set_tick_params(labelcolor="#aaaaaa")
    fig.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf

def build_bar_chart(dates, closes, ticker, color="#00CC66"):
    fig, ax = plt.subplots(figsize=(8, 3), facecolor="#2b2d31")
    ax.set_facecolor("#2b2d31")
    bar_colors = [color if c >= closes[0] else "#FF4444" for c in closes]
    ax.bar(range(len(closes)), closes, color=bar_colors, width=0.8)
    step = max(1, len(dates) // 6)
    ax.set_xticks(range(0, len(dates), step))
    ax.set_xticklabels([d.strftime("%H:%M") for d in dates[::step]], color="#aaaaaa", fontsize=8)
    ax.tick_params(colors="#aaaaaa", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#444444")
    ax.set_title(f"{ticker} — ostatnie 24h", color="#ffffff", fontsize=11)
    ax.yaxis.set_tick_params(labelcolor="#aaaaaa")
    fig.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf

def build_candle_chart(ohlc_data, ticker):
    fig, ax = plt.subplots(figsize=(8, 3), facecolor="#2b2d31")
    ax.set_facecolor("#2b2d31")
    candlestick_ohlc(ax, ohlc_data, width=0.0003, colorup="#00CC66", colordown="#FF4444", alpha=0.9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.tick_params(colors="#aaaaaa", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#444444")
    ax.set_title(f"{ticker} — ostatnie 24h", color="#ffffff", fontsize=11)
    ax.yaxis.set_tick_params(labelcolor="#aaaaaa")
    fig.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf

# ─── Stock Data ───────────────────────────────────────────────────────────────
async def get_stock_data(ticker: str):
    quote_data = await fetch_json(
        "https://www.alphavantage.co/query",
        params={"function": "GLOBAL_QUOTE", "symbol": ticker, "apikey": ALPHA_VANTAGE_KEY}
    )
    quote = quote_data.get("Global Quote", {})
    intraday_data = await fetch_json(
        "https://www.alphavantage.co/query",
        params={
            "function": "TIME_SERIES_INTRADAY",
            "symbol": ticker,
            "interval": "15min",
            "outputsize": "compact",
            "apikey": ALPHA_VANTAGE_KEY
        }
    )
    ts = intraday_data.get("Time Series (15min)", {})
    intraday = []
    for ts_str, vals in sorted(ts.items()):
        dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        intraday.append((dt, float(vals["1. open"]), float(vals["2. high"]), float(vals["3. low"]), float(vals["4. close"])))
    return quote, intraday[-96:]

async def get_fx_rate() -> float:
    fx_data = await fetch_json(
        "https://www.alphavantage.co/query",
        params={"function": "CURRENCY_EXCHANGE_RATE", "from_currency": "USD", "to_currency": "EUR", "apikey": ALPHA_VANTAGE_KEY}
    )
    return float(fx_data.get("Realtime Currency Exchange Rate", {}).get("5. Exchange Rate", 0.92))

async def get_stock_embed_and_chart(ticker: str, chart_type: str):
    try:
        quote, intraday = await get_stock_data(ticker)
        if not quote.get("05. price"):
            embed = discord.Embed(title="❌ Nie znaleziono tickera", color=0xFF4444)
            embed.description = f"Nie ma takiego tickera: **{ticker.upper()}**. Sprawdź czy dobrze wpisałeś."
            return embed, None

        price_usd  = float(quote["05. price"])
        change_usd = float(quote["09. change"])
        change_pct = float(quote["10. change percent"].replace("%", ""))
        fx_rate    = await get_fx_rate()
        price_eur  = price_usd * fx_rate
        change_eur = change_usd * fx_rate

        is_positive = change_usd >= 0
        arrow       = "📈" if is_positive else "📉"
        color       = 0x00CC66 if is_positive else 0xFF4444
        sign        = "+" if is_positive else ""
        chart_color = "#00CC66" if is_positive else "#FF4444"

        embed = discord.Embed(title=f"{arrow} {ticker.upper()}", color=color)
        embed.add_field(name="💵 Cena (USD)",       value=f"${price_usd:.2f}",                               inline=True)
        embed.add_field(name="💶 Cena (EUR)",       value=f"€{price_eur:.2f}",                               inline=True)
        embed.add_field(name="\u200b",              value="\u200b",                                          inline=True)
        embed.add_field(name="📊 Zmiana 24h (USD)", value=f"{sign}${change_usd:.2f} ({sign}{change_pct:.2f}%)", inline=True)
        embed.add_field(name="📊 Zmiana 24h (EUR)", value=f"{sign}€{change_eur:.2f} ({sign}{change_pct:.2f}%)", inline=True)
        embed.add_field(name="\u200b",              value="\u200b",                                          inline=True)
        embed.set_footer(text="Dane z Alpha Vantage • mogą być opóźnione o 15 min")
        embed.timestamp = datetime.now(timezone.utc)

        chart_buf = None
        if intraday:
            dates  = [r[0] for r in intraday]
            closes = [r[4] for r in intraday]
            if chart_type == "line":
                chart_buf = build_line_chart(dates, closes, ticker.upper(), chart_color)
            elif chart_type == "bar":
                chart_buf = build_bar_chart(dates, closes, ticker.upper(), chart_color)
            elif chart_type == "candle":
                ohlc = [(mdates.date2num(r[0]), r[1], r[2], r[3], r[4]) for r in intraday]
                chart_buf = build_candle_chart(ohlc, ticker.upper())
            if chart_buf:
                embed.set_image(url="attachment://wykres.png")

        return embed, chart_buf

    except Exception as e:
        print(f"Błąd akcji: {e}")
        embed = discord.Embed(title="❌ Coś poszło nie tak", color=0xFF4444)
        embed.description = "Nie udało się pobrać danych. Spróbuj za chwilę."
        return embed, None

# ─── Help ─────────────────────────────────────────────────────────────────────
def get_help_embed(admin: bool) -> discord.Embed:
    embed = discord.Embed(title="🌑 Polecenia Aku", color=0x5865F2)
    # Commands available to everyone
    embed.add_field(name="/rps",            value="Zagraj w kamień, papier, nożyczki przeciwko Aku", inline=False)
    embed.add_field(name="/pomoc",          value="Wyświetla tę wiadomość", inline=False)
    # Admin-only commands
    if admin:
        embed.add_field(name="\u200b", value="──────────── **Admin** ────────────", inline=False)
        embed.add_field(name="/akcje <ticker>", value="Sprawdź cenę akcji w USD i EUR ze zmianą 24h + wykres\nNp. `/akcje AAPL`", inline=False)
        embed.add_field(name="/sprawdz",        value="Ręcznie sprawdź czy jest aktywny stream lub nowe wideo", inline=False)
        embed.add_field(name="/sluchaj",     value="Ogranicz bota do użytkownika lub roli\n`@użytkownik`, `@Rola` lub `wszyscy`", inline=False)
        embed.add_field(name="/kanal",       value="Ustaw kanał bota. `/kanal reset` usuwa ograniczenie", inline=False)
        embed.add_field(name="/avatar",      value="Zmień avatar Aku (podaj URL obrazka)", inline=False)
        embed.add_field(name="/ustawstatus", value="Zmień status Aku", inline=False)
        embed.add_field(name="/status",      value="Pokaż aktualne ustawienia bota", inline=False)
        embed.add_field(name="\u200b", value="──────────── **Właściciel** ────────────", inline=False)
        embed.add_field(name="/wylacz",      value="Natychmiast wyłącz bota", inline=False)
        embed.add_field(name="/wlacz",       value="Włącz bota z powrotem", inline=False)
    embed.set_footer(text="Aku • Mistrz Ciemności i władca czasu")
    return embed

# ─── Slash Commands — General ─────────────────────────────────────────────────
@bot.tree.command(name="rps", description="Zagraj w kamień, papier, nożyczki z Aku!")
@app_commands.choices(choice=[
    app_commands.Choice(name="🪨 Kamień",    value="rock"),
    app_commands.Choice(name="📄 Papier",    value="paper"),
    app_commands.Choice(name="✂️ Nożyczki", value="scissors"),
])
async def rps(interaction: discord.Interaction, choice: app_commands.Choice[str]):
    if not await guard(interaction):
        return
    embed = play_rps(choice.value)
    await interaction.response.send_message(embeds=[embed])

@bot.tree.command(name="akcje", description="Sprawdź cenę akcji i zmianę w ostatnich 24h")
@app_commands.describe(
    ticker="Symbol akcji (np. AAPL, TSLA, GOOGL)",
    wykres="Rodzaj wykresu"
)
@app_commands.choices(wykres=[
    app_commands.Choice(name="📈 Linia",   value="line"),
    app_commands.Choice(name="🕯️ Świece", value="candle"),
    app_commands.Choice(name="📊 Słupki",  value="bar"),
])
async def akcje(interaction: discord.Interaction, ticker: str, wykres: app_commands.Choice[str] = None):
    if not await guard(interaction):
        return
    if not is_admin(interaction):
        await interaction.response.send_message(
            "Ta wiedza jest zarezerwowana dla wybranych. Nie dla ciebie.",
            ephemeral=True
        )
        return
    await interaction.response.defer()
    chart_type = wykres.value if wykres else "line"
    embed, chart_buf = await get_stock_embed_and_chart(ticker.upper(), chart_type)
    if chart_buf:
        file = discord.File(chart_buf, filename="wykres.png")
        await interaction.followup.send(embeds=[embed], files=[file])
    else:
        await interaction.followup.send(embeds=[embed])

@bot.tree.command(name="pomoc", description="Lista wszystkich dostępnych poleceń")
async def pomoc(interaction: discord.Interaction):
    if not await guard(interaction):
        return
    admin = is_admin(interaction)
    await interaction.response.send_message(embeds=[get_help_embed(admin)], ephemeral=True)

@bot.tree.command(name="sprawdz", description="Ręcznie sprawdź czy jest aktywny stream lub nowe wideo")
async def sprawdz(interaction: discord.Interaction):
    if not await guard(interaction):
        return
    if not is_admin(interaction):
        await interaction.response.send_message(
            "Nie masz uprawnień by kazać mi sprawdzać cokolwiek.",
            ephemeral=True
        )
        return
    await interaction.response.defer(ephemeral=True)

    lines = []

    # Check YouTube
    try:
        video = await get_latest_youtube_video()
        if video:
            video_id  = video["id"]["videoId"]
            title     = video["snippet"]["title"]
            published = video["snippet"]["publishedAt"]
            dt        = datetime.fromisoformat(published.replace("Z", "+00:00"))
            is_new    = video_id != bot.last_youtube_video_id
            prefix    = "🆕 **Nowe wideo!**" if is_new else "🎥 **Ostatnie wideo:**"
            lines.append(f"{prefix} [{title}](https://www.youtube.com/watch?v={video_id})\n📅 Opublikowane: <t:{int(dt.timestamp())}:R>")
        else:
            lines.append("🎥 Nie udało się pobrać wideo z YouTube.")
    except Exception as e:
        lines.append(f"🎥 Błąd sprawdzania YouTube: {e}")

    # Check Twitch
    try:
        if not bot.twitch_access_token:
            await get_twitch_token()
        data = await fetch_json(
            "https://api.twitch.tv/helix/streams",
            params  = {"user_login": TWITCH_CHANNEL},
            headers = {"Client-ID": TWITCH_CLIENT_ID, "Authorization": f"Bearer {bot.twitch_access_token}"}
        )
        streams = data.get("data", [])
        if streams:
            s = streams[0]
            lines.append(f"🔴 **Twitch — na żywo teraz!**\n🎮 Gra w: {s['game_name']} • 👀 {s['viewer_count']} widzów\n🔗 [Oglądaj](https://twitch.tv/{TWITCH_CHANNEL})")
        else:
            lines.append(f"⚫ **Twitch:** Nie ma aktywnego streamu.")
    except Exception as e:
        lines.append(f"⚫ Błąd sprawdzania Twitcha: {e}")

    embed = discord.Embed(title="🔍 Sprawdzam...", description="\n\n".join(lines), color=0x5865F2)
    embed.set_footer(text="Aku sprawdził wszystko w twoim imieniu.")
    await interaction.followup.send(embeds=[embed], ephemeral=True)

# ─── Slash Commands — Admin ───────────────────────────────────────────────────
@bot.tree.command(name="sluchaj", description="[Admin] Ogranicz bota do użytkownika, roli lub przywróć wszystkich")
@app_commands.describe(cel="wszyscy = wszyscy, @użytkownik lub @Rola")
async def sluchaj(interaction: discord.Interaction, cel: str):
    if not in_allowed_channel(interaction):
        channel = bot.get_channel(bot.allowed_channel_id)
        mention = channel.mention if channel else "wyznaczonym kanale"
        await interaction.response.send_message(
            f"Rozkazuję ci udać się na {mention}. Tylko tam moje słowa mają moc.",
            ephemeral=True
        )
        return
    if not is_admin(interaction):
        await interaction.response.send_message("Nie masz wystarczającej władzy, by mi wydawać rozkazy.", ephemeral=True)
        return
    if cel.lower() in ("wszyscy", "all"):
        bot.listen_mode = "all"
        bot.listen_user_id = None
        bot.listen_role_id = None
        await interaction.response.send_message("Dobrze. Będę znowu słuchał wszystkich... na razie.", ephemeral=True)
        return
    if cel.startswith("<@") and not cel.startswith("<@&"):
        user_id = int(cel.strip("<@!>"))
        bot.listen_mode = "user"
        bot.listen_user_id = user_id
        bot.listen_role_id = None
        await interaction.response.send_message(f"Rozumiem. Od teraz słucham tylko <@{user_id}>. Reszta może milczeć.", ephemeral=True)
        return
    if cel.startswith("<@&"):
        role_id = int(cel.strip("<@&>"))
        bot.listen_mode = "role"
        bot.listen_role_id = role_id
        bot.listen_user_id = None
        await interaction.response.send_message(f"Rozumiem. Od teraz słucham tylko <@&{role_id}>. Reszta nie istnieje.", ephemeral=True)
        return
    await interaction.response.send_message("Nie rozpoznaję tego rozkazu. Użyj `wszyscy`, `@użytkownik` lub `@Rola`.", ephemeral=True)

@bot.tree.command(name="kanal", description="[Admin] Ustaw kanał dla bota lub usuń ograniczenie")
@app_commands.describe(reset="Wpisz 'reset' żeby usunąć ograniczenie kanału")
async def kanal(interaction: discord.Interaction, reset: str = ""):
    if not is_admin(interaction):
        await interaction.response.send_message("Nie masz wystarczającej władzy, by mi wydawać rozkazy.", ephemeral=True)
        return
    if reset.lower() == "reset":
        bot.allowed_channel_id = None
        await interaction.response.send_message("Ograniczenie kanału usunięte. Będę działał wszędzie.", ephemeral=True)
        return
    bot.allowed_channel_id = interaction.channel_id
    await interaction.response.send_message("Ten kanał stał się moją twierdzą. Na innych moje słowa nie będą słyszane.", ephemeral=True)

@bot.tree.command(name="avatar", description="[Admin] Zmień avatar Aku")
@app_commands.describe(url="URL obrazka (png/jpg)")
async def avatar(interaction: discord.Interaction, url: str):
    if not is_admin(interaction):
        await interaction.response.send_message("Nie masz wystarczającej władzy, by mi wydawać rozkazy.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await interaction.followup.send("Nie udało się pobrać obrazka. Sprawdź URL.", ephemeral=True)
                    return
                img_data = await resp.read()
        await bot.user.edit(avatar=img_data)
        await interaction.followup.send("Moja nowa twarz jest... odpowiednia.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"Discord odrzucił zmianę: {e}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Błąd: {e}", ephemeral=True)

@bot.tree.command(name="ustawstatus", description="[Admin] Zmień status Aku")
@app_commands.describe(tekst="Tekst statusu", typ="Rodzaj aktywności")
@app_commands.choices(typ=[
    app_commands.Choice(name="🎮 Gra w",  value="playing"),
    app_commands.Choice(name="👀 Ogląda", value="watching"),
    app_commands.Choice(name="🎧 Słucha", value="listening"),
    app_commands.Choice(name="⚡ Własny", value="custom"),
])
async def ustawstatus(interaction: discord.Interaction, tekst: str, typ: app_commands.Choice[str] = None):
    if not is_admin(interaction):
        await interaction.response.send_message("Nie masz wystarczającej władzy, by mi wydawać rozkazy.", ephemeral=True)
        return
    activity_type = typ.value if typ else "custom"
    if activity_type == "playing":
        activity = discord.Game(name=tekst)
    elif activity_type == "watching":
        activity = discord.Activity(type=discord.ActivityType.watching, name=tekst)
    elif activity_type == "listening":
        activity = discord.Activity(type=discord.ActivityType.listening, name=tekst)
    else:
        activity = discord.CustomActivity(name=tekst)
    await bot.change_presence(activity=activity)
    await interaction.response.send_message("Status zmieniony. Niech wszyscy wiedzą.", ephemeral=True)

@bot.tree.command(name="status", description="[Admin] Pokaż aktualne ustawienia bota")
async def status_cmd(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("Nie masz wystarczającej władzy, by wiedzieć zbyt wiele.", ephemeral=True)
        return
    embed = discord.Embed(title="🌑 Status Aku", color=0x5865F2)
    if bot.allowed_channel_id:
        ch = bot.get_channel(bot.allowed_channel_id)
        ch_val = ch.mention if ch else f"ID: {bot.allowed_channel_id}"
    else:
        ch_val = "Wszystkie kanały"
    embed.add_field(name="📢 Aktywny kanał", value=ch_val, inline=False)
    if bot.listen_mode == "all":
        listen_val = "Wszyscy"
    elif bot.listen_mode == "user":
        listen_val = f"<@{bot.listen_user_id}>"
    else:
        listen_val = f"<@&{bot.listen_role_id}>"
    embed.add_field(name="👂 Słucha", value=listen_val, inline=False)
    embed.add_field(name="⚡ Stan", value="✅ Aktywny" if bot.enabled else "😴 Wyłączony", inline=False)
    embed.set_footer(text="Aku • Mistrz Ciemności i władca czasu")
    await interaction.response.send_message(embeds=[embed], ephemeral=True)


@bot.tree.command(name="kanalnotyfikacji", description="[Admin] Ustaw kanał na powiadomienia o filmach i streamach")
@app_commands.describe(reset="Wpisz 'reset' żeby wrócić do domyślnego kanału")
async def kanalnotyfikacji(interaction: discord.Interaction, reset: str = ""):
    if not is_admin(interaction):
        await interaction.response.send_message("Nie masz wystarczającej władzy, by mi wydawać rozkazy.", ephemeral=True)
        return
    if reset.lower() == "reset":
        bot.notification_channel_id = GENERAL_CHANNEL_ID
        ch = bot.get_channel(GENERAL_CHANNEL_ID)
        mention = ch.mention if ch else f"ID: {GENERAL_CHANNEL_ID}"
        await interaction.response.send_message(
            f"Powiadomienia wróciły na domyślny kanał: {mention}.",
            ephemeral=True
        )
        return
    bot.notification_channel_id = interaction.channel_id
    await interaction.response.send_message(
        "Ten kanał będzie odtąd otrzymywał powiadomienia o filmach i streamach.",
        ephemeral=True
    )


@bot.tree.command(name="wylacz", description="[Właściciel] Wyłącz bota — będzie ignorował wszystkie komendy")
async def wylacz(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "Nie masz wystarczającej władzy, by mnie uśpić.",
            ephemeral=True
        )
        return
    if not bot.enabled:
        await interaction.response.send_message("Już śpię.", ephemeral=True)
        return
    bot.enabled = False
    await interaction.response.send_message(
        "Aku zasypia. Wzbudź mnie gdy będzie trzeba.",
        ephemeral=True
    )
    print("⚠️ Bot wyłączony przez właściciela")

@bot.tree.command(name="wlacz", description="[Właściciel] Włącz bota")
async def wlacz(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "Nie masz wystarczającej władzy, by mnie obudzić.",
            ephemeral=True
        )
        return
    if bot.enabled:
        await interaction.response.send_message("Już jestem aktywny.", ephemeral=True)
        return
    bot.enabled = True
    await interaction.response.send_message(
        "Aku przebudził się. Biada tym, którzy narobili szkód pod moją nieobecność.",
        ephemeral=True
    )
    print("✅ Bot włączony przez właściciela")


# ─── Stream Management ────────────────────────────────────────────────────────

async def refresh_twitch_user_token():
    """Refresh Twitch user OAuth token."""
    data = await post_json(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id":     TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET,
            "refresh_token": TWITCH_REFRESH_TOKEN,
            "grant_type":    "refresh_token"
        }
    )
    if "access_token" in data:
        bot.twitch_user_token = data["access_token"]
        print("✅ Twitch user token odświeżony")
        return True
    print(f"❌ Błąd odświeżania Twitch token: {data}")
    return False

async def refresh_youtube_token():
    """Refresh YouTube OAuth token."""
    data = await post_json(
        "https://oauth2.googleapis.com/token",
        params={
            "client_id":     YT_CLIENT_ID,
            "client_secret": YT_CLIENT_SECRET,
            "refresh_token": YT_REFRESH_TOKEN,
            "grant_type":    "refresh_token"
        }
    )
    if "access_token" in data:
        bot.yt_access_token = data["access_token"]
        print("✅ YouTube token odświeżony")
        return True
    print(f"❌ Błąd odświeżania YouTube token: {data}")
    return False

async def get_twitch_user_id() -> str | None:
    """Get Twitch user ID for the channel."""
    data = await fetch_json(
        "https://api.twitch.tv/helix/users",
        params  = {"login": TWITCH_CHANNEL},
        headers = {
            "Client-ID":     TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {bot.twitch_user_token}"
        }
    )
    return data.get("data", [{}])[0].get("id")

async def get_twitch_game_id(game_name: str) -> str | None:
    """Get Twitch game/category ID by name."""
    data = await fetch_json(
        "https://api.twitch.tv/helix/games",
        params  = {"name": game_name},
        headers = {
            "Client-ID":     TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {bot.twitch_user_token}"
        }
    )
    return data.get("data", [{}])[0].get("id")

async def get_youtube_broadcast_id() -> str | None:
    """Get active or upcoming YouTube broadcast ID."""
    data = await fetch_json(
        "https://www.googleapis.com/youtube/v3/liveBroadcasts",
        params  = {"part": "id,snippet", "broadcastStatus": "active", "broadcastType": "all"},
        headers = {"Authorization": f"Bearer {bot.yt_access_token}"}
    )
    items = data.get("items", [])
    if items:
        return items[0]["id"]
    # Try upcoming if no active
    data2 = await fetch_json(
        "https://www.googleapis.com/youtube/v3/liveBroadcasts",
        params  = {"part": "id,snippet", "broadcastStatus": "upcoming", "broadcastType": "all"},
        headers = {"Authorization": f"Bearer {bot.yt_access_token}"}
    )
    items2 = data2.get("items", [])
    return items2[0]["id"] if items2 else None

async def set_twitch_stream(title: str, game_name: str) -> tuple[bool, str]:
    """Update Twitch stream title and category. Returns (success, message)."""
    try:
        # Get user ID
        user_id = await get_twitch_user_id()
        if not user_id:
            # Try refreshing token
            await refresh_twitch_user_token()
            user_id = await get_twitch_user_id()
        if not user_id:
            return False, "Nie udało się pobrać ID kanału Twitch."

        # Get game ID
        game_id = await get_twitch_game_id(game_name)
        if not game_id:
            return False, f"Nie znaleziono kategorii **{game_name}** na Twitchu. Sprawdź czy nazwa jest dokładna."

        # Update channel info
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"https://api.twitch.tv/helix/channels?broadcaster_id={user_id}",
                json    = {"title": title, "game_id": game_id},
                headers = {
                    "Client-ID":     TWITCH_CLIENT_ID,
                    "Authorization": f"Bearer {bot.twitch_user_token}",
                    "Content-Type":  "application/json"
                }
            ) as resp:
                if resp.status == 204:
                    return True, f"Twitch ✅"
                elif resp.status == 401:
                    await refresh_twitch_user_token()
                    return False, "Token Twitch wygasł — odświeżono, spróbuj ponownie."
                else:
                    text = await resp.text()
                    return False, f"Twitch błąd {resp.status}: {text}"
    except Exception as e:
        return False, f"Twitch wyjątek: {e}"

async def set_youtube_stream(title: str, game_name: str) -> tuple[bool, str]:
    """Update YouTube live broadcast title and description. Returns (success, message)."""
    try:
        broadcast_id = await get_youtube_broadcast_id()
        if not broadcast_id:
            await refresh_youtube_token()
            broadcast_id = await get_youtube_broadcast_id()
        if not broadcast_id:
            return False, "Nie znaleziono aktywnej ani nadchodzącej transmisji na YouTube."

        async with aiohttp.ClientSession() as session:
            async with session.put(
                "https://www.googleapis.com/youtube/v3/liveBroadcasts?part=snippet",
                json    = {
                    "id": broadcast_id,
                    "snippet": {
                        "title":              title,
                        "scheduledStartTime": datetime.now(timezone.utc).isoformat(),
                        "description":        f"Gram w: {game_name}"
                    }
                },
                headers = {
                    "Authorization": f"Bearer {bot.yt_access_token}",
                    "Content-Type":  "application/json"
                }
            ) as resp:
                if resp.status == 200:
                    return True, "YouTube ✅"
                elif resp.status == 401:
                    await refresh_youtube_token()
                    return False, "Token YouTube wygasł — odświeżono, spróbuj ponownie."
                else:
                    text = await resp.text()
                    return False, f"YouTube błąd {resp.status}: {text}"
    except Exception as e:
        return False, f"YouTube wyjątek: {e}"

@bot.tree.command(name="ustawstream", description="[Admin] Ustaw tytuł i kategorię transmisji na Twitchu i/lub YouTube")
@app_commands.describe(
    tytul="Tytuł transmisji",
    kategoria="Nazwa gry lub kategorii (np. Minecraft, Just Chatting)",
    platforma="Na której platformie ustawić"
)
@app_commands.choices(platforma=[
    app_commands.Choice(name="🟣 Twitch + 🔴 YouTube", value="both"),
    app_commands.Choice(name="🟣 Tylko Twitch",        value="twitch"),
    app_commands.Choice(name="🔴 Tylko YouTube",       value="youtube"),
])
async def ustawstream(interaction: discord.Interaction, tytul: str, kategoria: str, platforma: app_commands.Choice[str] = None):
    if not is_admin(interaction):
        await interaction.response.send_message(
            "Nie masz wystarczającej władzy, by mi wydawać rozkazy.",
            ephemeral=True
        )
        return
    await interaction.response.defer(ephemeral=True)

    platform = platforma.value if platforma else "both"
    results  = []

    if platform in ("both", "twitch"):
        ok, msg = await set_twitch_stream(tytul, kategoria)
        results.append(msg)

    if platform in ("both", "youtube"):
        ok, msg = await set_youtube_stream(tytul, kategoria)
        results.append(msg)

    summary = "\n".join(results)
    embed = discord.Embed(
        title       = "📡 Aktualizacja transmisji",
        description = f"**Tytuł:** {tytul}\n**Kategoria:** {kategoria}\n\n{summary}",
        color       = 0x9146FF
    )
    embed.set_footer(text="Aku zaktualizował transmisję")
    await interaction.followup.send(embeds=[embed], ephemeral=True)

# ─── YouTube ──────────────────────────────────────────────────────────────────
async def resolve_youtube_channel_id():
    try:
        data = await fetch_json(
            "https://www.googleapis.com/youtube/v3/channels",
            params={"part": "id", "forHandle": YOUTUBE_HANDLE, "key": YOUTUBE_API_KEY}
        )
        channel_id = data.get("items", [{}])[0].get("id")
        if channel_id:
            bot.youtube_channel_id = channel_id
            print(f"✅ YouTube channel ID: {channel_id}")
    except Exception as e:
        print(f"Błąd YouTube resolve: {e}")

async def get_latest_youtube_video():
    if not bot.youtube_channel_id:
        return None
    data = await fetch_json(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "part": "snippet",
            "channelId": bot.youtube_channel_id,
            "maxResults": 1,
            "order": "date",
            "type": "video",
            "key": YOUTUBE_API_KEY
        }
    )
    return data.get("items", [None])[0]

@tasks.loop(time=dtime(hour=16, minute=0, tzinfo=timezone.utc))  # 18:00 CET / 17:00 CEST
async def check_youtube():
    try:
        video = await get_latest_youtube_video()
        if not video:
            return
        video_id = video["id"]["videoId"]
        if video_id == bot.last_youtube_video_id:
            return
        bot.last_youtube_video_id = video_id
        snippet      = video["snippet"]
        title        = snippet["title"]
        description  = snippet.get("description", "")[:200]
        channel_name = snippet["channelTitle"]
        published_at = snippet["publishedAt"]
        thumbnail    = snippet["thumbnails"]["high"]["url"]
        channel = bot.get_channel(bot.notification_channel_id)
        if not channel:
            return
        embed = discord.Embed(
            title       = f"🎥 Nowe wideo — {channel_name}",
            description = f"**{title}**\n\n{description}...",
            url         = f"https://www.youtube.com/watch?v={video_id}",
            color       = 0xFF0000
        )
        embed.set_image(url=thumbnail)
        embed.set_footer(text="YouTube")
        embed.timestamp = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        await channel.send(content="@everyone nowe wideo właśnie wylądowało 🎬", embeds=[embed])
    except Exception as e:
        print(f"Błąd sprawdzania YouTube: {e}")

# ─── Twitch ───────────────────────────────────────────────────────────────────
async def get_twitch_token():
    data = await post_json(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
    )
    bot.twitch_access_token = data.get("access_token")
    print("✅ Token Twitch uzyskany")

@tasks.loop(minutes=2)
async def check_twitch():
    try:
        if not bot.twitch_access_token:
            await get_twitch_token()
        data = await fetch_json(
            "https://api.twitch.tv/helix/streams",
            params  = {"user_login": TWITCH_CHANNEL},
            headers = {"Client-ID": TWITCH_CLIENT_ID, "Authorization": f"Bearer {bot.twitch_access_token}"}
        )
        streams = data.get("data", [])
        if not streams:
            bot.last_twitch_stream_id = None
            return
        stream = streams[0]
        if stream["id"] == bot.last_twitch_stream_id:
            return
        bot.last_twitch_stream_id = stream["id"]
        channel = bot.get_channel(bot.notification_channel_id)
        if not channel:
            return
        thumbnail = stream["thumbnail_url"].replace("{width}", "1280").replace("{height}", "720")
        embed = discord.Embed(
            title       = f"🔴 {stream['user_name']} jest na żywo na Twitchu!",
            description = f"**{stream['title']}**\n\nGra w: {stream['game_name']}",
            url         = f"https://twitch.tv/{TWITCH_CHANNEL}",
            color       = 0x9146FF
        )
        embed.set_image(url=thumbnail)
        embed.add_field(name="👀 Widzów", value=str(stream["viewer_count"]), inline=True)
        embed.add_field(name="🎮 Gra",    value=stream["game_name"],         inline=True)
        embed.set_footer(text="Twitch")
        embed.timestamp = datetime.now(timezone.utc)
        await channel.send(content="@everyone stream właśnie się zaczął, chodźcie! 🎮", embeds=[embed])
    except Exception as e:
        if "401" in str(e):
            bot.twitch_access_token = None
        print(f"Błąd sprawdzania Twitcha: {e}")

# ─── On Ready ─────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Aku przebudził się jako {bot.user} (ID: {bot.user.id})")
    await resolve_youtube_channel_id()
    await get_twitch_token()
    video = await get_latest_youtube_video()
    if video:
        bot.last_youtube_video_id = video["id"]["videoId"]
        print(f"✅ YouTube zainicjowany: {bot.last_youtube_video_id}")
    check_youtube.start()
    check_twitch.start()
    print("✅ Obserwatorzy uruchomieni — Aku czuwa")

# ─── Run ──────────────────────────────────────────────────────────────────────
bot.run(DISCORD_TOKEN)
