import logging
import os
import asyncio
import json
import easyocr
import io
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from integrations.llm_providers import OllamaProvider
from telethon import TelegramClient, events
from PIL import Image

logger = logging.getLogger(__name__)

class TelegramSignalAgent(BaseAgent):
    """
    Agent responsible for monitoring Telegram channels,
    extracting trading signals from text and images,
    and initiating backtesting/verification.
    """

    def __init__(self, event_bus):
        super().__init__(event_bus, "TelegramSignalAgent")
        self.channels = []
        self.is_running = False
        self.client = None
        self.ocr_reader = None
        # Initialize LLM provider
        self.llm = OllamaProvider(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "mistral")
        )

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tasks such as starting monitoring,
        adding/removing channels, or processing a specific message.
        """
        task_type = task.get("type")
        task_id = task.get("task_id")

        logger.info(f"📥 TelegramSignalAgent executing task: {task_type}")

        if task_type == "start_monitoring":
            result = await self.start_monitoring(task)
        elif task_type == "add_channels":
            result = await self.add_channels(task)
        elif task_type == "process_message":
            result = await self.process_message(task)
        else:
            result = {"status": "error", "message": f"Unknown task type: {task_type}"}
            await self.log_task(task_id, "failed", result)
            return result

        await self.log_task(task_id, "completed", result)
        return result

    async def start_monitoring(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Start the Telegram client and monitor channels"""
        api_id = os.getenv("TELEGRAM_API_ID")
        api_hash = os.getenv("TELEGRAM_API_HASH")
        session_name = os.getenv("TELEGRAM_SESSION_NAME", "trading_agent_session")

        if not api_id or not api_hash:
            logger.error("❌ TELEGRAM_API_ID or TELEGRAM_API_HASH not set")
            return {"status": "error", "message": "Telegram credentials missing"}

        logger.info("🚀 Starting Telegram monitoring...")

        try:
            self.client = TelegramClient(session_name, api_id, api_hash)
            await self.client.start()

            @self.client.on(events.NewMessage(chats=self.channels))
            async def handler(event):
                await self.on_new_message(event)

            self.is_running = True
            # Run the client in the background
            asyncio.create_task(self.client.run_until_disconnected())

            return {"status": "started", "monitored_channels": len(self.channels)}
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram client: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def on_new_message(self, event):
        """Handle new incoming messages from monitored channels"""
        chat = await event.get_chat()
        chat_id = event.chat_id
        message_text = event.message.text
        has_media = event.message.media is not None

        logger.info(f"📩 New message from {chat_id}: {message_text[:50]}...")

        # Process the message
        task = {
            "type": "process_message",
            "chat_id": chat_id,
            "message_text": message_text,
            "has_media": has_media,
            "message_obj": event.message
        }
        await self.process_message(task)

    async def add_channels(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Add new channels to the monitor list"""
        new_channels = task.get("channels", [])
        self.channels.extend(new_channels)
        logger.info(f"✅ Added {len(new_channels)} channels to monitoring list")
        return {"status": "success", "total_channels": len(self.channels)}

    async def process_message(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Extract signal data from message text and media"""
        message_text = task.get("message_text", "")
        has_media = task.get("has_media", False)
        message_obj = task.get("message_obj")
        chat_id = task.get("chat_id")

        extracted_text = message_text

        if has_media and message_obj:
            media_text = await self.extract_text_from_media(message_obj)
            extracted_text += "\n" + media_text

        if not extracted_text.strip():
            return {"status": "ignored", "reason": "empty_message"}

        # Use LLM to parse the signal
        signal = await self.parse_signal_with_llm(extracted_text)

        if signal:
            signal["channel_id"] = chat_id
            signal["raw_text"] = extracted_text

            # Emit event for other agents (Backtester, etc.)
            await self.event_bus.emit("signal:new", signal)

            return {"status": "signal_extracted", "signal": signal}

        return {"status": "no_signal_found"}

    async def extract_text_from_media(self, message_obj) -> str:
        """Download media and use OCR to extract text"""
        if not self.ocr_reader:
            # Support major trading languages
            self.ocr_reader = easyocr.Reader(['en', 'ru', 'ar', 'zh_sim'])

        try:
            buffer = io.BytesIO()
            await message_obj.download_media(file=buffer)
            buffer.seek(0)

            # Perform OCR
            results = self.ocr_reader.readtext(buffer.read())
            text = " ".join([res[1] for res in results])
            logger.info(f"🖼️ OCR extracted text: {text[:50]}...")
            return text
        except Exception as e:
            logger.error(f"❌ OCR failed: {str(e)}")
            return ""

    async def parse_signal_with_llm(self, text: str) -> Optional[Dict[str, Any]]:
        """Use LLM to convert unstructured text into structured signal data"""
        prompt = f"""
        Return ONLY a JSON object. Extract trading signal information from the following text.
        If it's not a trading signal, return exactly: null

        JSON Fields:
        - symbol (e.g., EURUSD, BTCUSD)
        - action (BUY, SELL)
        - entry_price (float)
        - stop_loss (float)
        - take_profit (list of floats)
        - signal_type (MARKET, LIMIT, STOP)
        - trade_management (list of strings)

        Text:
        {text}
        """

        logger.info("🧠 Parsing signal with LLM...")

        try:
            response_text = await self.llm.generate_text(prompt)
            # Find JSON block if LLM returned extra text
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                signal = json.loads(json_str)
                logger.info(f"✅ Successfully parsed signal: {signal.get('symbol')}")
                return signal
            elif "null" in response_text.lower():
                return None
        except Exception as e:
            logger.error(f"❌ LLM parsing failed: {str(e)}")

        return None
