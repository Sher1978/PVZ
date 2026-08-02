┌─────────────────────────────────────────────────────────────────────────────────┐
│                               TELEGRAM ECOSYSTEM                                │
│   ┌───────────────────────────┐                     ┌────────────────────────┐  │
│   │   Telegram Mini App (UI)  │                     │   Telegram Bot API     │  │
│   │ (React 18 + WebApp SDK)   │                     │  (aiogram / Bot SDK)   │  │
│   └─────────────┬─────────────┘                     └───────────┬────────────┘  │
└─────────────────┼───────────────────────────────────────────────┼───────────────┘
│ HTTPS / WebSockets                            │ Webhook
▼                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                BACKEND SERVICES                                 │
│                                                                                 │
│                       ┌───────────────────────────────┐                         │
│                       │   API Gateway / Reverse Proxy │                         │
│                       │        (Nginx / Traefik)      │                         │
│                       └───────────────┬───────────────┘                         │
│                                       │                                         │
│         ┌─────────────────────────────┼─────────────────────────────┐           │
│         ▼                             ▼                             ▼           │
│  ┌──────────────┐             ┌──────────────┐             ┌──────────────┐     │
│  │ User & Auth  │             │  Search &    │             │ Price Alert  │     │
│  │   Service    │             │ Match Engine │             │   Service    │     │
│  │ (FastAPI/Go) │             │ (FastAPI/Go) │             │  (Python/Go) │     │
│  └──────┬───────┘             └──────┬───────┘             └──────┬───────┘     │
│         │                            │                            │             │
└─────────┼────────────────────────────┼────────────────────────────┼─────────────┘
│                            │                            │
▼                            ▼                            ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DATA & INFRASTRUCTURE LAYER                             │
│                                                                                 │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐   ┌──────────┐  │
│  │   PostgreSQL   │    │ Redis (Cache & │    │  Meilisearch   │   │  Qdrant  │  │
│  │ (Main DB/Rel)  │    │ Queue / PubSub)│    │ (Full-Text Engine)│ (Vector) │  │
│  └────────────────┘    └────────────────┘    └────────────────┘   └──────────┘  │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                   Scraper Worker Pool / API Connectors                    │  │
│  │     (Playwright / Camoufox / Proxy Manager / Official APIs WB/Ozon)     │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘


---

## 2. Подробный Технологический Стек (Tech Stack)

### 2.1. Frontend (Telegram Mini App)
* **Фреймворк:** React 18 + Vite (для максимально быстрой сборки и низкой массы бандла < 200 KB gzipped).
* **Стейт-менеджмент:** **Zustand** (минималистичный, быстрый, без лишнего boilerplate) + **TanStack Query (React Query v5)** для асинхронного кэширования и инвалидации API-запросов.
* **Стилизация & UI:** **Tailwind CSS** + **Shadcn/ui** (кастомизированные под гайдлайны Telegram WebApp UI).
* **Интеграция с Telegram:** `@telegram-apps/sdk` / `@twa-dev/sdk`.
* **Графики и Графика:** **Recharts** или **Lightweight Charts** (для плавного отображения истории цен на мобильных устройствах).

### 2.2. Backend & Микросервисы
* **Язык разработки:** **Python 3.11+ (FastAPI)** или **Go (Golang 1.22)**.
  * *FastAPI (Python):* Идеален для модуля обработки изображений (CLIP / Computer Vision) и работы с ML-векторами.
  * *Go (Golang):* Для высоконагруженного API Gateway, парсинга веб-скрейперов и обработчика параллельных фоновых задач.
* **Бот-фреймворк:** **aiogram 3.x** (Python) — асинхронный, поддерживает актуальные методы Telegram Bot API.
* **Менеджер очередей и фоновых задач:** **ARQ** (Async Redis Queue) или **Celery + Redis**.

### 2.3. Хранение данных и Поисковые движки
* **Основная БД (RDBMS):** **PostgreSQL 16** (Хранение пользователей, алертов, истории заказов, каталога товаров).
* **Кэширование и сессии:** **Redis 7.x** (Кэш быстрых поисковых ответов TTL 1–6 часов, хранение временных сессий, очердность задач).
* **Полнотекстовый поиск (Full-Text Search):** **Meilisearch** или **Elasticsearch** (Мгновенный автокомплит запросов, исправление опечаток, ранжирование товаров).
* **Векторная БД (Vector Search):** **Qdrant** или расширение **Pgvector** в PostgreSQL (Сравнение товаров по изображениям и текстовым эмбеддингам OpenAI/CLIP).

