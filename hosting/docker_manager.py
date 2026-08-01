import aiodocker
import os
import asyncio
from config import settings

class DockerManager:
    def __init__(self):
        self.docker = aiodocker.Docker()

    async def create_and_start_container(self, project_name: str, lang: str, project_dir: str, ram_mb: int, cpu_cores: float) -> str:
        # Determine image and command based on language
        if lang == "python":
            image = "python:3.12-slim"
            cmd = ["sh", "-c", "if [ -f requirements.txt ]; then pip install -r requirements.txt; fi && python main.py"]
        elif lang == "nodejs":
            image = "node:20-alpine"
            cmd = ["sh", "-c", "if [ -f package.json ]; then npm install; fi && npm start"]
        elif lang == "php":
            image = "php:8.2-cli"
            cmd = ["php", "-S", "0.0.0.0:8000"]
        else:
            raise ValueError("Unsupported language")

        # Pull image if not exists
        try:
            await self.docker.images.inspect(image)
        except aiodocker.exceptions.DockerError:
            await self.docker.images.pull(image)

        container_name = f"host_{project_name}_{asyncio.get_running_loop().time()}"
        
        host_config = {
            "Binds": [f"{os.path.abspath(project_dir)}:/app"],
            "Memory": ram_mb * 1024 * 1024,
            "NanoCPUs": int(cpu_cores * 1e9),
            "NetworkMode": "bridge"
        }

        config = {
            "Image": image,
            "Cmd": cmd,
            "WorkingDir": "/app",
            "HostConfig": host_config,
            "Tty": True,
            "OpenStdin": True
        }

        container = await self.docker.containers.create(config=config, name=container_name)
        await container.start()
        return container.id

    async def stop_container(self, container_id: str):
        try:
            container = await self.docker.containers.get(container_id)
            await container.stop()
        except aiodocker.exceptions.DockerError:
            pass

    async def delete_container(self, container_id: str):
        try:
            container = await self.docker.containers.get(container_id)
            await container.delete(force=True)
        except aiodocker.exceptions.DockerError:
            pass

    async def get_logs(self, container_id: str, tail: int = 20) -> str:
        try:
            container = await self.docker.containers.get(container_id)
            logs = await container.log(stdout=True, stderr=True, tail=tail)
            return "".join(logs) if logs else "No logs available."
        except Exception as e:
            return f"Error fetching logs: {str(e)}"

    async def get_stats(self, container_id: str) -> dict:
        try:
            container = await self.docker.containers.get(container_id)
            stats = await container.stats(stream=False)
            return stats[0]
        except:
            return {}

    async def close(self):
        await self.docker.close()

docker_manager = DockerManager()