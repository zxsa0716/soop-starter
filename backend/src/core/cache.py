"""Redis 7일 TTL 캐시 — 시연 안정성 3중 안전장치 중 #3."""
from __future__ import annotations
import json
import logging
from typing import Any

import redis.asyncio as aioredis

from .config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self, host: str = None, port: int = None):
        self.client = aioredis.Redis(
            host=host or settings.redis_host,
            port=port or settings.redis_port,
            decode_responses=True,
        )

    async def get(self, key: str) -> Any | None:
        raw = await self.client.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    async def set(self, key: str, value: Any, ttl: int = None) -> None:
        ttl = ttl if ttl is not None else settings.redis_ttl_seconds
        payload = json.dumps(value, ensure_ascii=False, default=str)
        await self.client.set(key, payload, ex=ttl)

    async def ping(self) -> bool:
        try:
            return await self.client.ping()
        except Exception as e:
            logger.warning(f"redis ping failed: {e}")
            return False
