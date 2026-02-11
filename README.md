# 🚀 Price Alert Engine

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)](https://www.docker.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![Poetry](https://img.shields.io/badge/Poetry-Dependency%20Manager-60A5FA.svg)](https://python-poetry.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)]()

**Price Alert Engine** es un sistema de monitoreo de precios para activos financieros/cripto construido con:

- FastAPI (API REST)
- Worker asincrónico
- PostgreSQL
- SQLAlchemy
- Telegram Notifications
- Docker

El motor evalúa estrategias automáticamente y envía alertas cuando se cumplen condiciones como:

- Take Profit
- Stop Loss
- Trailing Stop

---

## 🧠 Arquitectura

El proyecto está compuesto por tres servicios principales:

- **API** → expone endpoints REST para configurar activos, holdings y estrategias  
- **Worker** → evalúa precios periódicamente y dispara alertas  
- **PostgreSQL** → persistencia  

El worker consulta proveedores de precio como Binance, Coinbase y CoinGecko.

---

## 📦 Requisitos

### Para Docker (recomendado)

- Docker >= 24
- Docker Compose

### Para ejecución local

- Python **3.12**
- Poetry  

---

# 🐳 Levantar el proyecto con Docker (Recomendado)

## 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/dannielgloria/price-alert-engine.git
cd price-alert-engine
```

---

## 2️⃣ Crear archivo `.env`

```bash
cp .env.example .env
```

---

## 3️⃣ Construir y levantar

```bash
docker compose up --build
```

Postgres se expone en:

```
localhost:5433
```

API:

```
http://localhost:8000
```

---

## ✅ Verificar que el sistema está vivo

```bash
curl http://localhost:8000/health
```

Respuesta:

```json
{
  "status": "ok"
}
```

---

# 📘 Swagger / OpenAPI

FastAPI genera documentación automáticamente.

### Abrir en navegador:

```
http://localhost:8000/docs
```

---

# 💻 Ejecutar SIN Docker (modo local)

## 1. Instalar dependencias

```bash
poetry install
```

---

## 2. Levantar Postgres

```bash
docker run -p 5433:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=alerts postgres:16
```

---

## 3. Ejecutar API

```bash
poetry run uvicorn app.main:app --reload
```

---

## 4. Ejecutar Worker

```bash
poetry run python -m app.engine.run
```

---

# 🔔 Configurar Telegram (Opcional)

Si no configuras token/chat, el notifier simplemente no enviará mensajes.

---

# 📡 Endpoints

- `/health`
- `/assets`
- `/holdings`
- `/strategies`

---

# 🧪 Ejemplos CURL + Explicación

---

## ✅ Health Check

```bash
curl http://localhost:8000/health
```

Sirve para validar que la API está operativa.

---

# 📊 Assets

Representan los activos a monitorear.

## Crear / actualizar asset

```bash
curl -X POST http://localhost:8000/assets -H "Content-Type: application/json" -d '{
  "symbol": "BTC",
  "enabled": true,
  "binance_symbol": "BTCUSDT",
  "coinbase_product_id": "BTC-USD",
  "coingecko_id": "bitcoin"
}'
```

### Request Fields

| Campo | Tipo | Significado |
|--------|------|-------------|
| symbol | string | Identificador del activo |
| enabled | bool | Si el worker debe monitorearlo |
| binance_symbol | string | Símbolo en Binance |
| coinbase_product_id | string | Producto en Coinbase |
| coingecko_id | string | ID en CoinGecko |

---

## Listar assets

```bash
curl http://localhost:8000/assets
```

---

# 💰 Holdings

Representan posiciones abiertas.

## Crear holding

```bash
curl -X POST http://localhost:8000/holdings -H "Content-Type: application/json" -d '{
  "symbol": "BTC",
  "entry": 60000,
  "invested_amount": 1500
}'
```

### Campos

| Campo | Significado |
|--------|-------------|
| symbol | Activo comprado |
| entry | Precio de entrada |
| invested_amount | Capital invertido |

---

# 📈 Strategies

Controlan la lógica de trading.

## Obtener estrategia

```bash
curl http://localhost:8000/strategies/BTC
```

Si no existe, se crea automáticamente.

---

## Actualizar estrategia

```bash
curl -X PUT http://localhost:8000/strategies/BTC -H "Content-Type: application/json" -d '{
  "base_tp": 0.10,
  "sl_pct": 0.08,
  "trail_atr_mult": 2.5,
  "profit_lock_pct": 0.06,
  "cooldown_sec": 1800,
  "confirm_regime": true
}'
```

---

# ⚙️ Worker Engine

El worker:

1. Obtiene activos habilitados  
2. Consulta precios  
3. Calcula indicadores  
4. Evalúa señales  
5. Envía alertas  
6. Guarda estado  

---

# 🧱 Base de Datos

Tablas principales:

- assets  
- holdings  
- strategies  
- engine_state  
- alerts  

---

# 🧯 Troubleshooting

## Error de conexión DB

Verifica:

```
DATABASE_URL
```

---

## Worker no envía alertas

Revisa:

- token Telegram  
- chat id  
- assets habilitados  

---

## Puerto ocupado

Cambia:

```
8000
5433
```

---

# 🧪 Testing

```bash
poetry run pytest
```

---

# 🚀 Producción (Recomendaciones)

- usar secrets manager  
- activar logs estructurados  
- agregar retry policy  
- métricas (Prometheus / OTEL)  
- mover cache a Redis  

---

# 👨‍💻 Autor

Daniel  

---

## 🧭 Resumen

Este motor está diseñado para ser:

✅ extensible  
✅ automatizable  
✅ docker-friendly  
✅ event-driven  

Ideal para sistemas de alertas financieras o bots de trading.
