import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


class APIException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class DatabaseHandler:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            raise APIException(f"Ошибка при подключении к базе данных: {e}")

    def disconnect(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        except Exception as e:
            raise APIException(f"Ошибка при отключении от базы данных: {e}")
