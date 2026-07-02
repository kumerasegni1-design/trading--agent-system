# Trading Agent System - Quick Start Guide

## 🚀 Installation

### Prerequisites
- Docker & Docker Compose
- Git
- 4GB+ RAM
- Python 3.10+ (if running locally without Docker)

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/kumerasegni1-design/trading--agent-system.git
cd trading--agent-system

# Setup
make setup

# Update .env with your credentials
cp .env.example .env
vim .env  # Edit with your API keys

# Start system
make up
```

### Option 2: Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start backend
cd backend
uvicorn app:app --reload

# In another terminal, start frontend
cd frontend
npm install
npm start

# In another terminal, start Ollama
ollama serve
```

## 📖 Usage

### Access Dashboard
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Jupyter**: http://localhost:8888 (token: trading-agent)

### Example Commands

#### 1. Generate Strategy
```
Prompt: "Generate a mean reversion strategy on EUR/USD using RSI, backtest it, and deploy if it passes all checks."
```

#### 2. Research-Based Strategy
```
Prompt: "Research the latest mean reversion papers, generate a strategy based on findings, backtest, and deploy."
```

#### 3. ML Model Training
```
Prompt: "Create a random forest model to predict EUR/USD direction, train on 5 years of data using Colab GPU, backtest, and deploy."
```

## 🤖 Agent Roles

| Agent | Purpose |
|-------|----------|
| **Strategy Generator** | Creates novel trading strategies |
| **Data Downloader** | Fetches historical data |
| **Backtesting Critic** | Detects overfitting, data leakage |
| **ML Trainer** | Trains models on Colab/Kaggle |
| **Research Agent** | Finds ideas from papers, YouTube |
| **Verifier** | Statistical soundness checks |
| **Deployment** | Pushes to MT5, TradingView, Alpaca |
| **Portfolio Manager** | Ensures diversification |

## 🔗 External Integrations

### Data Sources (Free)
- **Dukascopy**: Forex OHLC data (no API key)
- **Yahoo Finance**: Stocks & crypto (no API key)
- **Polygon.io**: Stocks (free tier available)

### Backtesting
- **Backtrader**: Local backtesting
- **VectorBT**: Vectorized backtesting
- **QuantConnect**: Institutional grade

### ML Training
- **Google Colab**: Free GPU/TPU
- **Kaggle**: Free GPU compute
- **Local Ollama**: Private LLM

### Trading Platforms
- **MetaTrader 5**: Forex/CFD trading
- **TradingView**: Alerts & webhooks
- **Alpaca**: Stock API trading

### LLM Providers
- **Ollama** (default): Local, free
- **OpenAI**: GPT-4 API
- **Anthropic**: Claude API

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│      React Dashboard (Port 3000)        │
│  - Command Center                       │
│  - Agent Monitor                        │
│  - Strategy Marketplace                 │
│  - Backtester UI                        │
└────────────────┬────────────────────────┘
                 │ WebSocket
┌────────────────▼────────────────────────┐
│      FastAPI Backend (Port 8000)        │
│  - Agent Orchestrator                   │
│  - Event Bus                            │
│  - REST API & WebSocket                 │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌─────────┐
│ Redis  │  │Postgres│  │Ollama   │
│ Cache  │  │Database│  │ LLM API │
└────────┘  └────────┘  └─────────┘

Agent Services:
┌─────────────┬──────────────┬──────────┬────────┐
│ Backtrader  │ Google Colab │ MT5 API  │ Dukask │
│ VectorBT    │ Kaggle API   │ TradingV │ Yahoo  │
│ QuantConnect│ Papermill    │ Alpaca   │ Polygon│
└─────────────┴──────────────┴──────────┴────────┘
```

## ⚙️ Configuration

Edit `.env` to configure:

```bash
# LLM (ollama, openai, anthropic)
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral

# Trading Platforms
MT5_SERVER=ICMarkets-Demo
MT5_LOGIN=your_login
MT5_PASSWORD=your_password

# Colab GPU Training
GOOGLE_COLAB_AUTH_TOKEN=your_token
COLAB_NOTEBOOK_ID=your_notebook_id

# System
MAX_AGENTS=10
BAC KTEST_LOOKBACK_YEARS=5
MIN_SHARPE_RATIO=1.0
MAX_DRAWDOWN_PCT=30
```

## 🧪 Testing

```bash
# Run tests
make test

# Run specific test
pytest backend/tests/test_agents.py -v

# View coverage
pytest --cov=backend
```

## 📈 Monitoring

```bash
# View logs
make logs

# Check agent status
curl http://localhost:8000/api/agents/status

# Get active tasks
curl http://localhost:8000/api/agents/tasks
```

## 🚨 Common Issues

### WebSocket Connection Failed
- Ensure backend is running: `docker-compose logs backend`
- Check CORS settings in `.env`

### Models not Training
- Verify Colab auth token
- Check Google Drive permissions
- Test Colab connection manually

### MT5 Connection Error
- Install MT5 on your system
- Update MT5_PATH in .env
- Ensure demo/live account is active

### Out of Memory
- Reduce backtest lookback years
- Use smaller training datasets
- Enable Colab GPU for ML training

## 📚 Resources

- [QuantConnect Academy](https://www.quantconnect.com/learning)
- [Backtrader Documentation](https://www.backtrader.com/docu/)
- [Trading Strategy Books](https://algorithmic-trading.com/)
- [Research Papers](https://arxiv.org/list/q-fin/recent)

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes
3. Test thoroughly
4. Submit PR

## 📝 License

MIT License - see LICENSE file

## 🆘 Support

For issues or questions:
1. Check GitHub issues
2. Review logs: `docker-compose logs -f`
3. Create new issue with details

---

**Next Steps**:
1. Configure `.env` with your credentials
2. Run `make up` to start all services
3. Access http://localhost:3000
4. Send your first command to the agents!
