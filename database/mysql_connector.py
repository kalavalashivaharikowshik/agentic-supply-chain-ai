import mysql.connector
from mysql.connector import Error


class MySQLConnector:

    def __init__(self):
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="kowshik@123",
                database="agentic_supply_chain"
            )

            if self.connection.is_connected():
                print("Connected to MySQL Database")

        except Error as e:
            print("Error while connecting to MySQL:", e)

    def get_connection(self):
        return self.connection

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params if params else ())
        self.connection.commit()
        cursor.close()

    def fetch_all(self, query):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def fetch_one(self, query):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")