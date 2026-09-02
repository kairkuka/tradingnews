# ТЗ ДЛЯ CODEX

# Historical News Impact & Market Reaction Intelligence Bot

## 1. Название проекта

**News Impact Intelligence Bot**

Рабочая задача:

> Создать систему, которая в реальном времени мониторит экономические и рыночные новости, сопоставляет их с историческими событиями, анализирует фактическую реакцию финансовых активов после аналогичных событий и показывает пользователю статистически обоснованный исторический сценарий.

Система **не должна выдавать торговые сигналы BUY/SELL** и не должна автоматически открывать сделки.

Главный принцип:

> AI объясняет исторические данные, но не придумывает их.

---

# 2. Основная задача

Пользователь торгует:

### Metals

* Gold
* Silver

### Index Futures

* MNQ
* NQ

### Energy

* Crude Oil / WTI

### Crypto

* BTC

### FX

* EURUSD
* GBPUSD
* USDJPY
* AUDUSD
* USDCAD
* USDCHF

Бот должен отвечать на вопрос:

> «Когда сейчас произошло событие X, что исторически происходило с этими активами после похожих событий?»

Например:

```text
US CPI

Actual: 3.1%
Forecast: 3.3%
Previous: 3.4%

Surprise: -0.20%
```

Бот должен найти исторические CPI releases с похожим surprise и сравнить реакцию:

```text
XAUUSD
XAGUSD
MNQ
BTC
EURUSD
USDJPY
CL
```

на горизонтах:

```text
1m
5m
15m
30m
1h
2h
4h
1D
```

---

# 3. Главный принцип архитектуры

Систему разделить на 4 независимых слоя:

```text
DATA
 ↓
STATISTICS
 ↓
AI
 ↓
PRESENTATION
```

### DATA

Получение:

* economic calendar
* news
* market data
* macro data
* rates
* DXY
* VIX
* commodities context

### STATISTICS

Расчёт:

* surprise
* historical matching
* returns
* probability
* median
* percentiles
* MFE
* MAE
* confidence
* market regime

### AI

Только:

* классификация новостей
* извлечение смысла
* semantic matching
* формирование текстового объяснения

### PRESENTATION

* Telegram
* Web dashboard

---

# 4. Supported Assets

Создать конфигурационный registry.

```python
SUPPORTED_ASSETS = {
    "XAUUSD": {
        "name": "Gold",
        "class": "METAL"
    },

    "XAGUSD": {
        "name": "Silver",
        "class": "METAL"
    },

    "MNQ": {
        "name": "Nasdaq Micro E-mini",
        "class": "INDEX_FUTURE"
    },

    "NQ": {
        "name": "Nasdaq E-mini",
        "class": "INDEX_FUTURE"
    },

    "CL": {
        "name": "Crude Oil WTI",
        "class": "ENERGY"
    },

    "WTI": {
        "name": "West Texas Intermediate",
        "class": "ENERGY"
    },

    "BTCUSDT": {
        "name": "Bitcoin",
        "class": "CRYPTO"
    },

    "EURUSD": {
        "name": "Euro / USD",
        "class": "FX"
    },

    "GBPUSD": {
        "name": "British Pound / USD",
        "class": "FX"
    },

    "USDJPY": {
        "name": "USD / Japanese Yen",
        "class": "FX"
    },

    "AUDUSD": {
        "name": "Australian Dollar / USD",
        "class": "FX"
    },

    "USDCAD": {
        "name": "USD / Canadian Dollar",
        "class": "FX"
    },

    "USDCHF": {
        "name": "USD / Swiss Franc",
        "class": "FX"
    }
}
```

Не хардкодить тикеры в бизнес-логике.

---

# 5. Economic Events

В MVP поддержать следующие события.

## Inflation

```text
CPI
Core CPI
PCE
Core PCE
PPI
Core PPI
```

## Employment

```text
NFP
Non-Farm Payrolls
Unemployment Rate
Average Hourly Earnings
Initial Jobless Claims
Continuing Claims
JOLTS
ADP Employment
```

## Growth

```text
GDP
Retail Sales
Industrial Production
Durable Goods
```

## Business Activity

```text
ISM Manufacturing
ISM Services
Manufacturing PMI
Services PMI
Composite PMI
```

## Consumer

```text
Consumer Confidence
Michigan Consumer Sentiment
```

## Housing

```text
Housing Starts
Building Permits
Existing Home Sales
New Home Sales
```

## Federal Reserve

```text
FOMC Rate Decision
FOMC Statement
FOMC Minutes
Powell Press Conference
Fed Speaker
```

---

# 6. Oil-specific events

Для Crude Oil создать отдельную группу.

```text
EIA Crude Oil Inventories
EIA Gasoline Inventories
EIA Distillate Inventories
API Crude Inventories
OPEC Meeting
OPEC+ Meeting
OPEC Production Decision
Saudi Production
US Production
US Oil Rig Count
SPR Release
SPR Refill
```

