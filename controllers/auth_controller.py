from controllers.database import Database

class AuthController:
    def __init__(self):
        self.db = Database()

    def login(self, username, password):
        conn = self.db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        return user is not None