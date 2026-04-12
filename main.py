from fastapi import FastAPI, Request
import logging, json
from datetime import datetime
import uvicorn
from core.config import FASTAPI_PORT

app = FastAPI(title='Projeto Genesis - Velocimetro de Fluxo')
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
log = logging.getLogger('genesis')

@app.post('/webhook/pine')
async def receive_pine_alert(request: Request):
    payload = await request.json()
    log.info(f'📡 Pine Sensor: {json.dumps(payload)}')
    return {'status': 'received', 'ts': datetime.utcnow().isoformat(), 'payload': payload}

@app.get('/health')
async def health():
    return {'status': 'ok', 'service': 'genesis-webhook'}

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=FASTAPI_PORT, reload=False)