Также отслеживать новости:

```text
Iran
Iraq
Saudi Arabia
Russia
Ukraine
Middle East
Red Sea
Hormuz
sanctions
oil embargo
production cuts
production increases
pipeline disruptions
refinery outages
```

---

# 7. Silver-specific context

Для Silver дополнительно собирать:

```text
Gold price
Gold return
Gold/Silver ratio
DXY
US10Y
real yields
industrial metals
China macro data
```

Главная дополнительная метрика:

```text
GOLD_SILVER_RATIO
```

Бот должен понимать:

```text
Gold ↑
Silver ↑
Gold/Silver ratio ↓
```

или:

```text
Gold ↑
Silver ↓
Gold/Silver ratio ↑
```

Это важно для анализа XAGUSD.

---

# 8. Gold-specific context

Для Gold:

```text
DXY
US10Y
real yields
VIX
Gold
Silver
Gold/Silver ratio
Fed expectations
```

---

# 9. MNQ/NQ context

Для Nasdaq:

```text
NQ
MNQ
VIX
US10Y
DXY
S&P 500
Russell 2000
Treasury yields
```

Минимально обязательно:

```text
MNQ/NQ
VIX
US10Y
DXY
```

---

# 10. BTC context

Для Bitcoin:

```text
BTC
ETH
DXY
US10Y
Nasdaq
VIX
BTC volatility
```

Основные cross-asset relationships:

```text
BTC ↔ Nasdaq
BTC ↔ DXY
BTC ↔ liquidity/rates
```

---

# 11. FX context

Для FX:

```text
DXY
US10Y
VIX
relevant central bank
relevant country data
```

Например EURUSD:

```text
EURUSD
DXY
US10Y
ECB
Eurozone CPI
Eurozone PMI
```

USDJPY:

```text
USDJPY
US10Y
JGB yields if available
BOJ
DXY
```

USDCAD:

```text
USDCAD
WTI
BoC
US data
Canada data
```

Особенно учитывать связь:

```text
USDCAD ↔ Crude Oil
```

---

# 12. Economic Calendar Provider

Создать абстракцию:

```python
class EconomicCalendarProvider(ABC):

    async def get_upcoming_events(...)
    async def get_historical_events(...)
    async def get_event(...)
```

Provider должен быть заменяемым.

Архитектура:

```text
providers/
    economic/
        base.py
        primary.py
        fallback.py
```

Не делать бизнес-логику зависимой от конкретного API.

---

# 13. News Provider

Создать:

```python
class NewsProvider(ABC):

    async def get_latest_news(...)
    async def search_news(...)
```

Каждая новость:

```json
{
    "id": "...",
    "timestamp": "...",
    "source": "...",
    "title": "...",
    "body": "...",
    "url": "...",
    "language": "en",
    "country": "US"
}
```

---

# 14. Market Data Provider

Создать:

```python
class MarketDataProvider(ABC):

    async def get_ohlcv(...)
    async def get_latest_price(...)
    async def get_quote(...)
}
```

Поддержать:

```text
1m
5m
15m
30m
1h
2h
4h
1D
```

Все timestamps:

```text
UTC
```

---

# 15. Database

Использовать:

```text
PostgreSQL
SQLAlchemy
Alembic
Redis
```

При наличии возможности:

```text
pgvector
```

---

# 16. Database: events

```sql
events
---------
id UUID PRIMARY KEY

timestamp TIMESTAMP WITH TIME ZONE

country VARCHAR
currency VARCHAR

category VARCHAR
event_type VARCHAR
title TEXT

importance VARCHAR

actual NUMERIC
forecast NUMERIC
previous NUMERIC
revision NUMERIC

unit VARCHAR

surprise NUMERIC
surprise_pct NUMERIC
surprise_zscore NUMERIC

directionality VARCHAR

source VARCHAR
source_url TEXT

created_at TIMESTAMP
updated_at TIMESTAMP
```

---

# 17. Database: news

```sql
news
---------
id UUID PRIMARY KEY

timestamp TIMESTAMP WITH TIME ZONE

source VARCHAR
title TEXT
body TEXT
url TEXT

country VARCHAR
language VARCHAR

event_id UUID NULL

category VARCHAR
importance VARCHAR

sentiment VARCHAR
sentiment_score NUMERIC

embedding VECTOR NULL

created_at TIMESTAMP
```

---

# 18. Database: assets

```sql
assets
---------
id UUID PRIMARY KEY

symbol VARCHAR UNIQUE

display_name VARCHAR
asset_class VARCHAR

exchange VARCHAR
currency VARCHAR

timezone VARCHAR

enabled BOOLEAN
```

---

# 19. Database: candles

