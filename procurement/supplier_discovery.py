from database.mysql_connector import MySQLConnector


class SupplierDiscovery:

    def get_suppliers(self):

        db = MySQLConnector()
        db.connect()

        query = "SELECT * FROM suppliers"
        suppliers = db.fetch_all(query)

        db.close()

        return suppliers