from database.mysql_connector import MySQLConnector


class PurchaseOrderGenerator:

    def create_order(self, supplier_id, product_id, quantity, total_price):

        db = MySQLConnector()
        db.connect()

        query = """
        INSERT INTO purchase_orders
        (supplier_id, product_id, quantity, total_price, order_status)
        VALUES (%s,%s,%s,%s,%s)
        """

        db.execute_query(query, (
            supplier_id,
            product_id,
            quantity,
            total_price,
            "Pending Approval"
        ))

        db.close()

        print("Purchase Order Created")