```sql
candles
---------
id BIGSERIAL PRIMARY KEY

symbol VARCHAR
timeframe VARCHAR

timestamp TIMESTAMP WITH TIME ZONE

open NUMERIC
high NUMERIC
low NUMERIC
close NUMERIC
volume NUMERIC

UNIQUE(symbol, timeframe, timestamp)
```

Индексы:

```text
(symbol, timestamp)
(symbol, timeframe, timestamp)
```

---

# 20. Database: market context

```sql
market_context
---------
id UUID PRIMARY KEY

event_id UUID
symbol VARCHAR

timestamp TIMESTAMP WITH TIME ZONE

trend VARCHAR

atr NUMERIC
atr_percentile NUMERIC

rsi NUMERIC

dxy_change NUMERIC
us10y_change NUMERIC
vix NUMERIC

gold_change NUMERIC
silver_change NUMERIC

gold_silver_ratio NUMERIC

oil_change NUMERIC
btc_change NUMERIC
nq_change NUMERIC

session VARCHAR

volatility_regime VARCHAR

distance_from_daily_high NUMERIC
distance_from_daily_low NUMERIC
```

---

# 21. Database: Event reactions

```sql
event_reactions
---------
id UUID PRIMARY KEY

event_id UUID
symbol VARCHAR

horizon VARCHAR

price_before NUMERIC
price_after NUMERIC

return_pct NUMERIC

high_after NUMERIC
low_after NUMERIC

max_favorable_excursion NUMERIC
max_adverse_excursion NUMERIC

volatility_before NUMERIC
volatility_after NUMERIC

volume_before NUMERIC
volume_after NUMERIC

created_at TIMESTAMP
```

---

# 22. Database: Historical statistics

Создать materialized/calculated statistics table:

```sql
historical_statistics
---------
id UUID PRIMARY KEY

event_type VARCHAR
symbol VARCHAR
horizon VARCHAR

sample_size INTEGER

up_count INTEGER
down_count INTEGER

up_probability NUMERIC
down_probability NUMERIC

mean_return NUMERIC
median_return NUMERIC
std_return NUMERIC

p10 NUMERIC
p25 NUMERIC
p50 NUMERIC
p75 NUMERIC
p90 NUMERIC

median_mfe NUMERIC
median_mae NUMERIC

confidence VARCHAR

updated_at TIMESTAMP
```

---

# 23. Event normalization

Все economic events привести к единому виду.

Например:

```text
US CPI
Actual: 3.1
Forecast: 3.3
Previous: 3.4
```

↓

```json
{
    "event_type": "US_CPI",
    "actual": 3.1,
    "forecast": 3.3,
    "previous": 3.4,
    "surprise": -0.2
}
```

---

# 24. Surprise

Основная формула:

```python
surprise = actual - forecast
```

Но учитывать economic directionality.

Например:

```text
CPI:
higher = hawkish
lower = dovish

Unemployment:
higher = dovish
lower = hawkish
```

Создать configuration:

```python
EVENT_DIRECTIONALITY = {
    "US_CPI": "HIGHER_IS_HAWKISH",
    "US_CORE_CPI": "HIGHER_IS_HAWKISH",
    "US_UNEMPLOYMENT": "HIGHER_IS_DOVISH",
    "US_NFP": "HIGHER_IS_HAWKISH",
}
```

---

# 25. Surprise normalization

Для каждого event type:

```python
z_score = (
    surprise - historical_mean
) / historical_std
```

Хранить:

```text
surprise
surprise_pct
surprise_zscore
```

Historical matching должен в первую очередь учитывать:

```text
surprise_zscore
```

а не только абсолютное значение.

---

# 26. Historical Matching Engine

Создать:

```text
services/historical_matcher.py
```

API:

```python
find_similar_events(
    current_event,
    symbol,
    lookback_years=10,
    min_samples=20
)
```

---

# 27. Structured Event Matching

Для CPI искать CPI.

Для NFP искать NFP.

Для FOMC искать FOMC.

Не смешивать разные типы событий без explicit fallback.

Основные similarity factors:

```text
event type
surprise
surprise z-score
market regime
volatility regime
DXY regime
US10Y regime
session
```

---

# 28. Similarity Score

Начальная модель:

```python
score = (
    event_type_score * 0.25 +
    surprise_score * 0.30 +
    regime_score * 0.15 +
    volatility_score * 0.10 +
    dxy_score * 0.10 +
    yield_score * 0.10
)
```

Каждый компонент:

```text
0.0 → 1.0
```

---

# 29. Matching modes

Поддержать:

```text
STRICT
RELAXED
```

STRICT:

```text
similarity >= 0.80
```

RELAXED:

```text
>= 0.70
```

затем:

```text
>= 0.60
```

если недостаточно данных.

Никогда не использовать низкокачественную выборку без указания:

```text
LOW CONFIDENCE
```

---

# 30. Historical horizons

Для каждого события рассчитывать:

```text
1m
5m
15m
30m
1h
2h
4h
1D
```

