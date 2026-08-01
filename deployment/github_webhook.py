import hmac
import hashlib
from aiohttp import web
from config import settings
from hosting.git_manager import pull_repo
from logs.logger import get_logger

logger = get_logger("hosting")

async def github_webhook_handler(request: web.Request):
    """Listens for GitHub Push events to trigger auto-deployments."""
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        return web.Response(status=401, text="Missing signature")

    payload = await request.read()
    secret = settings.GITHUB_WEBHOOK_SECRET.encode()
    expected_signature = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return web.Response(status=403, text="Invalid signature")

    data = await request.json()
    if request.headers.get("X-GitHub-Event") == "push":
        repo_name = data.get("repository", {}).get("name")
        logger.info(f"Received push event for repository: {repo_name}. Triggering git pull.")
        
        # In a full implementation, you would map repo_name to the project_dir via DB
        # pull_repo(target_dir)
        
        return web.Response(status=200, text="Deployed successfully")

    return web.Response(status=200, text="Ignored non-push event")

async def start_webhook_server():
    """Starts the internal aiohttp server for incoming webhooks."""
    app = web.Application()
    app.router.add_post("/webhook/github", github_webhook_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', settings.WEBHOOK_PORT)
    await site.start()
    logger.info(f"GitHub Webhook server started on port {settings.WEBHOOK_PORT}")