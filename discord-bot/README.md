# 🌑 Aku — Discord Bot

> Bot discordowy inspirowany postacią Aku z serialu Samurai Jack. Napisany w Pythonie, hostowany na Hetzner CAX21.

---

## Funkcje

### Dla wszystkich
- 🪨 `/rps` — Kamień, papier, nożyczki z Aku
- ❓ `/pomoc` — Lista dostępnych poleceń

### Tylko Admin
- 📈 `/akcje <ticker>` — Cena akcji w USD/EUR z wykresem 24h (linia, świece, słupki)
- 🔍 `/sprawdz` — Ręczne sprawdzenie YouTube i Twitch
- 📡 `/ustawstream` — Ustaw tytuł i kategorię transmisji na Twitchu i/lub YouTube
- 👂 `/sluchaj` — Ogranicz bota do użytkownika lub roli (`@użytkownik`, `@Rola`, `wszyscy`)
- 📢 `/kanal` — Ustaw kanał działania bota (`/kanal reset` usuwa ograniczenie)
- 🔔 `/kanalnotyfikacji` — Ustaw kanał powiadomień YT/Twitch
- 🖼️ `/avatar <url>` — Zmień avatar bota
- ⚡ `/ustawstatus` — Zmień status bota (gra w / ogląda / słucha / własny)
- 📊 `/status` — Pokaż aktualne ustawienia bota

### Tylko właściciel
- 😴 `/wylacz` — Wyłącz bota natychmiast
- ✅ `/wlacz` — Włącz bota z powrotem

### Automatyczne
- 🎥 Powiadomienia o nowych filmach YouTube (raz dziennie o 18:00 CET)
- 🔴 Powiadomienia o streamach Twitch (co 2 minuty)

---

## Instalacja

### Wymagania
- Docker + Docker Compose
- Klucze API: Discord, Alpha Vantage, YouTube Data API v3, Twitch
- OAuth tokens: Twitch (channel:manage:broadcast), YouTube (youtube.force-ssl)

### Konfiguracja

1. Skopiuj `.env.example` jako `.env`:
   ```bash
   cp .env.example .env
   ```

2. Uzupełnij wszystkie wartości w `.env`

3. W `bot.py` zmień `OWNER_ID` na swoje Discord User ID

### Uruchomienie

```bash
docker compose up -d --build discord-bot
```

### Logi

```bash
docker logs discord-bot -f
```

---

## Zmienne środowiskowe

| Zmienna | Opis |
|---|---|
| `DISCORD_TOKEN` | Token bota Discord |
| `ALPHA_VANTAGE_KEY` | Klucz API Alpha Vantage (akcje) |
| `YOUTUBE_API_KEY` | Klucz API YouTube Data v3 (powiadomienia) |
| `TWITCH_CLIENT_ID` | Client ID aplikacji Twitch |
| `TWITCH_CLIENT_SECRET` | Client Secret aplikacji Twitch |
| `TWITCH_USER_TOKEN` | OAuth token użytkownika Twitch (zarządzanie kanałem) |
| `TWITCH_REFRESH_TOKEN` | Refresh token Twitch |
| `YOUTUBE_CLIENT_ID` | OAuth Client ID Google |
| `YOUTUBE_CLIENT_SECRET` | OAuth Client Secret Google |
| `YOUTUBE_ACCESS_TOKEN` | OAuth Access Token YouTube |
| `YOUTUBE_REFRESH_TOKEN` | OAuth Refresh Token YouTube |
| `GENERAL_CHANNEL_ID` | ID domyślnego kanału Discord |
| `YOUTUBE_CHANNEL_HANDLE` | Handle kanału YouTube (np. `@agis_`) |
| `TWITCH_CHANNEL` | Nazwa kanału Twitch (np. `agis`) |

---

## Limity API

| API | Limit | Uwagi |
|---|---|---|
| Alpha Vantage | 25 req/dzień | Każde `/akcje` = 2 req |
| YouTube Data API | 10 000 units/dzień | `/sprawdz` = 100 units |
| YouTube OAuth | Token ważny 7 dni | Odświeżaj co tydzień ręcznie |
| Twitch API | 800 req/min | Praktycznie bez limitu |
| Discord API | 5 req/5s | Bot nie przekracza |

---

## Struktura plików

```
discord-bot/
├── bot.py              # Główny kod bota
├── requirements.txt    # Zależności Python
├── Dockerfile          # Obraz Docker
├── .env                # Klucze API (nie commitować!)
├── .env.example        # Szablon zmiennych środowiskowych
├── .gitignore          # Ignorowane pliki
└── README.md           # Ta dokumentacja
```

---

## Ważne

- Nigdy nie commituj pliku `.env` — zawiera tajne klucze API
- `OWNER_ID` w `bot.py` musi być Twoim Discord User ID
- YouTube OAuth token wygasa co 7 dni — odświeżaj ręcznie do czasu weryfikacji Google
- Stan bota (`/sluchaj`, `/kanal`) resetuje się przy restarcie kontenera — nie jest zapisywany na dysk
- Alpha Vantage free tier: 25 zapytań/dzień — `/akcje` i `/sprawdz` są tylko dla adminów
