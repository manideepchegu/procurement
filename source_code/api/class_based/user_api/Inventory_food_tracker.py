from datetime import datetime

from flask import jsonify
from flask.views import MethodView

from source_code import app
from source_code.api.settings import connection
import psycopg2


class InventoryDetailsAPI(MethodView):
    def __init__(self):
        self.cur, self.conn = connection()

    def get(self, inventory_details_id=None):
        try:
            if inventory_details_id is not None:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT * FROM Inventory_Details WHERE inventory_details_id = %s LIMIT 1",
                                (inventory_details_id,))
                    item = cur.fetchone()

                    if item:
                        columns = [desc[0] for desc in cur.description]
                        data = dict(zip(columns, item))
                        return jsonify(data)
                    else:
                        return jsonify({"error": "Item not found"}), 404
            else:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT * FROM Inventory_Details")
                    all_items = cur.fetchall()

                    if all_items:
                        columns = [desc[0] for desc in cur.description]
                        data = [dict(zip(columns, item)) for item in all_items]
                        return jsonify(data)
                    else:
                        return jsonify({"error": "Empty table"}), 404

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"


inventory_new_view = InventoryDetailsAPI.as_view("inventory_new_api")
app.add_url_rule("/inventory_details_class_view/<int:inventory_details_id>", view_func=inventory_new_view,
                 methods=["GET"])
app.add_url_rule("/inventory_details_class_view", view_func=inventory_new_view, methods=["GET"])
