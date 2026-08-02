Документ 6: Инфраструктура, Docker Compose и CI/CD (06\_Infrastructure\_and\_Deployment.md)Проект: SmartSearch TMA — Умный агрегатор и поиск товаров по мультиплатформам1. Обзор Инфраструктурной АрхитектурыСистема разворачивается в изолированном контейнеризированном окружении Docker Compose с четким разделением слоев (Web/Proxy, App Backend, Background Workers, Databases \& Caches).  Edge / Reverse Proxy: Nginx (SSL Termination, Rate Limiting, HTTP/2, Static Delivery).Application Layer: FastAPI Web App (ASGI via Uvicorn).Worker Layer: Celery / ARQ Workers (асинхронные задачи сбора цен, отправки push-уведомлений и векторизации).Data Stores: PostgreSQL 16, Redis 7, Qdrant, Meilisearch.  2. Docker Compose Specification (docker-compose.yml)YAMLversion: '3.8'



services:

&#x20; nginx:

&#x20;   image: nginx:alpine

&#x20;   container\_name: smartsearch\_nginx

&#x20;   ports:

&#x20;     - "80:80"

&#x20;     - "443:443"

&#x20;   volumes:

&#x20;     - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro

&#x20;     - ./nginx/conf.d:/etc/nginx/conf.d:ro

&#x20;     - ./certbot/conf:/etc/letsencrypt:ro

&#x20;     - ./certbot/www:/var/www/certbot:ro

&#x20;   depends\_on:

&#x20;     - api

&#x20;   restart: always

&#x20;   networks:

&#x20;     - app\_network



&#x20; api:

&#x20;   build:

&#x20;     context: .

&#x20;     dockerfile: Dockerfile

&#x20;   container\_name: smartsearch\_api

&#x20;   command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

&#x20;   environment:

&#x20;     - DATABASE\_URL=postgresql+asyncpg://${POSTGRES\_USER}:${POSTGRES\_PASSWORD}@postgres:5432/${POSTGRES\_DB}

&#x20;     - REDIS\_URL=redis://redis:6379/0

&#x20;     - QDRANT\_HOST=qdrant

&#x20;     - MEILISEARCH\_HOST=http://meilisearch:7700

&#x20;     - BOT\_TOKEN=${BOT\_TOKEN}

&#x20;     - JWT\_SECRET=${JWT\_SECRET}

&#x20;   depends\_on:

&#x20;     postgres:

&#x20;       condition: service\_healthy

&#x20;     redis:

&#x20;       condition: service\_healthy

&#x20;     qdrant:

&#x20;       condition: service\_started

&#x20;     meilisearch:

&#x20;       condition: service\_started

&#x20;   restart: always

&#x20;   networks:

&#x20;     - app\_network



&#x20; worker:

&#x20;   build:

&#x20;     context: .

&#x20;     dockerfile: Dockerfile

&#x20;   container\_name: smartsearch\_worker

&#x20;   command: celery -A app.tasks.celery\_app worker --loglevel=info -c 4

&#x20;   environment:

&#x20;     - DATABASE\_URL=postgresql+asyncpg://${POSTGRES\_USER}:${POSTGRES\_PASSWORD}@postgres:5432/${POSTGRES\_DB}

&#x20;     - REDIS\_URL=redis://redis:6379/0

&#x20;     - QDRANT\_HOST=qdrant

&#x20;     - BOT\_TOKEN=${BOT\_TOKEN}

&#x20;   depends\_on:

&#x20;     - redis

&#x20;     - postgres

&#x20;   restart: always

&#x20;   networks:

&#x20;     - app\_network



&#x20; scheduler:

&#x20;   build:

&#x20;     context: .

&#x20;     dockerfile: Dockerfile

&#x20;   container\_name: smartsearch\_scheduler

&#x20;   command: celery -A app.tasks.celery\_app beat --loglevel=info

&#x20;   environment:

&#x20;     - REDIS\_URL=redis://redis:6379/0

&#x20;   depends\_on:

&#x20;     - worker

&#x20;   restart: always

&#x20;   networks:

&#x20;     - app\_network



&#x20; postgres:

&#x20;   image: postgres:16-alpine

&#x20;   container\_name: smartsearch\_postgres

&#x20;   environment:

&#x20;     POSTGRES\_USER: ${POSTGRES\_USER}

&#x20;     POSTGRES\_PASSWORD: ${POSTGRES\_PASSWORD}

&#x20;     POSTGRES\_DB: ${POSTGRES\_DB}

&#x20;   ports:

&#x20;     - "127.0.0.1:5432:5432"

&#x20;   volumes:

&#x20;     - postgres\_data:/var/lib/postgresql/data

&#x20;   healthcheck:

&#x20;     test: \["CMD-SHELL", "pg\_isready -U ${POSTGRES\_USER} -d ${POSTGRES\_DB}"]

&#x20;     interval: 5s

&#x20;     timeout: 5s

&#x20;     retries: 5

&#x20;   restart: always

&#x20;   networks:

&#x20;     - app\_network



&#x20; redis:

&#x20;   image: redis:7-alpine

&#x20;   container\_name: smartsearch\_redis

&#x20;   command: redis-server --appendonly yes

&#x20;   ports:

&#x20;     - "127.0.0.1:6379:6379"

&#x20;   volumes:

&#x20;     - redis\_data:/data

&#x20;   healthcheck:

&#x20;     test: \["CMD", "redis-cli", "ping"]

&#x20;     interval: 5s

&#x20;     timeout: 5s

&#x20;     retries: 5

&#x20;   restart: always

&#x20;   networks:

&#x20;     - app\_network



&#x20; qdrant:

&#x20;   image: qdrant/qdrant:v1.8.0