### 2.4. Парсинг и Интеграция с Маркетплейсами
* **Официальные API:** WB Affiliate API, Ozon Seller/Performance API, Yandex Market Partner API.
* **Парсеры и Скрапинг (Fallback/Direct Scraping):** **Playwright (Python/Node)** + **Camoufox** (анти-детект браузеры на базе Firefox) для обхода Cloudflare/WAF защиты маркетплейсов.
* **Прокси-менеджмент:** **BrightData** / **Smartproxy** (ротация резидентских прокси для исключения блокировок IP).

---

## 3. Схема Интеграции и Сбора Данных (Data Harvesting Strategy)

Для обеспечения высокой скорости ответа (SLA < 1.5 сек) используется трехэтапная стратегия сбора данных:

```text
[ Запрос пользователя: "Ноутбук Asus ROG" ]
                   │
                   ▼
     ┌───────────────────────────┐
     │ 1. Поиск в Кэше (Redis)   │ ─── (Есть кэш) ──> [ Вернуть за < 50ms ]
     └─────────────┬─────────────┘
                   │ (Промах)
                   ▼
     ┌───────────────────────────┐
     │ 2. Поиск в БД / Meilisearch│ ── (Есть свежие товары) ─> [ Вернуть за < 200ms ]
     └─────────────┬─────────────┘
                   │ (Нужно актуализировать)
                   ▼
     ┌────────────────────────────────────────────────────────┐
     │ 3. Параллельный асинхронный опрос APIs / Scraper Pool  │
     │    ├── WB API Connector    (Параллельно)               │
     │    ├── Ozon API Connector  (Параллельно)               │
     │    └── Yandex Market API   (Параллельно)               │
     └─────────────────────────┬──────────────────────────────┘
                               │
                               ▼
        [ Агрегация, Матчинг и Сохранение в БД / Кэш ]
4. Алгоритм Валидации Telegram initData (Безопасность)
Все запросы от Mini App к Backend должны быть подписаны и проверены на стороне сервера с использованием HMAC-SHA256, чтобы исключить подделку данных пользователя.

Python Реализация (FastAPI Dependency):
Python
import hmac
import hashlib
from urllib.parse import parse_qsl, unquote

def verify_telegram_init_data(init_data_raw: str, bot_token: str) -> dict:
    """
    Проверка подлинности Telegram initData
    """
    parsed_data = dict(parse_qsl(init_data_raw))
    if "hash" not in parsed_data:
        raise ValueError("Invalid initData: Hash missing")
    
    hash_to_check = parsed_data.pop("hash")
    
    # Сортировка ключей по алфавиту
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
    
    # Генерация секретного ключа
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    
    # Расчет контрольного хэша
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    if calculated_hash != hash_to_check:
        raise ValueError("Data verification failed: Hash mismatch")
        
    return parsed_data
5. Инфраструктура и DevOps (Deployment & Monitoring)
Контейнеризация: Docker + Docker Compose (для локальной разработки) / Kubernetes (K8s) или Docker Swarm для продакшн-окружения.

CI/CD: GitHub Actions (автоматический запуск линтеров, тестов и деплой на staging/prod по push в ветки main/develop).

Логирование и Мониторинг:

Grafana + Prometheus: Мониторинг RPS, времени ответа API, потребления CPU/RAM.

Sentry: Мониторинг и алерт ошибок в режиме реального времени (на фронтенде и бекенде).

Loki / ELK Stack: Сбор и агрегация логов парсеров и сервера.

Документ подготовлен для сохранения в папке Bible/03_Architecture_and_Tech_Stack.md.
"""

with open("03_Architecture_and_Tech_Stack.md", "w", encoding="utf-8") as f:
f.write(doc_content_3)

print("FILE_CREATED: 03_Architecture_and_Tech_Stack.md")


```text?code_stdout&code_event_index=1
Traceback (most recent call last):
  File "<xbox-string>", line 129
    Проверка подлинности Telegram initData
