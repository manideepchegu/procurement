from datetime import datetime

from flask import request, jsonify
from flask.views import MethodView
from source_code import app
from source_code.api.settings import logger, user_info, connection, decode_function


import psycopg2, jwt



class ProductDetailsAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.cur, self.conn = connection()

    def get(self, product_id):
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
            with self.conn.cursor() as cur:
                cur.execute("""SELECT * FROM Product_Details WHERE product_id = %s;""", (product_id,))
                row = cur.fetchone()
                if row:
                    data = {
                        'product_id': row[0],
                        'product_name': row[1],
                        'product_description': row[2],
                        'recurring': row[3],
                        'created': row[4],
                        'created_by': row[5],
                        'updated': row[6],
                        'updated_by': row[7]
                    }
                    logger(__name__).info("Successfully fetched the record from Product_Details table")
                    return jsonify(data)
                else:
                    return jsonify({"error": "Product not found"}), 404

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"

    def post(self):
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
            # Add a new product
            if "product_name" and "product_description" and "product_name" not in request.json:
                raise Exception("details are missing")
            data = request.get_json()
            product_name = data.get("product_name")
            product_description = data.get("product_description")
            recurring = data.get("recurring")
            created = datetime.utcnow()
            created_by = user_info()

            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO Product_Details (product_name, product_description, recurring, created, created_by)VALUES (%s, %s, %s, %s, %s)RETURNING product_id""", (product_name, product_description, recurring, created, created_by))
                product_id = cur.fetchone()[0]
                self.conn.commit()

            message = f"Successfully added record to Product_Details"
            logger(__name__).info(message)
            return "Successfully added record to Product_Details table", 201

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"

    def put(self, product_id):
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
            # Update an existing product
            with self.conn.cursor() as cur:
                cur.execute("""SELECT * FROM Product_Details WHERE product_id = %s""", (product_id,))
                product = cur.fetchone()

                if product:
                    data = request.get_json()
                    product_name = data.get("product_name", product[1])
                    product_description = data.get("product_description", product[2])
                    recurring = data.get("recurring", product[3])
                    updated = datetime.utcnow()
                    updated_by = user_info()

                    cur.execute(
                        """UPDATE Product_Detail SET product_name = %s, product_description = %s, recurring = %s, updated = %s, updated_by = %sWHERE product_id = %s""",
                        (product_name, product_description, recurring, updated, updated_by, product_id))
                    self.conn.commit()
                    cur.execute("""SELECT * FROM Product_Details WHERE product_id = %s """, (product_id,))
                    updated_product = cur.fetchone()

                    if updated_product:
                        columns = [desc[0] for desc in cur.description]
                        data = {columns[i]: value for i, value in enumerate(updated_product)}
                        message = "Successfully updated the record in Product_Details table"
                        logger(__name__).info(message)
                        return jsonify(data)
                    else:
                        return jsonify({"error": "Failed to update the record in Product_Details"}), 500
                else:
                    return jsonify({"error": "Product not found"}), 404

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"

    def delete(self, product_id):
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
            # Delete a product
            with self.conn.cursor() as cur:
                cur.execute("""DELETE FROM Product_Details WHERE product_id = %s  """, (product_id,))
                if cur.rowcount > 0:
                    self.conn.commit()
                    message = "Successfully deleted the record from Product_Details table"
                    logger(__name__).info(message)
                    return jsonify({"message": "Product deleted"})
                else:
                    return jsonify({"error": "Product not found"}), 404

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"


product_details_view = ProductDetailsAPI.as_view("product_details_api")
app.add_url_rule("/product_details_class_view/<int:product_id>", view_func=product_details_view, methods=["GET", "PUT", "DELETE"])
app.add_url_rule("/product_details_class_view", view_func=product_details_view, methods=["POST"])
