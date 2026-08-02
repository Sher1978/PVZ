doc\_content\_5 = """# Документ 5: Структура и Схема Базы Данных (Database Architecture \& Schema)

\## Проект: SmartSearch TMA — Умный агрегатор и поиск товаров по мультиплатформам



\---



\## 1. Архитектура Хранилищ Данных (Polyglot Persistence)



Система использует комбинированный подход к хранению данных для обеспечения максимальной производительности, быстрого поиска и гибкого масштабирования:



| База данных / Хранилище | Тип / СУБД | Назначение |

| :--- | :--- | :--- |

| \*\*Primary Relational DB\*\* | PostgreSQL 16 | Основное транзакционное хранилище (пользователи, офферы, истории цен, подписки). |

| \*\*Vector DB\*\* | Qdrant | Векторная СУБД для поиска по изображениям (CLIP) и текстам (Sentence-BERT). |

| \*\*Search Engine\*\* | Meilisearch / Elasticsearch | Полнотекстовый поиск по заголовкам, брендам и категориям с поддержкой опечаток. |

| \*\*In-Memory Cache \& Broker\*\* | Redis | Кэширование поисковых ответов, сессии пользователей, Token Bucket (Rate Limit), очереди Celery. |



\---



\## 2. Реляционная Схема (PostgreSQL DDL)



```sql

\-- 1. Пользователи Telegram Mini App

CREATE TABLE users (

&#x20;   id BIGSERIAL PRIMARY KEY,

&#x20;   telegram\_id BIGINT UNIQUE NOT NULL,

&#x20;   username VARCHAR(64),

&#x20;   first\_name VARCHAR(128) NOT NULL,

&#x20;   language\_code VARCHAR(8) DEFAULT 'ru',

&#x20;   is\_premium BOOLEAN DEFAULT FALSE,

&#x20;   created\_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT\_TIMESTAMP,

&#x20;   last\_active\_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT\_TIMESTAMP

);



CREATE INDEX idx\_users\_telegram\_id ON users(telegram\_id);



\-- 2. Категории Товаров

CREATE TABLE categories (

&#x20;   id SERIAL PRIMARY KEY,

&#x20;   parent\_id INT REFERENCES categories(id) ON DELETE SET NULL,

&#x20;   name VARCHAR(255) NOT NULL,

&#x20;   slug VARCHAR(255) UNIQUE NOT NULL

);



\-- 3. Master-карточки (Объединенные товары)

CREATE TABLE master\_products (

&#x20;   id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),

&#x20;   title VARCHAR(512) NOT NULL,

&#x20;   brand VARCHAR(128),

&#x20;   category\_id INT REFERENCES categories(id),

&#x20;   main\_image\_url TEXT,

&#x20;   description TEXT,

&#x20;   created\_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT\_TIMESTAMP,

&#x20;   updated\_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT\_TIMESTAMP

);



CREATE INDEX idx\_master\_products\_brand ON master\_products(brand);



\-- 4. Офферы Маркетплейсов (Wildberries, Ozon, Yandex Market, AliExpress)

CREATE TABLE offers (

&#x20;   id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),

&#x20;   master\_id UUID REFERENCES master\_products(id) ON DELETE CASCADE,

&#x20;   platform VARCHAR(32) NOT NULL, -- 'wb', 'ozon', 'yandex\_market', 'aliexpress'

&#x20;   external\_sku VARCHAR(128) NOT NULL,

&#x20;   title VARCHAR(512) NOT NULL,

&#x20;   current\_price NUMERIC(12, 2) NOT NULL,

&#x20;   old\_price NUMERIC(12, 2),

&#x20;   currency VARCHAR(3) DEFAULT 'RUB',

&#x20;   product\_url TEXT NOT NULL,

&#x20;   image\_url TEXT,

&#x20;   in\_stock BOOLEAN DEFAULT TRUE,

&#x20;   rating NUMERIC(3, 2),

&#x20;   reviews\_count INT DEFAULT 0,

&#x20;   updated\_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT\_TIMESTAMP,

&#x20;   CONSTRAINT unique\_platform\_sku UNIQUE (platform, external\_sku)

);



CREATE INDEX idx\_offers\_master\_id ON offers(master\_id);

CREATE INDEX idx\_offers\_platform\_sku ON offers(platform, external\_sku);

CREATE INDEX idx\_offers\_price ON offers(current\_price);



\-- 5. История Цен

CREATE TABLE price\_history (

&#x20;   id BIGSERIAL PRIMARY KEY,

&#x20;   offer\_id UUID NOT NULL REFERENCES offers(id) ON DELETE CASCADE,

&#x20;   price NUMERIC(12, 2) NOT NULL,

&#x20;   recorded\_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT\_TIMESTAMP

);



CREATE INDEX idx\_price\_history\_offer\_time ON price\_history(offer\_id, recorded\_at DESC);



\-- 6. Подписки на Изменение Цены (Price Alerts)

CREATE TABLE price\_alerts (

&#x20;   id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),

&#x20;   user\_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

&#x20;   master\_id UUID NOT NULL REFERENCES master\_products(id) ON DELETE CASCADE,

&#x20;   target\_price NUMERIC(12, 2) NOT NULL,

&#x20;   is\_active BOOLEAN DEFAULT TRUE,

&#x20;   notify\_on\_any\_drop BOOLEAN DEFAULT FALSE,

&#x20;   created\_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT\_TIMESTAMP

);



CREATE INDEX idx\_alerts\_active ON price\_alerts(master\_id) WHERE is\_active = TRUE;

3\. Схема Векторной Базы Данных (Qdrant Vector Collection)

Коллекция: master\_product\_vectors



Vector Dimensions: 512 (Multimodal CLIP / Sentence-Transformers)



Distance Metric: Cosine



Payload Schema (Метаданные вектора):

JSON

{

&#x20; "master\_id": "mst\_9f83a210",

&#x20; "title": "Беспроводные полноразмерные наушники Sony WH-1000XM5 Black",

&#x20; "brand": "Sony",

&#x20; "category\_id": 42,

&#x20; "min\_price": 28990.00,

&#x20; "updated\_at": 1775030400

}

4\. Полнотекстовый Индекс (Meilisearch Index Schema)

Индекс: products\_index



Searchable Attributes: \["title", "brand", "category\_name", "description"]



Filterable Attributes: \["brand", "category\_id", "min\_price", "platforms"]



Sortable Attributes: \["min\_price", "rating", "created\_at"]



5\. Стратегия Оптимизации и Индексы

Партиционирование таблицы price\_history: По интервалам времени (RANGE (recorded\_at) по месяцам) для сохранения высокой скорости записи при десятках миллионов строк.



Индексы B-Tree: По ключевым колонкам фильтрации (master\_id, telegram\_id, platform\_sku).



Составные индексы: (master\_id, platform) в таблице offers для быстрого аггрегирования цен по Master-карточке.



Документ подготовлен для сохранения в папке Bible/05\_Database\_Structure.md.

"""



with open("05\_Database\_Structure.md", "w", encoding="utf-8") as f:

f.write(doc\_content\_5)



print("FILE\_CREATED: 05\_Database\_Structure.md")