Return:

```python
return_pct = (
    price_after / price_before - 1
) * 100
```

---

# 31. MFE / MAE

Для каждого horizon:

```text
MFE
MAE
```

Например:

```text
30m:

Median MFE: +0.61%
Median MAE: -0.17%
```

Это показывает не только конечный результат, но и характер движения.

---

# 32. Reaction classification

Для каждого события определить:

```text
IMMEDIATE
DELAYED
REVERSAL
CONTINUATION
NO_SIGNIFICANT_MOVE
```

Например:

```text
T+5m: +0.40%
T+30m: +0.70%
T+1h: +0.10%
T+4h: -0.20%
```

Можно классифицировать как:

```text
initial bullish
then reversal
```

Но классификация должна рассчитываться алгоритмически.

---

# 33. Pre-event analysis

Обязательно анализировать:

```text
T-60m
T-30m
T-15m
T-5m
```

Например:

```text
Gold before CPI:

60m: +0.31%
30m: +0.19%
5m: +0.05%
```

Если pre-event movement большой:

```text
PRE-EVENT MOVE: HIGH
```

---

# 34. Current Market Context

Перед формированием отчёта получить:

```text
price
ATR
ATR percentile
trend
volatility regime
DXY
US10Y
VIX
Gold
Silver
Gold/Silver ratio
Oil
BTC
NQ
session
```

В зависимости от asset дополнительно использовать relevant context.

---

# 35. Market Regime

Использовать deterministic logic.

Основные режимы:

```text
UPTREND
DOWNTREND
RANGE
```

Базовая структура:

```text
HH + HL = UPTREND
LH + LL = DOWNTREND
otherwise = RANGE
```

Дополнительно:

```text
EMA20
EMA50
ATR
```

Но EMA не должна заменять market structure.

---

# 36. Volatility Regime

Определить:

```text
LOW
NORMAL
HIGH
EXTREME
```

Использовать:

```text
ATR percentile
realized volatility
```

---

# 37. Cross-Asset Engine

Каждое важное событие анализировать относительно:

```text
XAUUSD
XAGUSD
MNQ
NQ
CL
BTC
EURUSD
GBPUSD
USDJPY
DXY
US10Y
VIX
```

Пример:

```text
CPI below forecast

DXY: -0.42%
US10Y: -0.17%
Gold: +0.47%
Silver: +0.62%
MNQ: +0.38%
EURUSD: +0.31%
USDJPY: -0.29%
BTC: +0.12%
Oil: +0.08%
```

Все значения должны быть рассчитаны из market data.

---

# 38. Asset-specific relationships

Система должна поддерживать relationship registry.

### Gold

```text
Gold ↔ DXY
Gold ↔ US10Y
Gold ↔ real yields
Gold ↔ Silver
```

### Silver

```text
Silver ↔ Gold
Silver ↔ Gold/Silver ratio
Silver ↔ DXY
Silver ↔ US10Y
Silver ↔ China data
```

### MNQ

```text
MNQ ↔ US10Y
MNQ ↔ VIX
MNQ ↔ DXY
```

### BTC

```text
BTC ↔ MNQ
BTC ↔ DXY
BTC ↔ US10Y
BTC ↔ VIX
```

### Crude Oil

```text
WTI ↔ USD
WTI ↔ inventories
WTI ↔ OPEC
WTI ↔ geopolitical risk
```

### USDCAD

```text
USDCAD ↔ WTI
```

---

# 39. Breaking News Engine

Обычные новости не всегда имеют:

```text
actual
forecast
previous
```

Поэтому отдельный pipeline:

```text
NEWS
↓
CLASSIFICATION
↓
IMPACT CATEGORY
↓
SEMANTIC MATCHING
↓
HISTORICAL EVENTS
↓
MARKET REACTION
```

---

# 40. News categories

Поддержать:

```text
GEOPOLITICAL
WAR
SANCTIONS
TARIFF
TRADE
CENTRAL_BANK
INTERVENTION
ENERGY
BANKING
FINANCIAL_CRISIS
POLITICAL
REGULATION
CRYPTO
COMMODITY
```

---

# 41. Semantic matching

Использовать embeddings только для unstructured news.

PostgreSQL:

```text
pgvector
```

Similarity:

```text
cosine similarity
```

Например:

```text
"US imposes new 25% tariff on Chinese goods"
```

искать:

```text
tariff
trade war
China-US
trade restrictions
sanctions
```

---

# 42. Structured + Semantic matching

Для economic events:

```text
STRUCTURED MATCHER
```

Для breaking news:

```text
SEMANTIC MATCHER
```

Не смешивать два алгоритма в один непрозрачный score.

---

# 43. AI Layer

LLM используется для:

```text
news classification
event extraction
semantic interpretation
natural-language explanation
```

LLM НЕ используется для:

