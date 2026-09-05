from pathlib import Path
from sqlite3 import Connection, connect


class DBWorker:
    """Small SQLite repository used by the API."""

    def __init__(self, database_path: str | Path = "db.db") -> None:
        self.connection: Connection = connect(str(database_path), check_same_thread=False)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                drugs_name TEXT NOT NULL,
                start_time INTEGER NOT NULL,
                repeat_time INTEGER NOT NULL,
                repeats INTEGER NOT NULL
            )
            """
        )
        self.connection.commit()

    def add_drug(
        self,
        user_id: int,
        name: str,
        start_time: int,
        repeats: int = 1,
        repeat_time: int = -1,
    ) -> int:
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO schedules (user_id, drugs_name, start_time, repeat_time, repeats)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, name, start_time, repeat_time, repeats),
            )
        return int(cursor.lastrowid)

    def get_drugs_by_uuid(self, user_id: int) -> list[tuple[str, int, int, int]]:
        cursor = self.connection.execute(
            """
            SELECT drugs_name, start_time, repeat_time, repeats
            FROM schedules
            WHERE user_id = ?
            ORDER BY id
            """,
            (user_id,),
        )
        return cursor.fetchall()

    def close(self) -> None:
        self.connection.close()

