import importlib.util

# Import session service classes conditionally based on available dependencies
__all__ = []

# Try to import FirestoreSessionService if google.cloud.firestore is available
if importlib.util.find_spec("google.cloud.firestore") is not None:
    from .firestore_session_svc import FirestoreSessionService

    __all__.append("FirestoreSessionService")

# Try to import RedisSessionService if redis is available
if importlib.util.find_spec("redis") is not None:
    from .redis_session_svc import RedisSessionService

    __all__.append("RedisSessionService")
