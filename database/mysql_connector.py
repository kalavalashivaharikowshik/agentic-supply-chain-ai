import mysql.connector
import os


class MySQLConnector:

    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.environ.get("MYSQLHOST"),
                user=os.environ.get("MYSQLUSER"),
                password=os.environ.get("MYSQLPASSWORD"),
                database=os.environ.get("MYSQLDATABASE"),
                port=int(os.environ.get("MYSQLPORT")),
                ssl_verify_cert=False
            )
        except Exception as e:
            print("Database connection failed:", e)
            self.connection = None


    def fetch_all(self, query):

        if self.connection is None:
            return []

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()

        return result
