# Observability — контракт для нескольких сервисов

## Стек

| Компонент | Роль |
|-----------|------|
| **OpenTelemetry SDK** (в каждом сервисе) | Метрики, трейсы, логи → **OTLP** |
| **OTel Collector** | Единая точка приёма OTLP, маршрутизация |
| **Tempo** | Хранение **трейсов** (цепочка вызовов) |
| **Prometheus** | Хранение **метрик** (RPS, latency, ошибки) |
| **Loki** | Хранение **логов** (строки JSON) |
| **Grafana Alloy** | Сбор stdout логов из Docker → Loki |
| **Grafana** | UI: дашборды, Explore, связка trace ↔ logs |

## Tempo — что это

**Grafana Tempo** — база данных для **distributed traces**. Хранит spans: «HTTP POST → service → SQL UPDATE», время каждого шага. В Grafana открываете waterfall одного запроса. Нужен, когда сервисов несколько и trace идёт через gateway → wallet → billing.

## Grafana Alloy — что это

**Grafana Alloy** — агент сбора телеметрии (з successor Promtail). У нас: читает **логи контейнеров Docker** (stdout), парсит JSON, шлёт в **Loki**. Альтернатива — OTLP logs напрямую в Collector; Alloy дублирует путь через stdout (надёжнее на dev).

## W3C Trace Context

Клиент или gateway передаёт заголовок `traceparent`. OTel FastAPI instrumentation продолжает trace. В логах — `trace_id` для поиска в Tempo/Loki.

## Request ID

Заголовок `X-Request-ID` (middleware в `app/api/middleware.py`). Возвращается в ответе. В логах поле `request_id`.

## Тесты

В pytest: `OTEL_SDK_DISABLED=true` — телеметрия не отправляется.

## Запуск

```bash
docker compose -f compose.yaml -f compose.observability.yaml up --build
```

| URL | Назначение |
|-----|------------|
| http://localhost:8000/docs | API |
| http://localhost:3000 | Grafana (admin / admin) |
| http://localhost:9090 | Prometheus |

## PromQL / LogQL примеры

Запросы вводятся в **Grafana → Explore** (не в терминал). Datasource: **Prometheus** для PromQL, **Loki** для LogQL. Сначала поднимите observability-стек и сделайте несколько запросов к API.

### Prometheus (метрики)

Лейбл сервиса после скрейпа Collector — **`exported_job="wallet-api"`** (не `service_name`).

Нагрузка (RPS):

```promql
sum(rate(http_server_duration_milliseconds_count{exported_job="wallet-api"}[5m]))
```

RPS по кодам ответа (200, 400, 404, 422):

```promql
sum by (http_status_code) (rate(http_server_duration_milliseconds_count{exported_job="wallet-api"}[5m]))
```

4xx RPS:

```promql
sum(rate(http_server_duration_milliseconds_count{exported_job="wallet-api",http_status_code=~"4.."}[5m]))
```

5xx RPS (если 5xx не было — линия на 0):

```promql
sum(rate(http_server_duration_milliseconds_count{exported_job="wallet-api",http_status_code=~"5.."}[5m])) or vector(0)
```

p95 latency:

```promql
histogram_quantile(0.95, sum(rate(http_server_duration_milliseconds_bucket{exported_job="wallet-api"}[5m])) by (le))
```

Всего запросов за час:

```promql
sum(increase(http_server_duration_milliseconds_count{exported_job="wallet-api"}[1h]))
```

### Loki (логи)

Только ошибки:

```logql
{service="wallet-api"} | json | level="ERROR"
```

Все логи сервиса:

```logql
{service="wallet-api"}
```

По trace_id (надёжнее — поиск по подстроке):

```logql
{service="wallet-api"} |= "ВСТАВЬТЕ_trace_id"
```

Готовые графики без ручных запросов: **Dashboards → Wallet API — RED**.
