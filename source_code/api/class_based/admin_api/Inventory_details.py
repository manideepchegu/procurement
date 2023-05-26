from datetime import datetime

from flask import request, jsonify
from flask.views import MethodView

from source_code import app
from source_code.api.settings import logger, user_info, connection,decode_function
import psycopg2, jwt


class InventoryDetailsAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.cur, self.conn = connection()

    def get(self, inventory_details_id=None):
        cur = self.cur
        if "access-token" not in request.headers:
            return jsonify("access token missing")
        encoded_token = request.headers['access-token']
        print("comments", type(encoded_token), encoded_token)
        try:
            decode_token = decode_function(encoded_token)
        except jwt.exceptions.InvalidTokenError:
            return jsonify("invalid access token")
        print('decoded token', decode_token)
        try:
            if inventory_details_id is not None:
                cur.execute("SELECT * FROM inventory_details WHERE inventory_details_id =%s;",(inventory_details_id))
                inventory = cur.fetchone()
                data = []
                if inventory:
                    feed = {
                        'product_id': inventory[0],
                        'quantity': inventory[1],
                        'updated': inventory[2],
                        'updated_by': inventory[3]

                    }
                    data.append(feed)
            else:
                cur.execute("SELECT * FROM inventory_details")
                all_inventory = cur.fetchall()
                data = []
                if  all_inventory:
                    for inventory in all_inventory:
                        feed = {
                            'id': inventory[0],
                            'product_id': inventory[1],
                            'quantity': inventory[2],
                            'updated': inventory[3],
                            'updated_by': inventory[4]

                        }

                        data.append(feed)

            return jsonify(data)
        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"

    def post(self):
        cur = self.cur
        try:
            if "access-token" not in request.headers:
                return jsonify("access token missing")
            encoded_token = request.headers['access-token']
            print("comments", type(encoded_token), encoded_token)
            try:
                decode_token = decode_function(encoded_token)
            except jwt.exceptions.InvalidTokenError:
                return jsonify("invalid access token")
            print('decoded token', decode_token)
            if "product_id" and "quantity" not in request.json:
                raise Exception("details are missing")
            data = request.get_json()
            product_id = data.get("product_id")
            quantity = data.get("quantity")
            created = datetime.utcnow()
            created_by = user_info()

            cur.execute(
                "INSERT INTO inventory_details (product_id, quantity, created, created_by) VALUES (%s, %s, %s, %s);",
                (product_id, quantity, created, created_by))
            self.conn.commit()

            message = "Successfully added record to Inventory_Details"
            logger(__name__).info(message)
            return message, 201

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"

    def put(self, inventory_details_id):
        cur = self.cur
        if "access-token" not in request.headers:
            return jsonify("access token missing")
        encoded_token = request.headers['access-token']
        print("comments", type(encoded_token), encoded_token)
        try:
            decode_token = decode_function(encoded_token)
        except jwt.exceptions.InvalidTokenError:
            return jsonify("invalid access token")
        print('decoded token', decode_token)
        try:
            cur.execute("SELECT * FROM inventory_details WHERE inventory_details_id = %s;", (inventory_details_id,))
            item = cur.fetchone()

            if item:
                data = request.get_json()
                product_id = data.get("product_id", item[1])
                quantity = data.get("quantity", item[2])
                updated = datetime.utcnow()
                updated_by = user_info()

                cur.execute(
                    "UPDATE inventory_details SET product_id = %s, quantity = %s, updated = %s, updated_by = %s WHERE inventory_details_id= %s;",
                    (product_id, quantity, updated, updated_by, inventory_details_id))
                self.conn.commit()

                cur.execute("SELECT * FROM inventory_details WHERE inventory_details_id = %s;", (inventory_details_id,))
                updated_item = cur.fetchone()
                if updated_item:
                    data = {
                        'id' : updated_item[0],
                        'product_id': updated_item[1],
                        'quantity' : updated_item[2],
                        'updated' : updated_item[3],
                        'updated_by' : updated_item[4]
                    }

                message = "Successfully updated the record in Inventory_Details table"
                logger(__name__).info(message)
                return jsonify(data)
            else:
                return jsonify({"error": "item not found"}), 404

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"

    def delete(self, inventory_details_id):
        cur = self.cur
        if "access-token" not in request.headers:
            return jsonify("access token missing")
        encoded_token = request.headers['access-token']
        print("comments", type(encoded_token), encoded_token)
        try:
            decode_token = decode_function(encoded_token)
        except jwt.exceptions.InvalidTokenError:
            return jsonify("invalid access token")
        print('decoded token', decode_token)
        try:
            # Check if the item exists
            cur.execute("SELECT * FROM inventory_details WHERE inventory_details_id = %s;", (inventory_details_id,))
            exists = cur.fetchone()

            if exists:
                # Delete the item
                cur.execute("DELETE FROM inventory_details WHERE inventory_details_id= %s;", (inventory_details_id,))
                self.conn.commit()
                message = f"Successfully deleted the record from Inventory_Details table"
                logger(__name__).info(message)
                return jsonify({"message": "item deleted"})
            else:
                return jsonify({"error": "item not found"}), 404

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"


inventory_details_view = InventoryDetailsAPI.as_view("inventory_details_api")
app.add_url_rule("/inventory_details_class_view/<int:inventory_details_id>", view_func=inventory_details_view,
                 methods=["GET", "PUT", "DELETE"])
app.add_url_rule("/inventory_details_class_view", view_func=inventory_details_view, methods=["GET", "POST"])
