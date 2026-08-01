FROM python:3.12-slim

# Install system dependencies (git for GitHub integration)
RUN apt-get update && apt-get install -y git curl docker.io && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set permissions
RUN chmod +x bot.py

CMD ["python", "bot.py"]