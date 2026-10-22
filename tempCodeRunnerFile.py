import sqlite3

class ScoreDB:
    def __init__(self, db_path="scores.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS high_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    level INTEGER NOT NULL
                )
            """)

    def top_scores(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name, score, level FROM high_scores ORDER BY score DESC LIMIT 9")
        return cur.fetchall()

    def add_score(self, name, score, level):
        with self.conn:
            self.conn.execute(
                "INSERT INTO high_scores (name, score, level) VALUES (?, ?, ?)",
                (name, score, level)
            )

    def delete_score_at(self, idx):
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM high_scores ORDER BY score DESC LIMIT 9")
        rows = cur.fetchall()
        if 0 <= idx < len(rows):
            target_id = rows[idx][0]
            with self.conn:
                self.conn.execute("DELETE FROM high_scores WHERE id = ?", (target_id,))

    def clear_scores(self):
        with self.conn:
            self.conn.execute("DELETE FROM high_scores")

    def close(self):
        self.conn.close()