```text
return calculation
probability calculation
median
mean
MFE
MAE
confidence
historical statistics
```

---

# 44. AI input

Передавать LLM только structured information:

```json
{
    "event": {},
    "historical_statistics": {},
    "similar_events": [],
    "current_context": {},
    "cross_asset_reaction": {}
}
```

---

# 45. AI output

Строго JSON:

```json
{
    "summary": "...",
    "assets": [
        {
            "symbol": "XAUUSD",
            "historical_bias": "BULLISH",
            "strength": 8,
            "confidence": "HIGH",
            "reason": "...",
            "key_horizon": "30m"
        }
    ],
    "risk_notes": []
}
```

Использовать Pydantic validation.

---

# 46. Anti-Hallucination Prompt

System prompt LLM:

```text
You are a historical market reaction analyst.

You must NEVER invent statistics.

Every numerical claim must come from the supplied dataset.

You must not create historical events that are not provided.

You must not calculate statistics yourself when the backend has already provided them.

If the sample is insufficient, say:
INSUFFICIENT DATA.

Do not issue BUY or SELL instructions.

Do not present historical probability as a guaranteed future outcome.

Use only the supplied market context.

Clearly distinguish:
historical observation
current market context
uncertainty.
```

---

# 47. Historical confidence

Использовать:

```text
HIGH
MEDIUM
LOW
INSUFFICIENT
```

Например:

```text
N >= 50 → HIGH
N = 30-49 → MEDIUM
N = 15-29 → LOW
N < 15 → INSUFFICIENT
```

Thresholds configurable.

---

# 48. Bootstrap confidence interval

Для:

```text
win rate
median return
```

рассчитывать bootstrap confidence intervals.

Например:

```text
UP probability:
74%

95% CI:
58% - 86%
```

---

# 49. Outlier protection

Основной показатель:

```text
MEDIAN
```

Дополнительно:

```text
MEAN
P25
P50
P75
P90
```

Не использовать mean как единственную характеристику.

---

# 50. Statistical Impact Score

Создать:

```python
impact_score()
```

Диапазон:

```text
-100 → +100
```

Интерпретация:

```text
+80 to +100
Strong historical bullish

+40 to +79
Moderate bullish

-39 to +39
Neutral / mixed

-40 to -79
Moderate bearish

-80 to -100
Strong historical bearish
```

Это называется:

```text
HISTORICAL IMPACT SCORE
```

Не:

```text
TRADE SIGNAL
```

---

# 51. Telegram Bot

Использовать:

```text
aiogram 3.x
```

Команды:

```text
/start
/status
/news
/events
/analyze
/history
/assets
/settings
/help
```

---

# 52. Telegram automatic alerts

Перед high-impact event:

```text
60 min
30 min
5 min
```

После release:

```text
immediately
```

и дополнительные:

```text
15m
30m
1h
```

post-event updates.

---

# 53. Pre-event Telegram message

Пример:

```text
⏰ HIGH IMPACT EVENT IN 30 MIN

🇺🇸 US CPI

Forecast: 3.3%
Previous: 3.4%

Historical data available:

XAUUSD: 34 events
XAGUSD: 34 events
MNQ: 31 events
BTC: 28 events
EURUSD: 29 events
CL: 27 events

Current context:

Gold: UPTREND
Silver: UPTREND
MNQ: RANGE
BTC: UPTREND
Oil: DOWNTREND
DXY: UP
US10Y: UP
```

---

# 54. Release Telegram message

Пример:

```text
🚨 US CPI RELEASED

Actual: 3.1%
Forecast: 3.3%
Previous: 3.4%

Surprise:
-0.20%

Z-score:
-1.42
```

---

# 55. Historical analysis

```text
━━━━━━━━━━━━━━
🥇 XAUUSD

30m:
UP 74%

Median:
+0.42%

Sample:
34

Confidence:
HIGH

1H:
UP 77%

Median:
+0.55%
```

---

# 56. Silver

```text
━━━━━━━━━━━━━━
🥈 XAGUSD

30m:
UP 79%

Median:
+0.58%

Sample:
34

Confidence:
HIGH

Gold/Silver ratio:
historically tends to decline after similar events
```

Последняя фраза должна формироваться только на основании рассчитанных данных.

---

# 57. MNQ

```text
━━━━━━━━━━━━━━
📈 MNQ

30m:
UP 64%

Median:
+0.31%

Sample:
31

Confidence:
MEDIUM
```

---

# 58. Oil

```text
━━━━━━━━━━━━━━
🛢 WTI

30m:
UP 57%

Median:
+0.11%

Sample:
27

Confidence:
LOW
```

---

# 59. BTC

```text
━━━━━━━━━━━━━━
₿ BTC

30m:
UP 55%

Median:
+0.08%

Sample:
28

Confidence:
LOW
```

---

# 60. Final AI summary

Пример:

