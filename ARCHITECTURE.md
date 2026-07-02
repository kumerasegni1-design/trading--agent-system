# Trading Agent System - Architecture & Internals

## System Overview

This is a **multi-agent orchestration system** for algorithmic trading strategy development, backtesting, ML optimization, and live deployment.

### Core Components

#### 1. Command Center (React Frontend)
- Real-time chat interface to dispatch commands
- Agent status monitoring
- Strategy marketplace viewer
- Backtesting dashboard
- Live trading P&L tracker

#### 2. Agent Orchestrator (FastAPI Backend)
- Coordinates all agents via event bus
- Routes commands to appropriate agents
- Manages task queue and execution
- Logs all agent decisions

#### 3. Specialized Agents

**Strategy Generator Agent**
- Uses LLM to create novel trading strategies
- Generates Python code based on trading ideas
- Integrates research findings into strategies

**Data Downloader Agent**
- Fetches historical OHLC data
- Sources: Dukascopy, Yahoo Finance, Polygon.io
- Handles multiple timeframes
- No API keys required for free sources

**Backtesting Critic Agent**
- Analyzes backtest results for issues
- Detects overfitting using walk-forward analysis
- Checks for data leakage
- Verifies edge stability
- Uses multiple backtesting engines

**ML Trainer Agent**
- Trains ML models for entry/exit prediction
- Uploads data to Google Colab/Kaggle
- Executes training on free GPU/TPU
- Downloads trained models
- Performs hyperparameter optimization

**Research Agent**
- Searches ArXiv for trading papers
- Scrapes YouTube for trading strategies
- Monitors Twitter/Reddit for ideas
- Summarizes findings

**Verifier Agent**
- Statistical soundness checks
- Sharpe ratio validation
- Monte Carlo analysis
- Stress testing
- Drawdown analysis

**Deployment Agent**
- Converts strategy to MT5 EAs
- Creates TradingView alerts
- Integrates with Alpaca API
- Paper trades before live
- Monitors deployed strategies

**Portfolio Manager Agent**
- Checks strategy correlation
- Prevents duplicate strategies
- Ensures portfolio diversification
- Manages position sizing
- Tracks combined portfolio P&L

## Agent Communication

### Event Bus Architecture
```
Agent 1 → Event Bus → Agent 2
              ↓
          Event History
              ↓
          Dashboard/Logs
```

- All agents communicate via centralized event bus
- Decoupled architecture: agents don't call each other directly
- Full event history for audit trail
- Pub/sub pattern for scalability

## Data Flow

### Strategy Generation Flow
```
User Prompt
    ↓
Command Center WebSocket
    ↓
Agent Coordinator
    ↓
Strategy Generator Agent
    ├→ Generate Strategy Code
    ├→ Create Test Data
    └→ Emit Strategy:Generated Event
        ↓
    Data Downloader Agent
    ├→ Fetch Historical Data
    └→ Emit Data:Downloaded Event
        ↓
    Backtester Agent
    ├→ Run Backtest
    ├→ Walk-Forward Analysis
    ├→ Monte Carlo Simulation
    └→ Emit Backtest:Completed Event
        ↓
    Backtesting Critic Agent
    ├→ Check for Overfitting
    ├→ Detect Data Leakage
    ├→ Verify Edge Stability
    └→ Emit Analysis:Complete Event
        ↓
    Verifier Agent
    ├→ Statistical Tests
    ├→ Stress Testing
    └→ Emit Verification:Done Event
        ↓
    Portfolio Manager Agent
    ├→ Check Correlation
    ├→ Verify Diversification
    └→ Emit Portfolio:CheckComplete Event
        ↓
    [Decision: Pass or Fail?]
    ├→ If PASS: Deployment Agent → Live Trading
    └→ If FAIL: Send feedback to Strategy Generator
```

## Backtesting Strategy

### Three-Tier Backtesting

1. **Fast Check** (Backtrader)
   - Quick performance assessment
   - ~1-5 minutes for 5 years daily data
   - Basic metrics only

2. **Deep Analysis** (VectorBT)
   - Vectorized performance metrics
   - Walk-forward analysis
   - Monte Carlo simulation
   - ~10-30 minutes

3. **Institutional Grade** (QuantConnect)
   - Most accurate simulation
   - Slippage, commission, margin modeling
   - Cross-venue testing
   - ~1-2 hours

### Overfitting Detection

**Walk-Forward Analysis**
- Divide data into N periods
- In-sample optimization on first N-1 periods
- Out-of-sample test on last period
- Compare in-sample vs out-of-sample Sharpe ratio
- If decay > 30%, strategy is overfitted

**Monte Carlo Testing**
- Generate 1000+ trade sequence permutations
- Simulate different market scenarios
- Calculate probability of profit
- Stress test with extreme market moves

## ML Integration

### Training Pipeline

1. **Feature Engineering**
   - RSI, MACD, Bollinger Bands
   - ATR, CCI, Stochastic
   - Volume indicators
   - Price action patterns

2. **Label Creation**
   - Binary labels (up/down next N candles)
   - Directional threshold (e.g., > 1% move)
   - Multi-class labels (strong buy, buy, hold, sell, strong sell)

3. **Model Training**
   - Random Forest for feature importance
   - Gradient Boosting for accuracy
   - Ensemble methods
   - Hyperparameter optimization

4. **Validation**
   - Time-series cross-validation
   - Forward testing
   - Overfitting detection

## Deployment Flow

### Strategy → EA Conversion
```python
Strategy Code (Python)
    ↓
Code Translator
    ↓
MT5 Expert Advisor (MQL5)
    ↓
Compile & Deploy to MT5 Terminal
    ↓
Paper Trading (Demo Account)
    ↓
Monitor P&L & Drawdown
    ↓
[Decision: Go Live?]
    ├→ If YES: Deploy to Live Account
    └→ If NO: Optimize & Redeploy
```

## Free Resources Integration

### Data
- **Dukascopy**: Forex OHLC (no API key needed)
- **Yahoo Finance**: Stocks/crypto (free)
- **Polygon.io**: Free tier available

### Backtesting
- **Backtrader**: Local, free library
- **VectorBT**: Open source
- **QuantConnect**: Free tier available

### ML Training
- **Google Colab**: 12 hours free GPU/week
- **Kaggle**: 30 free GPU hours/week
- **Ollama**: Local LLM (completely free)

### Trading
- **MT5 Demo**: Paper trading (free)
- **Alpaca**: Commission-free API
- **TradingView**: Webhooks (free tier)

## Scalability

### Horizontal Scaling
- Multiple Agent instances
- Load balancer for API requests
- Kafka/RabbitMQ for message queuing
- Distributed backtesting

### Performance Optimizations
- Redis caching for data
- Vectorized operations (NumPy/VectorBT)
- Parallel backtesting
- Async/await for I/O operations

## Security

### API Keys Management
- Stored in encrypted `.env` file
- Never committed to git
- Rotated regularly

### Trading Safety
- Paper trading before live
- Position size limits
- Drawdown limits
- Manual approval for large trades

### Data Privacy
- Local data storage
- No cloud sync of sensitive data
- Audit logs for all operations

## Monitoring & Logging

### Agent Logs
- Task execution status
- Error tracking
- Performance metrics
- Event history

### System Metrics
- Agent CPU/memory usage
- Response times
- Task queue depth
- API latency

### Trading Metrics
- P&L tracking
- Win rate
- Drawdown
- Sharpe ratio
- Monthly/yearly returns

---

**For questions, refer to DEPLOYMENT.md for setup instructions.**
