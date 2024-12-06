import sqlite3
from typing import Optional, Dict, List
from utils.logger import logger
from utils.constants import ANALYTICS_DB_PATH


class AnalyticsManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.db_path = ANALYTICS_DB_PATH
            self._initialize_db()
            self._initialized = True
            self._connection_cache: Dict[int, float] = {}
            self._conn = None
            logger.info("Analytics Manager initialized")

    def _initialize_db(self) -> None:
        """Initialize the analytics database"""
        try:
            with open("sql/create_table_analytics.sql", "r") as f:
                create_table_sql = f.read()

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(create_table_sql)
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize analytics database: {e}")
            raise

    @property
    def conn(self) -> sqlite3.Connection:
        """Get a database connection with connection pooling"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
        return self._conn

    def record_command(
        self,
        app: str,
        full_command: str,
        discord_user_id: int,
        discord_server_id: int,
        server_name: str,
        execution_time: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """Record a command interaction in the analytics table"""
        try:
            # Convert execution_time to integer milliseconds if it exists
            execution_time_ms = (
                int(execution_time * 1000) if execution_time is not None else None
            )

            # Convert boolean to integer for SQLite
            success_int = 1 if success else 0

            query = """
                INSERT INTO ANALYTICS (
                    app, full_command, discord_user_id, discord_server_id, server_name,
                    execution_time_ms, success, error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """

            data = (
                str(app),  # Ensure app is string
                str(full_command),  # Ensure command is string
                int(discord_user_id),  # Ensure user_id is integer
                int(discord_server_id),  # Ensure server_id is integer
                str(server_name),  # Ensure server_name is string
                execution_time_ms,  # Integer or None
                success_int,  # Integer (0 or 1)
                (
                    str(error_message) if error_message is not None else None
                ),  # String or None
            )

            with self.conn as conn:
                conn.execute(query, data)
            logger.info(f"Recorded analytics for command: {full_command}")
        except Exception as e:
            logger.error(f"Failed to record analytics: {e}")
            logger.error(
                f"Failed data: app: {app}, full_command: {full_command}, discord_user_id: {discord_user_id}, discord_server_id: {discord_server_id}, server_name: {server_name}, execution_time: {execution_time}, success: {success}, error_message: {error_message}"
            )

    def get_command_stats(
        self, days: int = 7, server_id: Optional[int] = None
    ) -> List[Dict]:
        """Get command usage statistics for the specified number of days"""
        try:
            base_query = """
                SELECT 
                    app,
                    full_command,
                    COUNT(*) as total_uses,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_uses,
                    COUNT(DISTINCT discord_user_id) as unique_users,
                    AVG(execution_time_ms) as avg_execution_time,
                    COUNT(DISTINCT discord_server_id) as server_count
                FROM ANALYTICS 
                WHERE timestamp >= datetime('now', ?, 'localtime')
                {server_filter}
                GROUP BY app, full_command
                ORDER BY total_uses DESC;
            """

            params = [f"-{days} days"]
            server_filter = ""

            if server_id:
                server_filter = "AND server_id = ?"
                params.append(server_id)

            query = base_query.format(server_filter=server_filter)

            with self.conn as conn:
                rows = conn.execute(query, params)

                return [
                    {
                        "app": row[0],
                        "full_command": row[1],
                        "total_uses": row[2],
                        "successful_uses": row[3],
                        "unique_users": row[4],
                        "avg_execution_time": row[5],
                        "server_count": row[6],
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Failed to get command stats: {e}")
            return []

    def get_user_stats(self, user_id: int, days: int = 7) -> List[Dict]:
        """Get command usage statistics for a specific user"""
        try:
            query = """
                SELECT 
                    app,
                    full_command,
                    COUNT(*) as total_uses,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_uses,
                    AVG(execution_time_ms) as avg_execution_time,
                    COUNT(DISTINCT discord_server_id) as server_count
                FROM ANALYTICS 
                WHERE user_id = ?
                AND timestamp >= datetime('now', ?, 'localtime')
                GROUP BY app, full_command
                ORDER BY total_uses DESC;
            """

            with self.conn as conn:
                rows = conn.execute(query, (user_id, f"-{days} days"))

                return [
                    {
                        "app": row[0],
                        "full_command": row[1],
                        "total_uses": row[2],
                        "successful_uses": row[3],
                        "avg_execution_time": row[4],
                        "server_count": row[5],
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return []

    def get_server_stats(self, server_id: int, days: int = 7) -> Dict:
        """Get usage statistics for a specific server"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_commands,
                    COUNT(DISTINCT discord_user_id) as unique_users,
                    COUNT(DISTINCT app) as unique_commands,
                    AVG(execution_time_ms) as avg_execution_time,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_commands
                FROM ANALYTICS 
                WHERE server_id = ?
                AND timestamp >= datetime('now', ?, 'localtime');
            """

            with self.conn as conn:
                row = conn.execute(query, (server_id, f"-{days} days")).fetchone()

                return {
                    "total_commands": row[0],
                    "unique_users": row[1],
                    "unique_commands": row[2],
                    "avg_execution_time": row[3],
                    "successful_commands": row[4],
                }
        except Exception as e:
            logger.error(f"Failed to get server stats: {e}")
            return {}
