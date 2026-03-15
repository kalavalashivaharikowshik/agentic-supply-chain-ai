from database.mysql_connector import MySQLConnector


class SupplierAPI:

    def get_all_suppliers(self):

        db = MySQLConnector()
        db.connect()

        query = "SELECT * FROM suppliers"
        suppliers = db.fetch_all(query)

        db.close()

        return suppliers