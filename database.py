import aiosqlite
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path

    async def _execute(self, query: str, parameters: tuple = ()) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, parameters)
            await db.commit()

    async def create_tables(self) -> None:
        await self._execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        await self._execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            role TEXT,  -- 'user' yoki 'assistant'
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        await self._execute("""
        CREATE TABLE IF NOT EXISTS smartphones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            brand TEXT NOT NULL,
            price TEXT NOT NULL,
            storage TEXT,
            ram TEXT,
            camera TEXT,
            battery TEXT,
            status TEXT DEFAULT 'available'
        );
        """)

    async def create_user(self, telegram_id: int, full_name: str, username: Optional[str]) -> None:
        query = "INSERT OR IGNORE INTO users (telegram_id, full_name, username) VALUES (?, ?, ?)"
        await self._execute(query, (telegram_id, full_name, username))

    async def save_message(self, telegram_id: int, role: str, content: str) -> None:
        query = "INSERT INTO messages (telegram_id, role, content) VALUES (?, ?, ?)"
        await self._execute(query, (telegram_id, role, content))

    async def get_chat_history(self, telegram_id: int, limit: int = 10) -> List[Dict[str, str]]:
        query = """
            SELECT role, content FROM (
                SELECT role, content, id FROM messages 
                WHERE telegram_id = ? 
                ORDER BY id DESC LIMIT ?
            ) ORDER BY id ASC
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, (telegram_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [{"role": row["role"], "content": row["content"]} for row in rows]
    
    async def search_smartphones(self, query: str) -> List[Dict[str, Any]]:
        sql_query = """
            SELECT model, brand, price, storage, ram, camera, battery, status 
            FROM smartphones 
            WHERE model LIKE ? OR brand LIKE ?
        """
        search_param = f"%{query}%"
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(sql_query, (search_param, search_param)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]