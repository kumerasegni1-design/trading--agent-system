# Enhanced Data Sources Integration

## 📥 Free Tick & 1-Minute Data Providers

### 1. **Dukascopy (RECOMMENDED - FREE TICK DATA)**

**What it provides:**
- ✅ Tick-level data (every transaction)
- ✅ 1-minute OHLC data
- ✅ Forex: All major, minor pairs
- ✅ Indices: SPX500, DAX, FTSE, Stoxx50e, etc.
- ✅ 20+ years of historical data
- ✅ **Completely FREE - no API key needed**

**Installation:**
```bash
pip install dukascopy-tools
```

**Usage:**
```bash
# Download tick data
duka EURUSD -tf t1 -from 2024-01-01 -to 2024-01-31 -f csv

# Download 1-minute OHLC
duka EURUSD -tf m1 -from 2024-01-01 -to 2024-01-31 -f csv

# Download indices
duka SPX500 -tf m1 -from 2024-01-01 -to 2024-01-31 -f csv
```

**Python Integration:**
```python
from backend.integrations.data_downloaders import DukascopyToolsDownloader

duka = DukascopyToolsDownloader()

# Tick data
tick_df = await duka.download_tick_data('EURUSD', '2024-01-01', '2024-01-31')
# Returns: DataFrame with columns [timestamp, bid, ask, bid_volume, ask_volume]

# 1-minute OHLC
minute_df = await duka.download_minute_ohlc('EURUSD', '2024-01-01', '2024-01-31')
# Returns: DataFrame with columns [timestamp, open, close, low, high, volume]
```

**Data Quality:** ⭐⭐⭐⭐⭐ (Institutional grade)
**File Size:** ~500MB per month per pair
**Supported Symbols:** 100+ Forex pairs + Indices

---

### 2. **HistData.com (VERY POPULAR - 1-MIN OHLC)**

**What it provides:**
- ✅ 1-minute OHLC data
- ✅ Forex pairs (19+ major/minor)
- ✅ Very high quality, widely used
- ✅ **FREE - requires manual CSV download**

**How to get data:**
1. Go to: https://www.histdata.com/download-free-forex-data/
2. Select pair (e.g., EURUSD)
3. Select year/month
4. Download ZIP file
5. Extract CSV
6. Place in `./data/histdata/`

**Python Integration:**
```python
from backend.services.enhanced_data_service import EnhancedDataService

data_service = EnhancedDataService()

# Load from pre-downloaded CSV
df = data_service.histdata.load_csv('EURUSD', year=2024, month=1)
# Returns: DataFrame with 1-minute OHLC
```

**Data Quality:** ⭐⭐⭐⭐⭐ (Trader favorite)
**File Size:** ~50MB per month
**Supported Symbols:** 20 Forex pairs

---

### 3. **Investing.com via InvestPy (FREE - LIVE SCRAPING)**

**What it provides:**
- ✅ 1-minute to daily data
- ✅ Forex, Stocks, Indices, Crypto
- ✅ **FREE for educational use**
- ❌ Real-time scraping (slower)

**Installation:**
```bash
pip install investpy
```

**Python Integration:**
```python
df = await EnhancedDataService().alternatives.download_from_investpy(
    'EURUSD', '2024-01-01', '2024-01-31'
)
```

---

### 4. **Polygon.io (STOCKS/INDICES - FREE TIER)**

**What it provides:**
- ✅ 1-minute tick data
- ✅ US stocks & indices
- ✅ Crypto (with premium)
- ❌ **Forex not supported**
- Free tier: 5 API calls/minute

**Setup:**
1. Sign up: https://polygon.io
2. Get free API key
3. Set environment: `export POLYGON_API_KEY=your_key`

**Python Integration:**
```python
df = await EnhancedDataService().alternatives.download_from_polygon(
    'AAPL', '2024-01-01', '2024-01-31',
    api_key='your_api_key'
)
```

---

### 5. **Yahoo Finance (STOCKS/INDICES - LIMITED)**

**What it provides:**
- ✅ Daily to minute data
- ✅ Stocks, ETFs, indices
- ✅ **FREE - no API key**
- ❌ Forex limited
- ⚠️ Rate limited

**Installation:**
```bash
pip install yfinance
```

---

## 📊 Multi-Timeframe Support

Our system automatically aggregates 1-minute data to:
- **1m** (base)
- **5m**
- **15m**
- **30m**
- **1h**
- **4h**
- **1d**

