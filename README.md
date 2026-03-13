# 🏠 HappyPlace — Home Server

> Personal home server running on Hetzner CAX21 (ARM64). Self-hosted ad blocking, VPN, Minecraft, and more — all managed via Docker Compose.

![Status](https://img.shields.io/badge/status-active-brightgreen) ![Host](https://img.shields.io/badge/host-Hetzner%20CAX21-red) ![OS](https://img.shields.io/badge/OS-Ubuntu%2024.04-orange) ![Arch](https://img.shields.io/badge/arch-ARM64-blue)

---

## 🗺️ Architecture

```
Internet
    │
    ▼
Your VPS or Local Machine
    │
    ├── 🛡️  Pi-hole        — DNS-level ad & tracker blocking   :8080
    ├── 🔒  WireGuard      — VPN for remote access & protection :51820 / :51821
    ├── 🎮  Minecraft      — PaperMC game server               :25565
    ├── 🤖  Discord Bot    — Custom bot                        (internal)
    ├── 🐳  Portainer      — Docker management GUI             :9443
    └── 🖥️  Cockpit        — Server management GUI             :9090
```

---

## 📦 Services

| Service | Image | Port | Description |
|---|---|---|---|
| **Pi-hole** | `pihole/pihole:latest` | `8080` | Network-wide ad blocking |
| **WireGuard** | `wg-easy:latest` | `51820/udp`, `51821` | VPN server with web UI |
| **Minecraft** | `itzg/minecraft-server` | `25565` | PaperMC server |
| **Discord Bot** | custom build | — | Personal Discord bot |
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
# Edit .env and fill in your passwords
nano .env
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

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in:

```env
PIHOLE_PASSWORD=your_pihole_password
```

> ⚠️ Never commit your `.env` file. It's listed in `.gitignore`.

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

## 🛡️ Pi-hole

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

Self-hosted VPN using [wg-easy](https://github.com/wg-easy/wg-easy) for easy client management.

- Connect from anywhere and have all traffic routed through your server
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

## 🖥️ Management

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
├── pihole/               # Pi-hole config (not committed)
├── wireguard/            # WireGuard config (not committed)
├── minecraft/            # Minecraft data (not committed)
├── discord-bot/
│   └── Dockerfile
└── caddy/                # Reverse proxy (future)
```

---

## 🗒️ Roadmap

- [x] Pi-hole DNS ad blocking
- [x] WireGuard VPN
- [x] Minecraft server
- [x] Portainer + Cockpit management UIs
- [ ] Discord bot
- [ ] Personal website
- [ ] Caddy reverse proxy + SSL
- [ ] Custom domain
- [ ] Automated backups

---

## 📄 License

Personal project — not intended for production use. Feel free to use as inspiration. 🙂
