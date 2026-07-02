# 🤖 Trading Agent System - Multi-Agent Trading Strategy Generator

A browser-based multi-agent orchestration system that autonomously generates, backtests, trains ML models on trading strategies, and deploys them to live markets with industry-grade accuracy verification.

## 🎯 System Architecture

### Agent Roles

1. **Strategy Generator Agent** - Creates novel trading strategies
2. **Data Downloader Agent** - Fetches historical data (Dukascopy, Yahoo Finance, etc.)
3. **Backtesting Critic Agent** - Detects overfitting, data leakage, edge decay
4. **ML Training Agent** - Trains models via Colab/Kaggle GPUs
5. **Research Agent** - Finds trading ideas from papers, YouTube, social media
6. **Strategy Verifier Agent** - Statistical soundness, walk-forward analysis
7. **Deployment Agent** - Pushes to TradingView, MT5, live markets
8. **Portfolio Manager Agent** - Ensures diversity, prevents duplicate strategies
9. **Command Center** - Routes prompts to agents, aggregates results

## 🏗️ Key Components

### Backend
- **FastAPI** - Agent orchestration & API endpoints
- **Agent Coordinator** - Routes tasks, manages agent state
- **Backtesting Engine** - QuantConnect/Backtrader integration
- **ML Pipeline** - Scikit-learn, XGBoost, TensorFlow

### Frontend
- **Dashboard** - Command center for prompt dispatch
- **Live Monitor** - Strategy performance tracking
- **Marketplace** - Deployed models list & status

### External Integrations
- **Data Sources**: Dukascopy, Yahoo Finance, Polygon.io
- **Backtesting**: QuantConnect, Backtrader, VectorBT
- **ML Training**: Google Colab, Kaggle (free GPUs)
- **Trading Platforms**: TradingView, MT5, Alpaca
- **LLM Providers**: Ollama (local), OpenAI, Anthropic

## 📋 Requirements

