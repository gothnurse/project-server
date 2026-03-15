# 🏠 HappyPlace — Home Server

> Prywatny serwer domowy na Hetzner CAX21 (ARM64). Blokowanie reklam, VPN, Minecraft, Discord bot i więcej — wszystko zarządzane przez Docker Compose.

![Status](https://img.shields.io/badge/status-active-brightgreen) ![Host](https://img.shields.io/badge/host-Hetzner%20CAX21-red) ![OS](https://img.shields.io/badge/OS-Ubuntu%2024.04-orange) ![Arch](https://img.shields.io/badge/arch-ARM64-blue)

---

## 🗺 Architektura

```
Internet
    │
    ▼
Hetzner CAX21 (ARM64)
    │
    ├── 🛡  Pi-hole        — Blokowanie reklam i trackerów na poziomie DNS   :8080
    ├── 🔒  WireGuard      — VPN do zdalnego dostępu i ochrony               :51820 / :51821
    ├── 🎮  Minecraft      — Serwer PaperMC                                  :25565
    ├── 🤖  Discord Bot    — Aku, własny bot discordowy                      (internal)
    ├── 🐳  Portainer      — GUI do zarządzania Dockerem                     :9443
    └── 🖥  Cockpit        — GUI do zarządzania serwerem                     :9090
```

---

## 📦 Usługi

| Usługa | Obraz | Port | Opis |
|---|---|---|---|
| **Pi-hole** | `pihole/pihole:latest` | `8080` | Blokowanie reklam dla całej sieci |
| **WireGuard** | `wg-easy:latest` | `51820/udp`, `51821` | Serwer VPN z interfejsem webowym |
| **Minecraft** | `itzg/minecraft-server` | `25565` | Serwer PaperMC |
| **Aku (Discord Bot)** | custom build | — | Własny bot discordowy |
| **Portainer** | `portainer-ce:latest` | `9443` | Wizualne zarządzanie Dockerem |
| **Cockpit** | system package | `9090` | Zarządzanie systemem serwera |

---

## 🚀 Instalacja

### Wymagania
- Ubuntu 24.04 LTS
- Docker + Docker Compose
- Użytkownik bez roota z dostępem sudo

### Klonowanie i konfiguracja
```bash
git clone https://github.com/YOUR_USERNAME/home-server.git
cd home-server
cp .env.example .env
nano .env  # uzupełnij hasła i klucze
```

### Uruchomienie wszystkich usług
```bash
docker compose up -d
```

### Sprawdzenie statusu
```bash
docker compose ps
```

---

## ⚙ Konfiguracja

Skopiuj `.env.example` jako `.env` i uzupełnij:

```env
PIHOLE_PASSWORD=twoje_haslo
```

> ⚠ Nigdy nie commituj pliku `.env`. Jest dodany do `.gitignore`.

---

## 🌐 Sieć

Wszystkie usługi działają na izolowanej sieci Docker `server-network`.

**Firewall (iptables)** — otwarte porty:
| Port | Protokół | Usługa |
|---|---|---|
| 22 | TCP | SSH |
| 53 | TCP/UDP | Pi-hole DNS |
| 80 / 443 | TCP | HTTP/HTTPS |
| 8080 | TCP | Pi-hole Web UI |
| 9090 | TCP | Cockpit |
| 9443 | TCP | Portainer |
| 25565 | TCP | Minecraft |
| 51820 | UDP | WireGuard VPN |
| 51821 | TCP | WireGuard Web UI |

---

## 🛡 Pi-hole

Blokowanie reklam przez DNS dla całej sieci domowej — ponad 133 000 zablokowanych domen.

**Używane listy blokad:**
- StevenBlack Unified Hosts
- AdAway
- Domyślne listy Pi-hole

**Panel administracyjny:**
```
http://YOUR_SERVER_IP:8080/admin
```

---

## 🔒 WireGuard

Własny VPN oparty na [wg-easy](https://github.com/wg-easy/wg-easy).

- Połącz się z dowolnego miejsca — cały ruch przechodzi przez serwer
- DNS automatycznie ustawiony na Pi-hole — blokowanie reklam działa też poza domem
- Zarządzanie klientami przez panel webowy pod `:51821`

---

## 🎮 Minecraft

Serwer PaperMC przez [itzg/minecraft-server](https://github.com/itzg/minecraft-server).

```bash
# Dostęp do konsoli serwera
docker exec -it minecraft rcon-cli
```

---

## 🤖 Aku — Discord Bot

Własny bot discordowy inspirowany postacią Aku z serialu Samurai Jack.

**Funkcje:**
- 🪨 `/rps` — Kamień, papier, nożyczki
- 📈 `/akcje <ticker>` — Cena akcji w USD/EUR z wykresem 24h (linia, świece, słupki)
- 🔍 `/sprawdz` — Ręczne sprawdzenie YouTube i Twitch
- 🎥 Automatyczne powiadomienia o nowych filmach (co 10 min)
- 🔴 Automatyczne powiadomienia o streamach (co 2 min)
- 👂 `/sluchaj` — Ogranicz bota do użytkownika lub roli
- 📢 `/kanal` — Ustaw kanał działania bota
- 🔔 `/kanalnotyfikacji` — Ustaw kanał powiadomień
- 😴 `/wylacz` / `/wlacz` — Włącz/wyłącz bota (tylko właściciel)

Szczegółowa dokumentacja w `discord-bot/README.md`.

---

## 🖥 Zarządzanie

**Portainer** — `https://YOUR_SERVER_IP:9443`
Wizualne zarządzanie Dockerem. Uruchamianie/zatrzymywanie kontenerów, logi, wolumeny.

**Cockpit** — `http://YOUR_SERVER_IP:9090`
Pełny przegląd serwera — CPU, pamięć, dysk, logi i terminal w przeglądarce.

---

## 📁 Struktura projektu

```
server/
├── docker-compose.yml
├── .env                  # sekrety (nie commitować!)
├── .env.example
├── .gitignore
├── README.md
├── pihole/               # konfiguracja Pi-hole (nie commitować)
├── wireguard/            # konfiguracja WireGuard (nie commitować)
├── minecraft/            # dane Minecraft (nie commitować)
├── discord-bot/
│   ├── bot.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
└── caddy/                # reverse proxy (w planach)
```

---

## 🗒 Roadmap

- [x] Pi-hole — blokowanie reklam przez DNS
- [x] WireGuard VPN
- [x] Serwer Minecraft
- [x] Portainer + Cockpit
- [x] Discord bot (Aku)
- [ ] Własna strona internetowa
- [ ] Caddy reverse proxy + SSL
- [ ] Własna domena
- [ ] Automatyczne kopie zapasowe

---

## 📄 Licencja

Projekt prywatny — nie przeznaczony do użytku produkcyjnego. Możesz używać jako inspirację. 🙂
