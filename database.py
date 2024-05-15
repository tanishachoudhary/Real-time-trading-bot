import sqlite3
from datetime import datetime
import random
import string

class Database:
    def __init__(self, db_name='user_data.db'):
        self.db_name = db_name

    def get_connection_cursor(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        return conn, cursor

    def close_connection(self, conn):
        try:
            if conn:
                conn.close()
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

    def create_table_if_not_exists(self):
        conn, cursor = self.get_connection_cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                unique_id TEXT,
                registration_time DATETIME,
                user_type TEXT DEFAULT 'Free'
            )
        ''')

        conn.commit()
        self.close_connection(conn)

    def generate_unique_id(self):
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        return f"Syndicate_{random_chars}"

    def register_user(self, user_id):
        conn, cursor = self.get_connection_cursor()

        unique_id = self.generate_unique_id()
        registration_time = datetime.now()

        try:
            cursor.execute('''
                INSERT INTO users (user_id, unique_id, registration_time)
                VALUES (?, ?, ?)
            ''', (user_id, unique_id, registration_time))

            conn.commit()
            self.close_connection(conn)

            return user_id
        except Exception as e:
            conn.rollback()
            self.close_connection(conn)
            raise e

    def is_user_registered(self, user_id):
        conn, cursor = self.get_connection_cursor()

        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user_data = cursor.fetchone()

        self.close_connection(conn)

        return user_data is not None

    def get_user_info(self, user_id):
        conn, cursor = self.get_connection_cursor()

        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user_info = cursor.fetchone()

        self.close_connection(conn)

        if user_info:
            return {
                'user_id': user_info[0],
                'first_name': user_info[1],
                'last_name': user_info[2],
                'unique_id': user_info[3],
                'registration_time': datetime.strptime(user_info[4], '%Y-%m-%d %H:%M:%S.%f'),
                'user_type': user_info[5]
            }
        else:
            return None

    def set_user_type(self, unique_id, user_type):
        conn, cursor = self.get_connection_cursor()

        try:
            cursor.execute("UPDATE users SET user_type = ? WHERE unique_id = ?", (user_type, unique_id))
            conn.commit()

            return True
        except Exception as e:
            logger.error(f"Error updating user type: {e}")
            return False
        finally:
            self.close_connection(conn)

    def print_all_users(self):
        conn, cursor = self.get_connection_cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()

        for user in users:
            print(user)

        self.close_connection(conn)
