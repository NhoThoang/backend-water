#!/bin/bash
set -e

echo "⏳ Waiting for PostgreSQL to be ready..."

python - <<'END'
import os
import time
import asyncio
import asyncpg

host = os.environ['POSTGRES_HOST']
user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
db = os.environ['POSTGRES_DB']

dsn = f"postgresql://{user}:{password}@{host}/{db}"

async def wait_for_db():
    for i in range(10):
        try:
            conn = await asyncpg.connect(dsn)
            await conn.close()
            print("✅ PostgreSQL is ready!")
            return
        except Exception as e:
            print(f"⏳ Waiting for PostgreSQL ({i+1}/10): {e}")
            await asyncio.sleep(3)
    raise RuntimeError("❌ PostgreSQL not ready after retries")

asyncio.run(wait_for_db())
END
echo "🚀 Starting Gunicorn..."
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8001}
WORKERS=${WORKERS:-1}
WORKER_CLASS=${WORKER_CLASS:-uvicorn.workers.UvicornWorker}
TIMEOUT=${TIMEOUT:-120}
KEEP_ALIVE=${KEEP_ALIVE:-120}
ACCESS_LOGFILE=${ACCESS_LOGFILE:--}
ERROR_LOGFILE=${ERROR_LOGFILE:--}
LOG_LEVEL=${LOG_LEVEL:-info}
exec gunicorn main:app \
    --worker-class ${WORKER_CLASS} \
    --workers ${WORKERS} \
    --bind ${HOST}:${PORT} \
    --timeout ${TIMEOUT} \
    --keep-alive ${KEEP_ALIVE} \
    --access-logfile ${ACCESS_LOGFILE} \
    --error-logfile ${ERROR_LOGFILE} \
    --log-level ${LOG_LEVEL}
