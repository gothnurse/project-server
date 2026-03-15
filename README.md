# 🏠 HappyPlace — Home Server

> 🇵🇱 [Polski](#-happyplace--serwer-domowy) | 🇬🇧 [English](#-happyplace--home-server-1)

---

# 🏠 HappyPlace — Serwer Domowy

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
- 📈 `/akcje <ticker>` — Cena akcji w USD/EUR z wykresem 24h
- 🔍 `/sprawdz` — Ręczne sprawdzenie YouTube i Twitch
- 🎥 Automatyczne powiadomienia o nowych filmach i streamach
- 👂 `/sluchaj` — Ogranicz bota do użytkownika lub roli
- 😴 `/wylacz` / `/wlacz` — Włącz/wyłącz bota (tylko właściciel)

Szczegółowa dokumentacja w `discord-bot/README.md`.

---

## 🖥 Zarządzanie

**Portainer** — `https://YOUR_SERVER_IP:9443`
Wizualne zarządzanie Dockerem.

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
├── pihole/
├── wireguard/
├── minecraft/
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

---
---

# 🏠 HappyPlace — Home Server

> Personal home server running on Hetzner CAX21 (ARM64). Self-hosted ad blocking, VPN, Minecraft, Discord bot and more — all managed via Docker Compose.

---

## 🗺 Architecture

```
Internet
    │
    ▼
Hetzner CAX21 (ARM64)
    │
    ├── 🛡  Pi-hole        — DNS-level ad & tracker blocking    :8080
    ├── 🔒  WireGuard      — VPN for remote access & protection :51820 / :51821
    ├── 🎮  Minecraft      — PaperMC game server                :25565
    ├── 🤖  Discord Bot    — Aku, custom Discord bot            (internal)
    ├── 🐳  Portainer      — Docker management GUI              :9443
    └── 🖥  Cockpit        — Server management GUI              :9090
```

---

## 📦 Services

| Service | Image | Port | Description |
|---|---|---|---|
| **Pi-hole** | `pihole/pihole:latest` | `8080` | Network-wide ad blocking |
| **WireGuard** | `wg-easy:latest` | `51820/udp`, `51821` | VPN server with web UI |
| **Minecraft** | `itzg/minecraft-server` | `25565` | PaperMC server |
| **Aku (Discord Bot)** | custom build | — | Personal Discord bot |
| **Portainer** | `portainer-ce:latest` | `9443` | Docker management UI |
| **Cockpit** | system package | `9090` | Server system UI |

---

## 🚀 Setup

### Prerequisites
- Ubuntu 24.04 LTS
- Docker + Docker Compose
- A non-root user with sudo access

### Clone & configure
```bash
git clone https://github.com/YOUR_USERNAME/home-server.git
cd home-server
cp .env.example .env
nano .env  # fill in your passwords and keys
```

### Start all services
```bash
docker compose up -d
```

### Check status
```bash
docker compose ps
```

---

## ⚙ Configuration

Copy `.env.example` to `.env` and fill in:

```env
PIHOLE_PASSWORD=your_password
```

> ⚠ Never commit your `.env` file. It's listed in `.gitignore`.

---

## 🌐 Network

All services run on an isolated Docker bridge network `server-network`.

**Firewall (iptables)** — open ports:

| Port | Protocol | Service |
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

Network-wide DNS ad blocking with 133,000+ blocked domains.

**Blocklists used:**
- StevenBlack Unified Hosts
- AdAway
- Default Pi-hole lists

**Access dashboard:**
```
http://YOUR_SERVER_IP:8080/admin
```

---

## 🔒 WireGuard

Self-hosted VPN using [wg-easy](https://github.com/wg-easy/wg-easy).

- Connect from anywhere and route all traffic through your server
- DNS automatically set to Pi-hole — ad blocking works on the go too
- Manage clients via web UI at `:51821`

---

## 🎮 Minecraft

PaperMC server via [itzg/minecraft-server](https://github.com/itzg/minecraft-server).

```bash
# Access server console
docker exec -it minecraft rcon-cli
```

---

## 🤖 Aku — Discord Bot

Custom Discord bot inspired by Aku from the Cartoon Network show Samurai Jack.

**Features:**
- 🪨 `/rps` — Rock Paper Scissors
- 📈 `/akcje <ticker>` — Stock price in USD/EUR with 24h chart
- 🔍 `/sprawdz` — Manually check YouTube and Twitch
- 🎥 Automatic notifications for new videos and streams
- 👂 `/sluchaj` — Restrict bot to a specific user or role
- 😴 `/wylacz` / `/wlacz` — Enable/disable bot (owner only)

Full documentation in `discord-bot/README.md`.

---

## 🖥 Management

**Portainer** — `https://YOUR_SERVER_IP:9443`
Visual Docker management. Start/stop containers, view logs, manage volumes.

**Cockpit** — `http://YOUR_SERVER_IP:9090`
Full server overview — CPU, memory, disk, logs, and a browser-based terminal.

---

## 📁 Project Structure

```
server/
├── docker-compose.yml
├── .env                  # secrets (not committed)
├── .env.example
├── .gitignore
├── README.md
├── pihole/
├── wireguard/
├── minecraft/
├── discord-bot/
│   ├── bot.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
└── caddy/                # reverse proxy (planned)
```

---

## 🗒 Roadmap

- [x] Pi-hole DNS ad blocking
- [x] WireGuard VPN
- [x] Minecraft server
- [x] Portainer + Cockpit
- [x] Discord bot (Aku)
- [ ] Personal website
- [ ] Caddy reverse proxy + SSL
- [ ] Custom domain
- [ ] Automated backups

---

## 📄 License

Personal project — not intended for production use. Feel free to use as inspiration. 🙂