```text
AI HISTORICAL SUMMARY

The strongest historical alignment is currently
visible in XAUUSD and XAGUSD.

MNQ shows a weaker positive historical reaction.

BTC shows no meaningful historical edge.

Oil reaction is mixed.

Current market context should be considered separately
from the historical event statistics.

This analysis describes historical market behavior and
is not a trading signal.
```

---

# 61. Post-event validation

После события система должна сравнить:

```text
historical expectation
vs
actual reaction
```

Например:

```text
XAUUSD

Historical:
+0.42% / 30m

Actual:
+0.51%

Result:
MATCH
```

---

# 62. Event lifecycle

```text
SCHEDULED
↓
PRE_EVENT
↓
RELEASED
↓
NORMALIZED
↓
HISTORICAL_MATCHED
↓
ANALYZED
↓
POST_EVENT
↓
VALIDATED
```

---

# 63. Backtesting

Создать:

```bash
python -m app.backtest.news
```

Backtest должен:

1. брать исторические события;
2. использовать только данные до события;
3. строить historical matching;
4. формировать prediction;
5. сравнивать с фактической реакцией;
6. сохранять результат.

---

# 64. Walk-forward validation

Пример:

```text
Training:
2016-2022

Validation:
2023

Training:
2016-2023

Validation:
2024

Training:
2016-2024

Validation:
2025
```

Продолжать по годам, где доступны данные.

---

# 65. Look-ahead bias protection

Критическое правило:

Если событие:

```text
2026-09-02 15:30 UTC
```

исторический matcher имеет право использовать только:

```text
events < 2026-09-02 15:30 UTC
```

Нельзя использовать будущие события.

Также нельзя использовать future candles при расчёте current context.

---

# 66. Event-study dataset

Для каждого события создать относительную шкалу:

```text
T-60m
T-30m
T-15m
T-5m
T0
T+1m
T+5m
T+15m
T+30m
T+1h
T+2h
T+4h
T+1D
```

Это понадобится для графиков.

---

# 67. Dashboard

После MVP создать web UI.

Stack:

```text
Next.js
React
Tailwind
TradingView Lightweight Charts
```

Pages:

```text
/dashboard
/events
/events/:id
/assets/:symbol
/history
/backtest
/settings
```

---

# 68. Event chart

Показывать:

```text
historical median
25th percentile
75th percentile
actual reaction
```

На одной временной шкале:

```text
T0 = news release
```

---

# 69. Asset dashboard

Например:

```text
XAUUSD

News Impact History

CPI
NFP
FOMC
PCE
PPI

Best historical catalysts

Worst historical catalysts

Median reaction
Win rate
Average reaction
```

Для Silver:

```text
Gold/Silver relationship
```

Для Oil:

```text
EIA
OPEC
geopolitical
inventory
```

---

# 70. Natural language search

Пользователь должен иметь возможность:

```text
What usually happens to gold after CPI misses expectations?

How does MNQ react to hawkish Fed decisions?

What happens to silver when CPI comes below forecast?

How does oil react to EIA inventory surprises?

What happens to USDCAD when oil rallies?
```

Pipeline:

```text
USER QUERY
↓
LLM INTENT EXTRACTION
↓
STRUCTURED QUERY
↓
DATABASE
↓
STATISTICS ENGINE
↓
AI EXPLANATION
```

LLM не должен отвечать на статистический вопрос напрямую.

---

# 71. Natural language commands

Telegram:

```text
/analyze CPI
/analyze NFP
/analyze FOMC

/history CPI XAUUSD
/history CPI XAGUSD
/history NFP MNQ
/history EIA CL
```

---

# 72. News deduplication

Одна новость может приходить от нескольких источников.

Deduplication по:

```text
title similarity
timestamp proximity
event type
country
source
```

Создать:

```python
deduplicate_news()
```

---

# 73. Data Quality

Перед использованием данных проверить:

```text
missing candles
duplicate candles
timestamp errors
price <= 0
volume anomalies
large data gaps
```

Для economic data:

```text
missing forecast
missing actual
incorrect release timestamp
revision errors
```

---

# 74. Data Quality Grade

Каждый report должен иметь:

```text
A
B
C
INSUFFICIENT
```

Учитывать:

```text
sample size
market data completeness
timestamp accuracy
provider reliability
```

---

# 75. Timezone

В database:

```text
UTC
```

В Telegram:

```text
Asia/Almaty
```

Все conversion делать централизованно.

Нельзя использовать локальное время машины.

---

# 76. Futures sessions

Для MNQ/NQ учитывать:

```text
RTH
ETH
```

Также:

```text
Asia
London
New York
Overnight
```

Session configuration должна быть отдельным модулем.

---

# 77. Price reference

Для event reaction:

```text
T0 = official release timestamp
```

`price_before`:

последняя доступная цена перед T0.

Default:

```text
REFERENCE_PRICE_MODE=previous_close
```

