from threading import Lock
import logging

logger = logging.getLogger(__name__)


class MemoryCache:
    """
    A thread-safe Singleton in-memory cache.
    """

    _instance = None
    _lock = Lock()
    _limit = 1000  # Optional limit for cache size

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-checked locking
                    cls._instance = super(MemoryCache, cls).__new__(cls)
                    cls._instance._cache = {}
        return cls._instance

    def get(self, key):
        with self._lock:
            """
            Retrieve a value from the cache by key.
            """
            return self._cache.get(key)

    def set(self, key, value):
        """
        Store a value in the cache with the specified key.
        """
        with self._lock:
            if len(self._cache) >= self._limit:
                logger.warning(
                    "Cache limit reached. Consider increasing the limit or clearing the cache."
                )
            self._cache[key] = value

    def delete(self, key):
        """
        Delete a value from the cache by key.
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self):
        """
        Clear the entire cache.
        """
        with self._lock:
            self._cache.clear()
