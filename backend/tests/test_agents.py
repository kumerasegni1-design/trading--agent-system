import pytest
from orchestrator.coordinator import EventBus
from agents.telegram_agent import TelegramSignalAgent
from agents.channel_ranker import ChannelRankerAgent

@pytest.mark.asyncio
async def test_telegram_agent_init():
    bus = EventBus()
    agent = TelegramSignalAgent(bus)
    assert agent.agent_name == "TelegramSignalAgent"
    assert not agent.is_running

@pytest.mark.asyncio
async def test_channel_ranker_logic():
    bus = EventBus()
    agent = ChannelRankerAgent(bus)

    task = {
        "type": "update_stats",
        "channel_id": "chan1",
        "backtest_result": {"net_profit": 100},
        "provider_claim": {"profit": True}
    }
    await agent.execute(task)

    ranking = await agent.rank_channels()
    assert len(ranking) == 1
    assert ranking[0]["channel_id"] == "chan1"
    assert ranking[0]["authenticity"] == 1.0