&#x20;   container\_name: smartsearch\_qdrant

&#x20;   ports:

&#x20;     - "127.0.0.1:6333:6333"

&#x20;   volumes:

&#x20;     - qdrant\_data:/qdrant/storage

&#x20;   restart: always

&#x20;   networks:

&#x20;     - app\_network



&#x20; meilisearch:

&#x20;   image: getmeili/meilisearch:v1.6

&#x20;   container\_name: smartsearch\_meilisearch

&#x20;   environment:

&#x20;     MEILI\_MASTER\_KEY: ${MEILI\_MASTER\_KEY}

&#x20;     MEILI\_ENV: "production"

&#x20;   ports:

&#x20;     - "127.0.0.1:7700:7700"

&#x20;   volumes:

&#x20;     - meili\_data:/meili\_data

&#x20;   restart: always

&#x20;   networks:

&#x20;     - app\_network



volumes:

&#x20; postgres\_data:

&#x20; redis\_data:

&#x20; qdrant\_data:

&#x20; meili\_data:



networks:

&#x20; app\_network:

&#x20;   driver: bridge

3\. Конфигурация Nginx \& SSL (nginx.conf)Nginxevents {

&#x20;   worker\_connections 1024;

}



http {

&#x20;   include       /etc/nginx/mime.types;

&#x20;   default\_type  application/octet-stream;



&#x20;   sendfile        on;

&#x20;   keepalive\_timeout 65;

&#x20;   client\_max\_body\_size 15M;



&#x20;   # Rate Limiting Zone

&#x20;   limit\_req\_zone $binary\_remote\_addr zone=api\_limit:10m rate=30r/s;



&#x20;   upstream fastapi\_app {

&#x20;       server api:8000;

&#x20;   }



&#x20;   server {

&#x20;       listen 80;

&#x20;       server\_name api.smartsearch.app;



&#x20;       location /.well-known/acme-challenge/ {

&#x20;           root /var/www/certbot;

&#x20;       }



&#x20;       location / {

&#x20;           return 301 https://$host$request\_uri;

&#x20;       }

&#x20;   }



&#x20;   server {

&#x20;       listen 443 ssl http2;

&#x20;       server\_name api.smartsearch.app;



&#x20;       ssl\_certificate /etc/letsencrypt/live/api.smartsearch.app/fullchain.pem;

&#x20;       ssl\_certificate\_key /etc/letsencrypt/live/api.smartsearch.app/privkey.pem;



&#x20;       ssl\_protocols TLSv1.2 TLSv1.3;

&#x20;       ssl\_ciphers HIGH:!aNULL:!MD5;



&#x20;       location /api/ {

&#x20;           limit\_req zone=api\_limit burst=20 nodelay;

&#x20;           proxy\_pass http://fastapi\_app;

&#x20;           proxy\_set\_header Host $host;

&#x20;           proxy\_set\_header X-Real-IP $remote\_addr;

&#x20;           proxy\_set\_header X-Forwarded-For $proxy\_add\_x\_forwarded\_for;

&#x20;           proxy\_set\_header X-Forwarded-Proto $scheme;

&#x20;       }



&#x20;       location / {

&#x20;           proxy\_pass http://fastapi\_app;

&#x20;           proxy\_set\_header Host $host;

&#x20;           proxy\_set\_header X-Real-IP $remote\_addr;

&#x20;       }

&#x20;   }

}

4\. Пайплайн CI/CD (GitHub Actions Workflow)Файл .github/workflows/deploy.yml:YAMLname: SmartSearch TMA CI/CD Pipeline



on:

&#x20; push:

&#x20;   branches:

&#x20;     - main



jobs:

&#x20; test:

&#x20;   runs-on: ubuntu-latest

&#x20;   steps:

&#x20;     - name: Checkout Code

&#x20;       uses: actions/checkout@v3



&#x20;     - name: Set up Python

&#x20;       uses: actions/setup-python@v4

&#x20;       with:

&#x20;         python-version: '3.11'



&#x20;     - name: Install Dependencies

&#x20;       run: |

&#x20;         python -m pip install --upgrade pip

&#x20;         pip install -r requirements.txt

&#x20;         pip install pytest pytest-asyncio httpx



&#x20;     - name: Run Tests

&#x20;       run: |

&#x20;         pytest tests/



&#x20; deploy:

&#x20;   needs: test

&#x20;   runs-on: ubuntu-latest

&#x20;   if: github.ref == 'refs/heads/main'

&#x20;   steps:

&#x20;     - name: Checkout Code

&#x20;       uses: actions/checkout@v3



&#x20;     - name: Deploy to Server via SSH

&#x20;       uses: appleboy/ssh-action@v0.1.10

&#x20;       with:

&#x20;         host: ${{ secrets.SERVER\_HOST }}

&#x20;         username: ${{ secrets.SERVER\_USER }}

&#x20;         key: ${{ secrets.SSH\_PRIVATE\_KEY }}

&#x20;         script: |

&#x20;           cd /opt/smartsearch-backend

&#x20;           git pull origin main

&#x20;           docker compose down

&#x20;           docker compose build --no-cache

&#x20;           docker compose up -d

&#x20;           docker system prune -f

5\. Мониторинг, Логирование и Резервное КопированиеЛогирование: Все контейнеры отправляют JSON-логи в Docker Driver (json-file) с ограничением размера файлов (max-size: "10m", max-file: "3").Мониторинг: Использование Prometheus + Grafana экспортёров (Postgres Exporter, Redis Exporter, Cadvisor).Резервное копирование PostgreSQL: Ежедневный автоматический снапшот БД в S3-совместимое хранилище через Cron-скрипт pg\_dump.