Архитектура должна позволять:

```text
previous_close
last_tick
mid_price
```

---

# 78. Transaction costs

MVP:

```text
raw market reaction
```

Но архитектура должна поддерживать:

```text
spread
commission
slippage
```

Позже использовать их для реалистичного trade simulation.

---

# 79. Jobs

Создать:

```text
sync_calendar
sync_news
sync_market_data
calculate_reactions
calculate_context
rebuild_statistics
send_pre_event_alert
send_release_alert
send_post_event_update
```

---

# 80. Scheduler

MVP:

```text
APScheduler
```

Если нагрузка вырастет:

```text
Celery + Redis
```

Архитектура должна позволять заменить scheduler.

---

# 81. Project structure

```text
news-impact-bot/
│
├── app/
│   ├── main.py
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── assets.py
│   │   ├── event_types.py
│   │   └── relationships.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── models/
│   │   └── repositories/
│   │
│   ├── providers/
│   │   ├── economic/
│   │   ├── news/
│   │   └── market/
│   │
│   ├── services/
│   │   ├── event_normalizer.py
│   │   ├── surprise.py
│   │   ├── historical_matcher.py
│   │   ├── semantic_matcher.py
│   │   ├── reaction_engine.py
│   │   ├── statistics.py
│   │   ├── bootstrap.py
│   │   ├── market_context.py
│   │   ├── regime.py
│   │   ├── cross_asset.py
│   │   ├── news_classifier.py
│   │   └── report_generator.py
│   │
│   ├── ai/
│   │   ├── client.py
│   │   ├── prompts.py
│   │   └── schemas.py
│   │
│   ├── telegram/
│   │   ├── bot.py
│   │   ├── handlers/
│   │   ├── keyboards/
│   │   └── formatters/
│   │
│   ├── jobs/
│   │   ├── calendar.py
│   │   ├── news.py
│   │   ├── market.py
│   │   └── analysis.py
│   │
│   └── backtest/
│       ├── engine.py
│       ├── walk_forward.py
│       └── metrics.py
│
├── migrations/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── backtest/
│
├── scripts/
│   ├── import_events.py
│   ├── import_market_data.py
│   └── rebuild_statistics.py
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

---

# 82. Environment

Создать `.env.example`:

```env
DATABASE_URL=
REDIS_URL=

TELEGRAM_BOT_TOKEN=

LLM_API_KEY=

ECONOMIC_DATA_API_KEY=
NEWS_API_KEY=
MARKET_DATA_API_KEY=

TIMEZONE=Asia/Almaty

HISTORICAL_YEARS=10

MIN_SAMPLE_SIZE=20

STRICT_SIMILARITY=0.80
RELAXED_SIMILARITY=0.60

REFERENCE_PRICE_MODE=previous_close
```

Никаких ключей в Git.

---

# 83. Docker

Создать:

```text
postgres
redis
app
```

Migrations должны запускаться отдельно или автоматически через entrypoint.

---

# 84. Logging

Structured logging:

```text
timestamp
service
job
event_id
symbol
duration
status
records_processed
error
```

---

# 85. Error handling

Если provider не работает:

```text
retry
↓
fallback
↓
log
↓
admin alert
```

Если данные рынка отсутствуют:

не формировать статистику.

Не заменять отсутствующие данные выдуманными значениями.

---

# 86. Tests

Обязательно:

```text
test_surprise
test_directionality
test_zscore
test_similarity
test_return
test_mfe
test_mae
test_regime
test_volatility
test_confidence
test_bootstrap
test_timezone
test_deduplication
test_lookahead_protection
test_cross_asset
```

---

# 87. Integration tests

Проверить полный pipeline:

```text
EVENT
↓
NORMALIZE
↓
SURPRISE
↓
MATCH
↓
REACTION
↓
STATISTICS
↓
CONTEXT
↓
AI
↓
TELEGRAM
```

---

# 88. Backtest acceptance

Создать небольшой вручную проверяемый dataset.

Для каждого тестового event:

```text
release timestamp
price before
price after 15m
price after 30m
price after 1h
```

Автоматически сравнить расчёты.

---

# 89. Performance targets

Цели MVP:

```text
Historical query < 500ms

Statistical report < 2s

AI report < 5s

