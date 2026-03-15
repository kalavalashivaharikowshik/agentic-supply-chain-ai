from database.mysql_connector import MySQLConnector


def test_connection():
    db = MySQLConnector()
    db.connect()

    suppliers = db.fetch_all("SELECT * FROM suppliers")

    print("Suppliers Table Data:")
    print(suppliers)

    db.close()


if __name__ == "__main__":
    test_connection()