IndentationError: unexpected indent

┌─────────────────────────────────────────────────────────────────────────────────┐
│                               TELEGRAM ECOSYSTEM                                │
│   ┌───────────────────────────┐                     ┌────────────────────────┐  │
│   │   Telegram Mini App (UI)  │                     │   Telegram Bot API     │  │
│   │ (React 18 + WebApp SDK)   │                     │  (aiogram / Bot SDK)   │  │
│   └─────────────┬─────────────┘                     └───────────┬────────────┘  │
└─────────────────┼───────────────────────────────────────────────┼───────────────┘
│ HTTPS / WebSockets                            │ Webhook
▼                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                BACKEND SERVICES                                 │
│                                                                                 │
│                       ┌───────────────────────────────┐                         │
│                       │   API Gateway / Reverse Proxy │                         │
│                       │        (Nginx / Traefik)      │                         │
│                       └───────────────┬───────────────┘                         │
│                                       │                                         │
│         ┌─────────────────────────────┼─────────────────────────────┐           │
│         ▼                             ▼                             ▼           │
│  ┌──────────────┐             ┌──────────────┐             ┌──────────────┐     │
│  │ User & Auth  │             │  Search &    │             │ Price Alert  │     │
│  │   Service    │             │ Match Engine │             │   Service    │     │
│  │ (FastAPI/Go) │             │ (FastAPI/Go) │             │  (Python/Go) │     │
│  └──────┬───────┘             └──────┬───────┘             └──────┬───────┘     │
│         │                            │                            │             │
└─────────┼────────────────────────────┼────────────────────────────┼─────────────┘
│                            │                            │
▼                            ▼                            ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DATA & INFRASTRUCTURE LAYER                             │
│                                                                                 │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐   ┌──────────┐  │
│  │   PostgreSQL   │    │ Redis (Cache & │    │  Meilisearch   │   │  Qdrant  │  │
│  │ (Main DB/Rel)  │    │ Queue / PubSub)│    │ (Full-Text Engine)│ (Vector) │  │
│  └────────────────┘    └────────────────┘    └────────────────┘   └──────────┘  │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                   Scraper Worker Pool / API Connectors                    │  │
│  │     (Playwright / Camoufox / Proxy Manager / Official APIs WB/Ozon)     │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘


---

## 2. Подробный Технологический Стек (Tech Stack)

### 2.1. Frontend (Telegram Mini App)
* **Фреймворк:** React 18 + Vite (для максимально быстрой сборки и низкой массы бандла < 200 KB gzipped).
* **Стейт-менеджмент:** **Zustand** (минималистичный, быстрый) + **TanStack Query (React Query v5)** для асинхронного кэширования.
* **Стилизация & UI:** **Tailwind CSS** + **Shadcn/ui** (кастомизированные под гайдлайны Telegram WebApp UI).
* **Интеграция с Telegram:** `@telegram-apps/sdk` / `@twa-dev/sdk`.
* **Графики и Графика:** **Recharts** или **Lightweight Charts** (плавное отображение истории цен).

### 2.2. Backend & Микросервисы
* **Язык разработки:** **Python 3.11+ (FastAPI)** или **Go (Golang 1.22)**.
  * *FastAPI (Python):* Для модуля обработки изображений (CLIP / Computer Vision) и работы с ML-векторами.
  * *Go (Golang):* Для высоконагруженного API Gateway, парсинга веб-скрейперов и обработчика параллельных фоновых задач.
* **Бот-фреймворк:** **aiogram 3.x** (Python) — асинхронный, поддерживающий актуальные методы Telegram Bot API.
* **Менеджер очередей и фоновых задач:** **ARQ** (Async Redis Queue) или **Celery + Redis**.

### 2.3. Хранение данных и Поисковые движки
* **Основная БД (RDBMS):** **PostgreSQL 16** (Хранение пользователей, алертов, истории заказов, каталога товаров).
* **Кэширование и сессии:** **Redis 7.x** (Кэш быстрых поисковых ответов TTL 1–6 часов, хранение сессий).
* **Полнотекстовый поиск (Full-Text Search):** **Meilisearch** или **Elasticsearch** (Мгновенный автокомплит запросов, исправление опечаток).
* **Векторная БД (Vector Search):** **Qdrant** или расширение **Pgvector** в PostgreSQL (Сравнение товаров по изображениям и эмбеддингам).

