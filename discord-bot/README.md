# Aku — Discord Bot

Bot discordowy inspirowany postacią Aku z serialu Samurai Jack.

## Funkcje

- 🪨 `/rps` — Kamień, papier, nożyczki z Aku
- 📈 `/akcje <ticker>` — Cena akcji w USD/EUR z wykresem 24h
- 🔍 `/sprawdz` — Ręczne sprawdzenie YouTube i Twitch
- 🎥 Automatyczne powiadomienia o nowych filmach (co 10 min)
- 🔴 Automatyczne powiadomienia o streamach (co 2 min)
- 👂 `/sluchaj` — Ogranicz bota do użytkownika/roli
- 📢 `/kanal` — Ustaw kanał działania bota
- 🔔 `/kanalnotyfikacji` — Ustaw kanał powiadomień
- 🖼️ `/avatar` — Zmień avatar bota
- ⚡ `/ustawstatus` — Zmień status bota
- 😴 `/wylacz` / `/wlacz` — Włącz/wyłącz bota (tylko właściciel)

## Instalacja

### Wymagania
- Docker + Docker Compose
- Konta i klucze API: Discord, Alpha Vantage, YouTube Data API v3, Twitch

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

## Struktura plików

```
discord-bot/
├── bot.py              # Główny kod bota
├── requirements.txt    # Zależności Python
├── Dockerfile          # Obraz Docker
├── .env                # Klucze API (nie commitować!)
├── .env.example        # Szablon zmiennych środowiskowych
└── .gitignore          # Ignorowane pliki
```

## Ważne

- Nigdy nie commituj pliku `.env` — zawiera tajne klucze API
- `OWNER_ID` w `bot.py` musi być Twoim Discord User ID
- Alpha Vantage free tier: 25 zapytań/dzień — wykresy mogą przestać działać przy intensywnym użyciu