- Python 3.10+
- Docker & Docker Compose
- Node.js 18+ (for frontend)
- Git
- Free API keys (Dukascopy, Polygon.io optional)
- TradingView/MT5 API credentials

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/kumerasegni1-design/trading--agent-system.git
cd trading--agent-system
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` with your credentials:
```
LLM_PROVIDER=ollama  # or openai, anthropic
COLAB_NOTEBOOK_ID=your_colab_id
MT5_ACCOUNT=your_account
TRADINGVIEW_API_KEY=your_key
```

### 3. Start System
```bash
docker-compose up -d
```

### 4. Access Dashboard
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Agent Logs: http://localhost:8000/agents/logs

## 💬 Example Prompt

```
"Generate a mean reversion strategy on EUR/USD using the last 5 years of data. 
Backtest it thoroughly for overfitting, verify statistical significance, 
train an ML model to optimize entry/exit, and if it passes all checks, 
deploy to MT5 demo account."
```

**System workflow:**
1. Strategy Generator → Creates 3-5 strategy variations
2. Data Downloader → Fetches EUR/USD daily & hourly data
3. Backtesting Critic → Stress tests, detects issues
4. ML Trainer → Trains model on Colab GPU
5. Verifier → Walk-forward analysis, Sharpe ratio check
6. Deployment → Pushes to MT5 if criteria met

## 🔄 Agent Communication

Agents communicate via:
- **JSON events** (standard)
- **gRPC** (for latency-critical tasks)
- **Shared state** (Redis cache)

## 📊 Backtesting Standards

Uses industry-grade libraries:
- **QuantConnect** - Institutional backtesting
- **Backtrader** - Custom indicators & strategies
- **VectorBT** - Vectorized performance analysis

Verification checklist:
- ✅ Overfitting detection (walk-forward analysis)
- ✅ Data leakage check
- ✅ Edge decay analysis
- ✅ Sharpe ratio > 1.0
- ✅ Max drawdown < 30%
- ✅ Out-of-sample performance > 70% of in-sample

## 🛠️ Integration Sources

GitHub projects integrated/referenced:
- [QuantConnect Lean](https://github.com/QuantConnect/Lean) - Backtesting
- [Backtrader](https://github.com/mementum/backtrader) - Strategy framework
- [AutoGluon](https://github.com/autogluon/autogluon) - AutoML
- [AgenticOS](https://github.com/operand/agenticOS) - Agent framework
- [Hermes](https://github.com/reconsumeralization/Hermes) - Agent orchestration

## 💰 Free Resources Used

- **Dukascopy** - Historical forex data (free, no API key)
- **Google Colab** - GPU/TPU training (free tier)
- **Kaggle** - Datasets & GPU compute (free)
- **Ollama** - Local LLM inference (free)
- **Yahoo Finance** - Market data (free)

## 🚨 Critical Safety Features

1. **Backtesting Critic** - Prevents overfitted strategies from deployment
2. **Risk Limits** - Max position size, drawdown limits
3. **Paper Trading** - Demo accounts before live
4. **Diversification** - Portfolio correlation checks
5. **Audit Trail** - All agent decisions logged

## 📁 Project Structure

```
trading--agent-system/
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── setup.sh
├── README.md
│
├── backend/
│   ├── app.py                    # FastAPI main
│   ├── config.py                 # Configuration
│   ├── requirements.txt
│   │
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── coordinator.py        # Main orchestrator
│   │   └── event_bus.py          # Agent communication
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py         # Base agent class
│   │   ├── strategy_generator.py
│   │   ├── data_downloader.py
│   │   ├── backtesting_critic.py
│   │   ├── ml_trainer.py
│   │   ├── research_agent.py
│   │   ├── verifier_agent.py
│   │   ├── deployment_agent.py
│   │   └── portfolio_manager.py
│   │
│   ├── services/
│   │   ├── backtesting_service.py
│   │   ├── ml_service.py
│   │   ├── data_service.py
│   │   └── trading_platforms.py
│   │
│   └── integrations/
│       ├── colab_connector.py
│       ├── dukascopy_fetcher.py
│       ├── tradingview_api.py
│       ├── mt5_connector.py
│       └── llm_providers.py
│
├── frontend/
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── CommandCenter.jsx
│       │   ├── AgentMonitor.jsx
│       │   ├── StrategyMarketplace.jsx
│       │   └── Backtester.jsx
│       └── services/
│           └── api.js
│
├── notebooks/
│   ├── strategy_development.ipynb
│   └── model_training.ipynb
│
└── tests/
    ├── test_agents.py
    └── test_backtesting.py
```

## 🔐 Environment Variables

See `.env.example` for full list. Key variables:
```
# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=optional

# Trading Platforms
MT5_SERVER=your_broker
MT5_LOGIN=your_login
MT5_PASSWORD=your_password

# Data Sources
POLYGON_API_KEY=optional

# Colab/Kaggle
COLAB_NOTEBOOK_ID=your_notebook_id
KAGGLE_USERNAME=your_username
KAGGLE_API_KEY=your_api_key

# System
MAX_AGENTS=10
AGENT_TIMEOUT=3600
REDIS_URL=redis://localhost:6379
```

## 📈 Workflow Examples

### Example 1: Generate & Deploy Strategy
```
User Prompt → Coordinator → Strategy Generator
                ↓ (strategies created)
                ├→ Data Downloader
                ├→ Backtesting Critic
                ├→ Verifier
                └→ Deployment Agent (if passed)
                    ↓
                    MT5 / TradingView
```

### Example 2: Research-Based Strategy
```
User Prompt → Research Agent
↓ (finds papers/ideas)
Strategy Generator → backtest → deploy
```

## 🎓 Learning Resources

- [QuantConnect Academy](https://www.quantconnect.com/learning)
- [Backtrader Docs](https://www.backtrader.com/docu/)
- [Trading Strategy Design](https://papers.ssrn.com)

## 🤝 Contributing

1. Create feature branch
2. Add tests
3. Submit PR with agent improvements

## 📝 License

MIT

## 🆘 Support & Debugging

- Check `/logs` directory for agent execution logs
- Access `http://localhost:8000/agents/status` for agent health
- View Colab execution logs in dashboard

---

**Status**: 🚧 Under Development
**Last Updated**: 2026-07-02
