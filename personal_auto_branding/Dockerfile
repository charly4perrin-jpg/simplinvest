FROM python:3.11-slim

# Dépendances système pour Playwright (Chromium)
RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libasound2 libpango-1.0-0 libpangocairo-1.0-0 \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir playwright playwright-stealth
RUN playwright install chromium --with-deps

COPY . .

RUN mkdir -p data/profiles data/posts data/leads data/metrics data/sessions

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LINKEDIN_MODE=mock

EXPOSE 5000

CMD ["python", "dashboard/app.py"]