### 2.4. Парсинг и Интеграция с Маркетплейсами
* **Официальные API:** WB Affiliate API, Ozon Seller/Performance API, Yandex Market Partner API.
* **Парсеры и Скрапинг (Fallback/Direct Scraping):** **Playwright (Python/Node)** + **Camoufox** (анти-детект браузеры на базе Firefox) для обхода Cloudflare/WAF защиты маркетплейсов.
* **Прокси-менеджмент:** **BrightData** / **Smartproxy** (ротация резидентских прокси для исключения блокировок IP).

---

## 3. Схема Интеграции и Сбора Данных (Data Harvesting Strategy)

Для обеспечения высокой скорости ответа (SLA < 1.5 сек) используется трехэтапная стратегия сбора данных:

```text
[ Запрос пользователя: "Ноутбук Asus ROG" ]
                   │
                   ▼
     ┌───────────────────────────┐
     │ 1. Поиск в Кэше (Redis)   │ ─── (Есть кэш) ──> [ Вернуть за < 50ms ]
     └─────────────┬─────────────┘
                   │ (Промах)
                   ▼
     ┌───────────────────────────┐
     │ 2. Поиск в БД / Meilisearch│ ── (Есть свежие товары) ─> [ Вернуть за < 200ms ]
     └─────────────┬─────────────┘
                   │ (Нужно актуализировать)
                   ▼
     ┌────────────────────────────────────────────────────────┐
     │ 3. Параллельный асинхронный опрос APIs / Scraper Pool  │
     │    ├── WB API Connector    (Параллельно)               │
     │    ├── Ozon API Connector  (Параллельно)               │
     │    └── Yandex Market API   (Параллельно)               │
     └─────────────────────────┬──────────────────────────────┘
                               │
                               ▼
        [ Агрегация, Матчинг и Сохранение в БД / Кэш ]
4. Алгоритм Валидации Telegram initData (Безопасность)
Все запросы от Mini App к Backend должны быть подписаны и проверены на стороне сервера с использованием HMAC-SHA256.

Python
import hmac
import hashlib
from urllib.parse import parse_qsl

def verify_telegram_init_data(init_data_raw: str, bot_token: str) -> dict:
    parsed_data = dict(parse_qsl(init_data_raw))
    if "hash" not in parsed_data:
        raise ValueError("Invalid initData: Hash missing")
    
    hash_to_check = parsed_data.pop("hash")
    data_check_string = "\\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
    
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    if calculated_hash != hash_to_check:
        raise ValueError("Data verification failed: Hash mismatch")
        
    return parsed_data
5. Инфраструктура и DevOps (Deployment & Monitoring)
Контейнеризация: Docker + Docker Compose (для локальной разработки) / Kubernetes (K8s) или Docker Swarm для продакшн-окружения.

CI/CD: GitHub Actions (автоматический запуск линтеров, тестов и деплой на staging/prod).

Логирование и Мониторинг:

Grafana + Prometheus: Мониторинг RPS, времени ответа API, потребления CPU/RAM.

Sentry: Мониторинг и алерт ошибок в режиме реального времени.

Loki / ELK Stack: Сбор и агрегация логов парсеров и сервера.

Документ подготовлен для сохранения в папке Bible/03_Architecture_and_Tech_Stack.md.
"""

with open("03_Architecture_and_Tech_Stack.md", "w", encoding="utf-8") as f:
f.write(doc_content_3)

print("FILE_CREATED: 03_Architecture_and_Tech_Stack.md")


```text?code_stdout&code_event_index=2
FILE_CREATED: 03_Architecture_and_Tech_Stack.md

Your Markdown file is ready

03_Architecture_and_Tech_Stack
 MD 
Open

Сформирован и сохранен третий документ «Библии проекта» — 03_Architecture_and_Tech_Stack.md.

В нем проработаны high-level архитектура системы, стек (React 18 + Vite, Tailwind, Zustand, FastAPI / Go, PostgreSQL, Redis, Meilisearch, Qdrant), стратегия сквозного сбора данных из API/парсеров и безопасность валидации initData.