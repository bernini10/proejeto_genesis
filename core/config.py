import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'ohlcv'
LOGS_DIR = BASE_DIR / 'logs'
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
FASTAPI_PORT = int(os.getenv('FASTAPI_PORT', '8000'))
TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '12h']
SYMBOL = 'BTC/USDT'
DEFAULT_THESIS = 'Compra quando velocidade de alta supera 0.8 com inercia >= 5 candles e saldo de pressao positivo.'
