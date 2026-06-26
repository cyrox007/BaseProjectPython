# core/redis.py
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
import redis.asyncio as redis
from redis.asyncio import Redis
from functools import wraps
import hashlib

from core.logger import setup_logger
from settings import config

logger = setup_logger(__name__)


class RedisClient:
    """Клиент для работы с Redis с поддержкой кэширования"""
    
    _instance: Optional['RedisClient'] = None
    _client: Optional[Redis] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self) -> None:
        """Подключение к Redis"""
        if self._client is None:
            try:
                self._client = redis.from_url(
                    config.REDIS_URL or "redis://localhost:6379/0",
                    decode_responses=True,
                    max_connections=200,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                )
                # Проверка соединения
                await self._client.ping()
                logger.info("Redis подключен успешно")
            except Exception as e:
                logger.error(f"Ошибка подключения к Redis: {e}")
                self._client = None
    
    async def close(self) -> None:
        """Закрытие соединения"""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Redis соединение закрыто")
    
    @property
    def client(self) -> Optional[Redis]:
        return self._client
    
    async def get(self, key: str) -> Optional[str]:
        """Получение значения по ключу"""
        if not self._client:
            await self.connect()
        try:
            return await self._client.get(key)
        except Exception as e:
            logger.error(f"Ошибка при получении из Redis: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Установка значения с TTL"""
        if not self._client:
            await self.connect()
        try:
            if isinstance(value, bytes):
                pass  # Оставляем как есть
            elif isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif not isinstance(value, str):
                value = str(value)
            
            if ttl:
                if isinstance(ttl, timedelta):
                    ttl = int(ttl.total_seconds())
                return await self._client.set(key, value, ex=ttl)
            return await self._client.set(key, value)
        except Exception as e:
            logger.error(f"Ошибка при установке в Redis: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Удаление ключа"""
        if not self._client:
            await self.connect()
        try:
            return bool(await self._client.delete(key))
        except Exception as e:
            logger.error(f"Ошибка при удалении из Redis: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Удаление ключей по шаблону"""
        if not self._client:
            await self.connect()
        try:
            keys = await self._client.keys(pattern)
            if keys:
                return await self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Ошибка при удалении по шаблону: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        if not self._client:
            await self.connect()
        try:
            return bool(await self._client.exists(key))
        except Exception as e:
            logger.error(f"Ошибка при проверке ключа: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Инкремент значения"""
        if not self._client:
            await self.connect()
        try:
            return await self._client.incr(key, amount)
        except Exception as e:
            logger.error(f"Ошибка при инкременте: {e}")
            return None
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Установка TTL для ключа"""
        if not self._client:
            await self.connect()
        try:
            return await self._client.expire(key, ttl)
        except Exception as e:
            logger.error(f"Ошибка при установке TTL: {e}")
            return False


# Глобальный экземпляр
redis_client = RedisClient()


# Декоратор для кэширования
def cache(
    key_prefix: str = "",
    ttl: int = 300,  # 5 минут
    key_from_args: bool = True,
    key_args: list = None
):
    """
    Декоратор для кэширования результатов функций.
    
    Args:
        key_prefix: Префикс ключа
        ttl: Время жизни кэша в секундах
        key_from_args: Использовать аргументы для формирования ключа
        key_args: Список имён аргументов для формирования ключа
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Формирование ключа
            if key_from_args:
                # Используем аргументы для ключа
                key_parts = [key_prefix]
                
                if key_args:
                    for arg_name in key_args:
                        if arg_name in kwargs:
                            value = kwargs[arg_name]
                            key_parts.append(f"{arg_name}:{value}")
                else:
                    # Используем все аргументы
                    for arg in args:
                        if arg is not None:
                            key_parts.append(str(arg))
                    for k, v in kwargs.items():
                        if v is not None:
                            key_parts.append(f"{k}:{v}")
                
                cache_key = ":".join(key_parts)
            else:
                cache_key = key_prefix
            
            # Хэшируем ключ для безопасности
            if len(cache_key) > 100:
                cache_key = f"{key_prefix}:{hashlib.md5(cache_key.encode()).hexdigest()[:16]}"
            
            # Пробуем получить из кэша
            if redis_client.client:
                cached_value = await redis_client.get(cache_key)
                if cached_value is not None:
                    try:
                        return json.loads(cached_value)
                    except (json.JSONDecodeError, TypeError):
                        return cached_value
            
            # Если нет в кэше — выполняем функцию
            result = await func(*args, **kwargs)
            
            # Сохраняем в кэш
            if result is not None and redis_client.client:
                try:
                    value_to_cache = json.dumps(result, default=str)
                    await redis_client.set(cache_key, value_to_cache, ttl=ttl)
                except Exception as e:
                    logger.warning(f"Не удалось сохранить в кэш: {e}")
            
            return result
        
        return wrapper
    return decorator


# Функция для инвалидации кэша
async def invalidate_cache(pattern: str = "*") -> int:
    """Инвалидация кэша по шаблону"""
    return await redis_client.delete_pattern(pattern)