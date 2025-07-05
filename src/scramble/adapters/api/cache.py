from functools import lru_cache

from scramble.app.session_persistence import SessionPersistence
from scramble.app import AppSession

@lru_cache(maxsize=8) # You can adjust maxsize as needed
def get_session(session_name: str) -> AppSession:
    """
    Fetches session data using functools.lru_cache.
    This decorator automatically handles caching, cache hits/misses,
    and a Least Recently Used (LRU) eviction policy.

    Parameters
    ----------
    session_name : str
        Name of the session to retrieve.
    """
    return SessionPersistence.load(session_name)
