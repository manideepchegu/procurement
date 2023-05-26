from datetime import datetime

from flask import request, jsonify
from flask.views import MethodView

from source_code import app
from source_code.api.settings import logger,  connection, user_info, decode_function

import psycopg2, jwt


class StatusTypeAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.cur, self.conn = connection()

    def get(self, vendor_id=None):
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
            if vendor_id is not None:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT * FROM Vendor_Details WHERE vendor_id = %s LIMIT 1", (vendor_id,))
                    vendor = cur.fetchone()

                    if vendor:
                        columns = [desc[0] for desc in cur.description]
                        data = dict(zip(columns, vendor))
                        return jsonify(data)
                    else:
                        return jsonify({"error": "Vendor not found"}), 404

            else:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT * FROM Vendor_Details")
                    all_vendor = cur.fetchall()

                    if all_vendor:
                        columns = [desc[0] for desc in cur.description]
                        data = [dict(zip(columns, vendor)) for vendor in all_vendor]
                        return jsonify(data)
                    else:
                        return jsonify({"error": "Empty table"}), 404

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"

    def post(self):
        try:
            # Add a new product
            if "status_name" not in request.json():
                raise Exception("details are missing")
            data = request.get_json()
            status_name = data.get("status_name")
            created = datetime.utcnow()
            created_by = user_info()

            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO Status_Type (status_name, created, created_by) VALUES (%s, %s, %s) RETURNING status_id",
                    (status_name, created, created_by))
                status_id = cur.fetchone()[0]
                self.conn.commit()

            message = f"Successfully added record to Status_Type"
            logger(__name__).info(message)
            return "Successfully added record to Status_Type table", 201

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"

    def put(self, status_id):
        try:
            # Update an existing status
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM Status_Type WHERE status_id = %s LIMIT 1", (status_id,))
                status = cur.fetchone()

                if status:
                    data = request.get_json()
                    status_name = data.get("status_name", status["status_name"])
                    updated = datetime.utcnow()
                    updated_by = user_info()

                    cur.execute(
                        "UPDATE Status_Type SET status_name = %s, updated = %s, updated_by = %s WHERE status_id = %s",
                        (status_name, updated, updated_by, status_id))
                    self.conn.commit()

                    cur.execute("SELECT * FROM Status_Type WHERE status_id = %s LIMIT 1", (status_id,))
                    status = cur.fetchone()

                    columns = [desc[0] for desc in cur.description]
                    data = dict(zip(columns, status))
                    message = f"Successfully updated the record in Status_Type table"
                    logger(__name__).info(message)
                    return jsonify(data)
                else:
                    return jsonify({"error": "Status not found"}), 404

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"

    def delete(self, status_id):
        try:
            # Delete a status
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM Status_Type WHERE status_id = %s LIMIT 1", (status_id,))
                status = cur.fetchone()

                if status:
                    cur.execute("DELETE FROM Status_Type WHERE status_id = %s", (status_id,))
                    self.conn.commit()

                    message = f"Successfully deleted the record from Status_Type table"
                    logger(__name__).info(message)
                    return jsonify({"message": "Status deleted"})
                else:
                    return jsonify({"error": "Status not found"}), 404

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"


status_type_view = StatusTypeAPI.as_view("status_type_api")
app.add_url_rule("/status_type_class_view/<int:status_id>", view_func=status_type_view, methods=["GET", "PUT", "DELETE"])
app.add_url_rule("/status_type_class_view", view_func=status_type_view, methods=["GET", "POST"])