Telegram alert < 10s
```

LLM не должен блокировать ingestion.

---

# 90. Cache

Redis cache:

```text
current_market_context
historical_statistics
similar_events
asset_metadata
```

TTL:

```text
market context: 10-30 sec
statistics: 1-24h
similar events: 1-24h
```

---

# 91. Critical security rules

Нельзя:

```text
hardcode API keys
store Telegram secrets in database
log API keys
log private credentials
```

`.env` добавить в `.gitignore`.

---

# 92. Development phases

## PHASE 1 — Foundation

Создать:

```text
FastAPI
PostgreSQL
SQLAlchemy
Alembic
Redis
Pydantic
Docker
logging
configuration
```

Сделать migrations.

---

# 93. PHASE 2 — Assets & Market Data

Подключить:

```text
XAUUSD
XAGUSD
MNQ
NQ
CL
BTCUSDT
EURUSD
GBPUSD
USDJPY
AUDUSD
USDCAD
USDCHF
```

Реализовать:

```text
OHLCV ingestion
validation
storage
```

---

# 94. PHASE 3 — Economic Calendar

Реализовать:

```text
event ingestion
normalization
actual
forecast
previous
revision
surprise
z-score
```

---

# 95. PHASE 4 — Reaction Engine

Реализовать:

```text
1m
5m
15m
30m
1h
2h
4h
1D
```

Расчёты:

```text
return
MFE
MAE
volatility
volume
pre-event movement
```

---

# 96. PHASE 5 — Historical Matcher

Реализовать:

```text
structured matching
similarity score
strict mode
relaxed mode
market regime matching
volatility matching
DXY matching
US10Y matching
```

---

# 97. PHASE 6 — Statistics

Реализовать:

```text
win rate
median
mean
percentiles
bootstrap CI
confidence
impact score
```

---

# 98. PHASE 7 — Cross Asset

Добавить:

```text
Gold/Silver
BTC/NQ
USDCAD/Oil
Gold/DXY
Gold/US10Y
MNQ/US10Y
```

---

# 99. PHASE 8 — Telegram

Реализовать:

```text
/start
/events
/news
/analyze
/history
/assets
/settings
```

И automatic alerts.

---

# 100. PHASE 9 — AI

Только после полной готовности statistics engine.

Добавить:

```text
news classification
event interpretation
semantic matching
natural language report
```

---

# 101. PHASE 10 — Breaking News

Добавить:

```text
news providers
semantic embeddings
news deduplication
geopolitical matching
tariff matching
sanctions matching
energy news
central bank news
```

---

# 102. PHASE 11 — Backtesting

Создать:

```text
historical replay
walk-forward
look-ahead protection
prediction validation
```

Показатели:

```text
accuracy
direction accuracy
calibration
sample size
false positive rate
```

---

# 103. PHASE 12 — Web Dashboard

После стабильного Telegram MVP:

```text
Next.js
React
Tailwind
Lightweight Charts
```

---

# 104. Definition of Done

MVP считается готовым только если система способна:

### Event

Получить:

```text
CPI
Actual
Forecast
Previous
```

### Surprise

Рассчитать:

```text
absolute surprise
normalized surprise
z-score
```

### History

Найти:

```text
similar historical events
```

### Assets

Проанализировать минимум:

```text
Gold
Silver
MNQ
BTC
EURUSD
Crude Oil
```

### Horizons

```text
15m
30m
1h
4h
```

### Statistics

Показать:

```text
sample size
up probability
median return
percentiles
confidence
MFE
MAE
```

### Context

Показать:

```text
trend
volatility
DXY
US10Y
VIX
relevant cross-assets
```

### Telegram

Отправить:

```text
pre-event alert
release alert
historical analysis
post-event validation
```

### Safety

Гарантировать:

```text
no hallucinated statistics
no look-ahead bias
no fabricated events
no fake market data
no automatic trading
```

---

# 105. Главное требование к Codex

Не пытайся написать весь проект за один шаг.

Работай как senior Python/data engineer.

Для каждой Phase:

1. Сначала изучи существующую структуру проекта.
2. Создай минимально необходимый код.
3. Запусти tests.
4. Исправь ошибки.
5. Проверь migrations.
6. Проверь typing.
7. Проверь linting.
8. Обнови README.
9. Покажи краткий список изменённых файлов.
10. Покажи результаты тестов.
11. Только после успешного завершения переходи к следующей Phase.

Не удаляй работающий код без необходимости.

Не переписывай архитектуру без причины.

Не создавай mock implementations для production providers.

Mock/fixtures разрешены только для automated tests.

Если внешний API требует ключ — создать interface, configuration и integration layer, а отсутствие ключа не должно ломать запуск unit tests.

---

# 106. Главный критерий качества

Система должна отвечать не:

> «AI думает, что золото вырастет».

А:

> «За последние N лет произошло X сопоставимых событий. В Y% случаев Gold рос в течение 30 минут. Медианная реакция составила Z%. При этом текущий market regime соответствует/не соответствует исторической выборке».

И отдельно:

> «Current market context: ...»

И отдельно:

> «Historical impact is not a trading signal.»

---

# 107. Первое задание Codex

Начать только с **PHASE 1**.

После завершения Phase 1 остановиться и предоставить:

```text
1. Project structure
2. Created files
3. Database schema
4. Docker configuration
5. Environment configuration
6. Tests
7. Test results
8. How to run locally
9. Any unresolved issues
```

Не переходить к Phase 2 автоматически до проверки Phase 1.
