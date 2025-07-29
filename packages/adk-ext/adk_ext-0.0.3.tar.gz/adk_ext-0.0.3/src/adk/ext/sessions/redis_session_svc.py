import importlib.util
import json
import logging
import sys
import time
import uuid
from typing import Any, Dict, List, Optional, Union

from typing_extensions import override

from google.adk.events import Event
from google.adk.sessions import BaseSessionService, Session, State
from google.adk.sessions.base_session_service import (
    GetSessionConfig,
    ListSessionsResponse,
)

# Check if redis is available
redis_available = importlib.util.find_spec("redis") is not None
if redis_available:
    import redis

logger = logging.getLogger("adk_ext." + __name__)


class RedisSessionService(BaseSessionService):
    """A session service that uses Redis as the backend.

    This class can be used with Google Cloud Memorystore for Redis instances
    to provide a high-performance session storage solution.

    Note:
        This class requires the redis package to be installed.
        You can install it with: pip install 'adk-ext[redis]'
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        ssl: bool = False,
        session_ttl: Optional[int] = None,
        prefix: str = "adk_session:",
        event_prefix: str = "adk_events:",
        index_prefix: str = "adk_index:",
        **kwargs,
    ):
        if not redis_available:
            raise ImportError(
                "The redis package is required to use RedisSessionService. "
                "Please install it with: pip install 'adk-ext[redis]'"
            )
        """Initialize the RedisSessionService.

        Args:
            host: Redis server hostname. For Google Cloud Memorystore, this is the IP address.
            port: Redis server port. Default is 6379.
            db: Redis database index. Default is 0.
            password: Redis password. For Google Cloud Memorystore, use this if auth is enabled.
            ssl: Whether to use SSL for the connection. Default is False.
            session_ttl: Optional TTL (time-to-live) for sessions in seconds. Default is None (no expiration).
            prefix: Prefix for session keys. Default is "adk_session:".
            event_prefix: Prefix for event keys. Default is "adk_events:".
            index_prefix: Prefix for index keys. Default is "adk_index:".
            **kwargs: Additional arguments to pass to the Redis client.
        """
        self.redis = redis.Redis(
            host=host, port=port, db=db, password=password, ssl=ssl, **kwargs
        )
        self.session_ttl = session_ttl
        self.prefix = prefix
        self.event_prefix = event_prefix
        self.index_prefix = index_prefix

    def _get_session_key(self, app_name: str, user_id: str, session_id: str) -> str:
        """Get the Redis key for a session.

        Args:
            app_name: The name of the application.
            user_id: The ID of the user.
            session_id: The ID of the session.

        Returns:
            The Redis key for the session.
        """
        return f"{self.prefix}{app_name}:{user_id}:{session_id}"

    def _get_events_key(self, app_name: str, user_id: str, session_id: str) -> str:
        """Get the Redis key for events in a session.

        Args:
            app_name: The name of the application.
            user_id: The ID of the user.
            session_id: The ID of the session.

        Returns:
            The Redis key for events in the session.
        """
        return f"{self.event_prefix}{app_name}:{user_id}:{session_id}"

    def _get_user_sessions_index_key(self, app_name: str, user_id: str) -> str:
        """Get the Redis key for the index of sessions for a user.

        Args:
            app_name: The name of the application.
            user_id: The ID of the user.

        Returns:
            The Redis key for the index of sessions.
        """
        return f"{self.index_prefix}{app_name}:{user_id}"

    def _serialize_session(self, session: Session) -> Dict[str, Any]:
        """Serialize a Session object to a dictionary.

        Args:
            session: The Session object to serialize.

        Returns:
            A dictionary representation of the session.
        """
        # The session's events are stored separately, so we exclude them here
        session_data = {
            "session_id": session.id,
            "app_name": session.app_name,
            "user_id": session.user_id,
            "state": session.state,
            "created_at": (
                int(session.last_update_time * 1000)
                if session.last_update_time
                else int(time.time() * 1000)
            ),
            "updated_at": int(time.time() * 1000),
        }
        return session_data

    def _deserialize_session(
        self, session_data: Dict[str, Any], include_events: bool = True
    ) -> Optional[Session]:
        """Deserialize a dictionary to a Session object.

        Args:
            session_data: The dictionary to deserialize.
            include_events: Whether to include events in the session.

        Returns:
            The deserialized Session object, or None if deserialization fails.
        """
        if not session_data:
            return None

        session_id = session_data.get("session_id")
        app_name = session_data.get("app_name")
        user_id = session_data.get("user_id")
        state_data = session_data.get("state", {})
        created_at = session_data.get("created_at")
        updated_at = session_data.get("updated_at")
        last_update_time = (updated_at or created_at) / 1000.0  # Convert to seconds

        try:
            session = Session(
                id=session_id,
                app_name=app_name,
                user_id=user_id,
                state=state_data,
                events=[],
                last_update_time=float(last_update_time),
            )
        except Exception as e:
            logger.error(f"Error creating session from data: {e}")
            return None

        # Include events if requested
        if include_events:
            events_key = self._get_events_key(app_name, user_id, session_id)
            # Get events from Redis sorted set, ordered by timestamp
            events_data = self.redis.zrange(events_key, 0, -1)

            for event_json in events_data:
                try:
                    event_data = json.loads(event_json)
                    event = Event(**event_data)
                    session.events.append(event)
                except Exception as e:
                    logger.error(f"Error deserializing event: {e}")

        return session

    @override
    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        """Create a new session.

        Args:
            app_name: The name of the application.
            user_id: The ID of the user.
            state: Optional initial state data.
            session_id: Optional session ID. If not provided, a new ID will be generated.

        Returns:
            The created session.

        Raises:
            ValueError: If app_name or user_id is empty or None.
            ValueError: If a session with the same ID already exists.
        """
        # Validate inputs
        if not app_name or not user_id:
            error_msg = "App name and user ID must be provided to create a session."
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())

        # Create timestamp (milliseconds since epoch)
        timestamp = int(time.time() * 1000)

        # Create session data
        session_data = {
            "session_id": session_id,
            "app_name": app_name,
            "user_id": user_id,
            "state": state or {},
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Session key in Redis
        session_key = self._get_session_key(app_name, user_id, session_id)

        # Index key to track sessions for this user & app
        index_key = self._get_user_sessions_index_key(app_name, user_id)

        # Use Redis pipeline for atomic operations
        pipe = self.redis.pipeline()

        # Check if session already exists and set new session in a transaction
        pipe.exists(session_key)
        pipe.watch(session_key)

        try:
            # Get the result of the exists check
            exists_result = pipe.execute()[0]

            if exists_result:
                error_msg = f"Session already exists: {app_name}:{user_id}:{session_id}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Multi/exec block for atomicity
            pipe.multi()

            # Store session data as a JSON string
            pipe.set(session_key, json.dumps(session_data))

            # Add to the user's sessions index set
            pipe.sadd(index_key, session_id)

            # Set expiration if TTL is provided
            if self.session_ttl:
                pipe.expire(session_key, self.session_ttl)
                pipe.expire(index_key, self.session_ttl)

            # Execute all commands atomically
            pipe.execute()

        except redis.WatchError:
            # Someone else modified the key while we were watching
            error_msg = f"Concurrent modification detected for session: {app_name}:{user_id}:{session_id}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Create a Session object
        session = Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            state=state or {},
            events=[],
            last_update_time=float(timestamp / 1000),
        )

        logger.info(f"Created session: {app_name}:{user_id}:{session_id}")
        return session

    @override
    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        """Get a session.

        Args:
            app_name: The name of the application.
            user_id: The ID of the user.
            session_id: The ID of the session.
            config: Optional configuration for retrieving the session.

        Returns:
            The session if found, None otherwise.

        Raises:
            ValueError: If app_name, user_id, or session_id is empty or None.
        """
        # Validate inputs
        if (
            not app_name
            or not user_id
            or not session_id
            or app_name == ""
            or user_id == ""
            or session_id == ""
        ):
            error_msg = (
                "App name, user ID, and session ID must be provided to get a session."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Get session key
        session_key = self._get_session_key(app_name, user_id, session_id)

        try:
            # Get session data from Redis
            session_json = self.redis.get(session_key)
            if not session_json:
                logger.warning(f"Session not found: {app_name}:{user_id}:{session_id}")
                return None

            # Parse JSON data
            session_data = json.loads(session_json)

            # Default to always include events
            include_events = True
            if config and hasattr(config, "include_events"):
                include_events = config.include_events

            # Deserialize session
            session = self._deserialize_session(
                session_data, include_events=include_events
            )

            if session:
                # Update expiration time if TTL is set
                if self.session_ttl:
                    self.redis.expire(session_key, self.session_ttl)
                    # Also refresh the index expiration
                    index_key = self._get_user_sessions_index_key(app_name, user_id)
                    self.redis.expire(index_key, self.session_ttl)
                    # And refresh events expiration
                    events_key = self._get_events_key(app_name, user_id, session_id)
                    self.redis.expire(events_key, self.session_ttl)

                logger.debug(f"Retrieved session: {app_name}:{user_id}:{session_id}")
                return session
            else:
                logger.error(
                    f"Failed to deserialize session: {app_name}:{user_id}:{session_id}"
                )
                return None

        except Exception as e:
            logger.error(
                f"Error getting session {app_name}:{user_id}:{session_id}: {e}"
            )
            return None

    @override
    async def list_sessions(
        self, *, app_name: str, user_id: str
    ) -> ListSessionsResponse:
        """List all sessions for an app and user.

        Args:
            app_name: The name of the application.
            user_id: The ID of the user.

        Returns:
            ListSessionsResponse containing the sessions.

        Raises:
            ValueError: If app_name or user_id is empty or None.
        """
        # Validate inputs
        if not app_name or not user_id:
            logger.error("App name and user ID must be provided to list sessions.")
            raise ValueError("App name and user ID must be provided to list sessions.")

        try:
            # Get the index of sessions for this user & app
            index_key = self._get_user_sessions_index_key(app_name, user_id)
            session_ids = self.redis.smembers(index_key)

            sessions = []

            # Get each session by its ID
            for session_id in session_ids:
                session_id_str = (
                    session_id.decode("utf-8")
                    if isinstance(session_id, bytes)
                    else session_id
                )
                session_key = self._get_session_key(app_name, user_id, session_id_str)
                session_json = self.redis.get(session_key)

                if session_json:
                    try:
                        session_data = json.loads(session_json)
                        session = self._deserialize_session(
                            session_data, include_events=True
                        )
                        if session:
                            sessions.append(session)
                    except Exception as e:
                        logger.error(
                            f"Error deserializing session {session_id_str}: {e}"
                        )
                else:
                    # The session ID exists in the index but not in storage
                    # This indicates an inconsistency - remove from index
                    logger.warning(
                        f"Removing orphaned session ID from index: {session_id_str}"
                    )
                    self.redis.srem(index_key, session_id)

            logger.debug(f"Listed {len(sessions)} sessions for {app_name}:{user_id}")
            return ListSessionsResponse(sessions=sessions)

        except Exception as e:
            logger.error(f"Error listing sessions for {app_name}:{user_id}: {e}")
            return ListSessionsResponse(sessions=[])

    @override
    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        """Delete a session and its associated events.

        Args:
            app_name: The name of the application.
            user_id: The ID of the user.
            session_id: The ID of the session.

        Raises:
            ValueError: If app_name, user_id, or session_id is empty or None.
        """
        # Validate inputs
        if (
            not app_name
            or not user_id
            or not session_id
            or app_name == ""
            or user_id == ""
            or session_id == ""
        ):
            error_msg = "App name, user ID, and session ID must be provided to delete a session."
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Get keys
        session_key = self._get_session_key(app_name, user_id, session_id)
        events_key = self._get_events_key(app_name, user_id, session_id)
        index_key = self._get_user_sessions_index_key(app_name, user_id)

        try:
            # Check if session exists
            exists = self.redis.exists(session_key)
            if not exists:
                logger.warning(
                    f"Cannot delete nonexistent session: {app_name}:{user_id}:{session_id}"
                )
                return

            # Use pipeline for atomic operations
            pipe = self.redis.pipeline()

            # Delete session data
            pipe.delete(session_key)

            # Delete events
            pipe.delete(events_key)

            # Remove from index
            pipe.srem(index_key, session_id)

            # Execute all commands
            pipe.execute()

            logger.info(f"Deleted session: {app_name}:{user_id}:{session_id}")

        except Exception as e:
            logger.error(
                f"Error deleting session {app_name}:{user_id}:{session_id}: {e}"
            )
            raise

    @override
    async def append_event(self, session: Session, event: Event) -> Event:
        """Append an event to a session.

        Args:
            session: The session to append the event to.
            event: The event to append.

        Returns:
            The appended event.

        Raises:
            ValueError: If the session does not exist or inputs are invalid.
        """
        # Validate inputs
        if not session:
            raise ValueError("Session must be provided to append an event.")
        if not event:
            raise ValueError("Event must be provided to append to session.")

        # If event doesn't have an ID, generate one
        if not event.id:
            event.id = str(uuid.uuid4())

        # If timestamp is not set, set it to current time
        if not event.timestamp:
            event.timestamp = int(time.time() * 1000)  # milliseconds since epoch

        # Get keys
        session_key = self._get_session_key(
            session.app_name, session.user_id, session.id
        )
        events_key = self._get_events_key(session.app_name, session.user_id, session.id)

        try:
            # Check if session exists
            exists = self.redis.exists(session_key)
            if not exists:
                error_msg = f"Session does not exist: {session.app_name}:{session.user_id}:{session.id}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Serialize the event to JSON
            event_json = json.dumps(event.model_dump())

            # Use pipeline for atomic operations
            pipe = self.redis.pipeline()

            # Add event to sorted set with score as timestamp for automatic ordering
            pipe.zadd(events_key, {event_json: event.timestamp})

            # Update session's updated_at timestamp
            pipe.hset(session_key, "updated_at", event.timestamp)

            # Refresh expiration time if TTL is set
            if self.session_ttl:
                pipe.expire(session_key, self.session_ttl)
                pipe.expire(events_key, self.session_ttl)
                # Also refresh the index expiration
                index_key = self._get_user_sessions_index_key(
                    session.app_name, session.user_id
                )
                pipe.expire(index_key, self.session_ttl)

            # Execute all commands
            pipe.execute()

            # Update in-memory session object
            await super().append_event(session=session, event=event)

            logger.debug(f"Appended event {event.id} to session {session.id}")
            return event

        except Exception as e:
            if session:
                logger.error(f"Error appending event to session {session.id}: {e}")
            else:
                logger.error(f"Error appending event to session: {e}")
            raise
