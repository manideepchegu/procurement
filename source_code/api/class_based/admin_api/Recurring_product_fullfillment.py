

from flask import jsonify, request
from flask.views import MethodView
from source_code import app
from source_code.api.settings import logger,  connection, decode_function

import psycopg2, jwt


class RecurringProductFulfillment(MethodView):

    def __init__(self):
        self.cur,self.conn = connection()

    def get(self, product_id=None):
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
            if product_id is not None:
                with self.conn.cursor() as cur:
                    cur.execute("""SELECT * FROM Product_Details WHERE product_id = %s AND recurring = 'Y' LIMIT 1""", (product_id,))
                    product = cur.fetchone()

                    if product:
                        columns = [desc[0] for desc in cur.description]
                        data = dict(zip(columns, product))
                        return jsonify(data)
                    else:
                        return jsonify({"error": "No recurring Product"}), 404

            else:
                with self.conn.cursor() as cur:
                    cur.execute("""SELECT * FROM Product_Details WHERE recurring = 'Y'""")
                    all_product = cur.fetchall()

                    if all_product:
                        columns = [desc[0] for desc in cur.description]
                        data = [dict(zip(columns, product)) for product in all_product]
                        message = "Successfully fetched recurring items from Product_Details table"
                        logger(__name__).info(message)
                        return jsonify(data)
                    else:
                        return jsonify({"error": "Table doesn't contain recurring products"}), 404

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"


recurring_product_fulfillment_view = RecurringProductFulfillment.as_view("recurring_product_fulfillment_api")
app.add_url_rule("/recurring_product_fulfillment_class_view/<int:product_id>", view_func=recurring_product_fulfillment_view, methods=["GET"])
app.add_url_rule("/recurring_product_fulfillment_class_view", view_func=recurring_product_fulfillment_view, methods=["GET"])