**Example:**
```python
data_service = EnhancedDataService()

# Download same data in all timeframes
multi_tf = await data_service.download_multi_timeframe(
    'EURUSD',
    start_date='2024-01-01',
    end_date='2024-01-31',
    timeframes=['1m', '5m', '15m', '1h', '4h', '1d']
)

for tf, df in multi_tf.items():
    print(f"{tf}: {len(df)} candles")
```

---

## 🌍 Bulk Downloads

### Download All Major Forex Pairs
```python
data_service = EnhancedDataService()

forex_data = await data_service.download_forex_major_pairs(
    start_date='2024-01-01',
    end_date='2024-01-31',
    timeframe='1m'  # or '5m', '15m', '1h', etc.
)

for pair, df in forex_data.items():
    print(f"{pair}: {len(df)} candles")
```

**Pairs included:**
- Majors: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD
- Crosses: EURJPY, EURGBP, GBPJPY

### Download All Indices
```python
indices_data = await data_service.download_indices(
    start_date='2024-01-01',
    end_date='2024-01-31',
    timeframe='1m'
)

for index, df in indices_data.items():
    print(f"{index}: {len(df)} candles")
```

**Indices included:**
- SPX500 (S&P 500)
- DAX (DAX 40)
- FTSE (FTSE 100)
- STOXX50E (Euro Stoxx 50)
- HSI (Hang Seng)
- N225 (Nikkei 225)

---

## 🔄 Integration with Trading Agent System

### API Endpoint
```bash
POST /api/data/download
{
    "symbol": "EURUSD",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "data_type": "tick"  # or "minute" or "multi_timeframe"
    "timeframes": ["1m", "5m", "15m", "1h"]
    "source": "dukascopy"  # or "histdata", "investpy"
}
```

---

## 📈 Performance Comparison

| Provider | Tick Data | Min OHLC | Forex | Indices | API Key | Speed | Quality |
|----------|-----------|----------|-------|---------|---------|-------|----------|
| Dukascopy | ✅ | ✅ | ✅ | ✅ | ❌ | ⚡ | ⭐⭐⭐⭐⭐ |
| HistData | ❌ | ✅ | ✅ | ❌ | ❌ | ⚡ | ⭐⭐⭐⭐⭐ |
| Investing.com | ❌ | ✅ | ✅ | ✅ | ❌ | 🐌 | ⭐⭐⭐⭐ |
| Polygon.io | ✅ | ✅ | ❌ | ✅ | ✅ | ⚡ | ⭐⭐⭐⭐ |
| Yahoo Finance | ❌ | ✅ | ⚠️ | ✅ | ❌ | ⚡ | ⭐⭐⭐ |

---

## 🎯 Recommended Setup

### For Maximum Data Coverage:
```python
# Primary: Dukascopy for Forex & Indices
data_service = EnhancedDataService()

# Get all Forex majors in multiple timeframes
forex = await data_service.download_forex_major_pairs(
    '2024-01-01', '2024-12-31', timeframe='1m'
)

# Get all indices
indices = await data_service.download_indices(
    '2024-01-01', '2024-12-31', timeframe='1m'
)
```

### For Backtest Accuracy:
```python
# Use tick data for best accuracy
tick_df = await data_service.download_tick_data(
    'EURUSD', '2024-01-01', '2024-01-31'
)

# Aggregate tick data to 1-minute for processing
minute_df = tick_df.resample('1T').agg({
    'bid': 'first',
    'ask': 'first',
    'bid_volume': 'sum',
    'ask_volume': 'sum'
})
```

---

## ⚠️ Important Notes

1. **Tick data is LARGE**: ~500MB per month per pair
2. **Download times**: Can take 5-30 minutes depending on date range
3. **Dukascopy is the only truly FREE tick provider** for Forex
4. **No authentication needed** for Dukascopy (use publicly available data feeds)
5. **Multi-timeframe aggregation** is accurate from 1-minute base data
6. **Data validation** is recommended before backtesting

---

## 🐛 Troubleshooting

### Connection Issues
```bash
# Test Dukascopy connectivity
curl https://datafeed.dukascopy.com/datafeed/EURUSD/2024/0/1/00h_quotes.bi5 -I
```

### Slow Downloads
- Use smaller date ranges
- Consider using cloud GPU for processing
- Implement parallel downloads per week

### Missing Data
- Dukascopy may have gaps on weekends/holidays
- Check data quality before backtesting
- Use alternative source if needed

---

## 📚 References

- Dukascopy: https://github.com/femtotrader/dukascopy-tools
- HistData: https://www.histdata.com
- InvestPy: https://github.com/alvarobartt/investpy
- Polygon.io: https://polygon.io
- Yahoo Finance: https://github.com/ranaroussi/yfinance
