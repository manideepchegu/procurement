from datetime import datetime

from flask import request, jsonify
from flask.views import MethodView

from source_code import app
from source_code.api.settings import logger, user_info, connection, decode_function

import psycopg2,jwt


class VendorDetailsAPI(MethodView):

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
                    cur.execute("""SELECT * FROM Vendor_Details WHERE vendor_id = %s LIMIT 1""", (vendor_id,))
                    vendor = cur.fetchone()

                    if vendor:
                        columns = [desc[0] for desc in cur.description]
                        data = dict(zip(columns, vendor))
                        return jsonify(data)
                    else:
                        return jsonify({"error": "Vendor not found"}), 404

            else:
                with self.conn.cursor() as cur:
                    cur.execute("""SELECT * FROM Vendor_Details""")
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
            if "vendor_name" and "location" and "address1" and "address2" and "address3" and "city" and "zipcode" and "state" and "country" and "vendor_contact_rep" and "phone" and "email" and "created" and "created_by" not in request.json:
                raise Exception("details are missing")
            data = request.get_json()
            vendor_name = data.get("vendor_name")
            location = data.get("location")
            address1 = data.get("address1")
            address2 = data.get("address2")
            address3 = data.get("address3")
            city = data.get("city")
            zipcode = data.get("zipcode")
            state = data.get("state")
            country = data.get("country")
            vendor_contact_rep = data.get("vendor_contact_rep")
            phone = data.get("phone")
            email = data.get("email")
            created = datetime.utcnow()
            created_by = user_info()

            with self.conn.cursor() as cur:
                cur.execute("""INSERT INTO Vendor_Details (vendor_name, location, address1, address2, address3, city, zipcode, state, country, vendor_contact_rep, phone, email, created, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """,
                            (vendor_name, location, address1, address2, address3, city, zipcode, state, country, vendor_contact_rep,phone, email, created, created_by))
                self.conn.commit()

            message = "Successfully added record to Vendor_Details"
            logger(__name__).info(message)
            return "Successfully added record to Vendor_Details"

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error"

    def put(self, vendor_id):
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
                cur.execute("SELECT * FROM Vendor_Details WHERE vendor_id = %s", (vendor_id,))
                vendor = cur.fetchone()

                if vendor:
                    data = request.get_json()
                    vendor_name = data.get("vendor_name", vendor[1])
                    location = data.get("location", vendor[2])
                    address1 = data.get("address1", vendor[3])
                    address2 = data.get("address2", vendor[4])
                    address3 = data.get("address3", vendor[5])
                    city = data.get("city", vendor[6])
                    zipcode = data.get("zipcode", vendor[7])
                    state = data.get("state", vendor[8])
                    country = data.get("country", vendor[9])
                    vendor_contact_rep = data.get("vendor_contact_rep", vendor[10])
                    phone = data.get("phone", vendor[11])
                    email = data.get("email", vendor[12])
                    updated = datetime.utcnow()
                    updated_by = user_info()

                    cur.execute("""UPDATE Vendor_Details SET vendor_name = %s, location = %s, address1 = %s, address2 = %s, address3 = %s, city = %s, zipcode = %s, state = %s, country = %s,
                            vendor_contact_rep = %s, phone = %s, email = %s, updated = %s, updated_by = %s WHERE vendor_id = %s""", (vendor_name, location, address1, address2, address3, city, zipcode, state, country,
                          vendor_contact_rep, phone, email, updated, updated_by, vendor_id))
                    self.conn.commit()
                    cur.execute("SELECT * FROM Vendor_Details WHERE vendor_id = %s", (vendor_id,))
                    vendor = cur.fetchone()
                    data = {}
                    for i in range(len(cur.description)):
                        attr = cur.description[i].name
                        data[attr] = vendor[i]

                    message = "Successfully updated the record in Vendor_Details table"
                    logger(__name__).info(message)
                    return jsonify(data)

                else:
                    return jsonify({"error": "Vendor not found"}), 404

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions

            return "Other error:"

    def delete(self, vendor_id):
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
                cur.execute("SELECT * FROM Vendor_Details WHERE vendor_id = %s", (vendor_id,))
                vendor = cur.fetchone()

                if vendor:
                    cur.execute("DELETE FROM Vendor_Details WHERE vendor_id = %s", (vendor_id,))
                    self.conn.commit()

                    message = "Successfully deleted the record from Vendor_Details table"
                    logger(__name__).info(message)
                    return jsonify({"message": "Vendor deleted"})
                else:
                    return jsonify({"error": "Vendor not found"}), 404

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"


vendor_details_api = VendorDetailsAPI.as_view("vendor_details_api")
app.add_url_rule("/vendor_details_class_view/<int:vendor_id>", view_func=vendor_details_api, methods=["GET", "PUT", "DELETE"])
app.add_url_rule("/vendor_details_class_view", view_func=vendor_details_api, methods=["GET", "POST"])
