# Telegram Cloud Hosting Bot 🚀

A fully-functional, production-ready Cloud Hosting Platform operated entirely through Telegram. Host Python, Node.js, and PHP applications inside isolated Docker containers with real-time logs, resource management, and limits.

## Features
- **Project Isolation**: Every app runs in an isolated Docker container with strict CPU/RAM limits.
- **Auto-Detection**: Upload a `.zip`, and the bot automatically configures the runtime environment (`pip install` / `npm install`).
- **File & Process Manager**: Start, Stop, Restart, and get live Server Logs inline.
- **Admin Panel**: Broadcast, monitor users, view system CPU/RAM usage.
- **Security**: Built-in path traversal protection and middleware-based authorization/bans.

## Installation (Ubuntu VPS / Dedicated Server)

1. **Clone the repository & Install Docker**:
    ```bash
    git clone <your-repo>
    cd telegram-cloud-host
    sudo apt install docker.io docker-compose -y
    ```
2. **Configure Environment**:
    ```bash
    cp .env.example .env
    nano .env # Add your BOT_TOKEN and ADMIN_IDS
    ```
3. **Deploy using Docker Compose**:
    ```bash
    sudo docker-compose up -d --build
    ```

## Security Notes
- The bot maps the host's `docker.sock` to control containers. Ensure only trusted Administrators have access to the VPS.
- Path traversal filters are strict; user `.zip` files can never overwrite bot core files.

## Limits Management
Administrators can assign Premium/VIP plans inside the SQLite/PostgreSQL database to allocate more CPU/RAM and disk space limits to specific users.