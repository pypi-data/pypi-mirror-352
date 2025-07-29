"""
Session manager singleton for managing Session instances.
"""

import logging
import os
import shutil
import threading
from typing import Dict

from langframe._constants import INDEX_DIR, VECTOR_INDEX_DIR
from langframe.api.session.config import SessionConfig
from langframe._backends.local.session_state import LocalSessionState
from langframe.api.session.session import Session

logger = logging.getLogger(__name__)


class LocalSessionManager:
    """
    Singleton class responsible for managing Session instances.
    Ensures only one Session exists per app name.
    """

    _instance = None
    _sessions_lock = threading.Lock()

    # Maps app name to Session
    _live_sessions: Dict[str, Session]

    def __new__(cls):
        """Ensure singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(LocalSessionManager, cls).__new__(cls)
            cls._instance._live_sessions = {}
        return cls._instance

    def check_session_active(self, app_name: str) -> bool:
        """
        Check if a Session exists for the given app name.
        """
        with self._sessions_lock:
            return app_name in self._live_sessions

    def remove_session(self, app_name: str) -> None:
        """
        Remove a session by app name from the SessionManager.

        Args:
            app_name: The name of the application to remove
        """
        with self._sessions_lock:
            if app_name not in self._live_sessions:
                return
            session_state: LocalSessionState = self._live_sessions[
                app_name
            ]._session_state

            session_state.intermediate_df_client.cleanup()
            session_state.duckdb_conn.close()

            try:
                session_state.language_model.client.shutdown()
            except Exception as e:
                logger.warning(
                    f"Failed graceful shutdown of language model client: {e}"
                )

            if session_state.embedding_model:
                try:
                    session_state.embedding_model.client.shutdown()
                except Exception as e:
                    logger.warning(
                        f"Failed graceful shutdown of embedding model client: {e}"
                    )

            # Remove LanceDB index directory
            if os.path.exists(VECTOR_INDEX_DIR):
                try:
                    shutil.rmtree(VECTOR_INDEX_DIR)
                    shutil.rmtree(INDEX_DIR)
                except Exception as e:
                    logger.warning(
                        f"Failed to cleanup intermediate semantic search data: {e}"
                    )

            del self._live_sessions[app_name]

    def get_or_create_session(
        self,
        config: SessionConfig,
    ) -> Session:
        """
        Get an existing Session or create a new one with appropriate clients.

        Args:
            app_name: The name of the application
            db_path: Path to the database
            semantic_config: Semantic configuration options

        Returns:
            A Session instance

        Raises:
            RuntimeError: If client or session creation fails
        """
        with self._sessions_lock:
            app_name = config.app_name
            if app_name in self._live_sessions:
                logger.info(
                    "Session already exists for this app name. Returning existing session."
                )
                return self._live_sessions[app_name]

            # Create and store the session
            session = Session._create_local_session(config)
            self._live_sessions[app_name] = session
            return session

    def get_existing_session(self, app_name: str) -> Session:
        """
        Get a Session instance by app name.
        """
        with self._sessions_lock:
            if app_name not in self._live_sessions:
                raise ValueError(f"No session found for app name: {app_name}")
            return self._live_sessions[app_name]
