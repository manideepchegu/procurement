from datetime import datetime

from flask import request, jsonify
from flask.views import MethodView

from source_code import app
from source_code.api.settings import logger, user_info, connection
import psycopg2

class ProcurementFulfillmentAPI(MethodView):

    def __init__(self):
        self.cur, self.conn = connection()

    def get(self, request_type, request_id):
        try:
            if request_type == 'inbox':
                requester_id = request_id
                self.cur.execute("SELECT * FROM procurement_fulfillment WHERE requester_id = %s", (requester_id,))
                inbox = self.cur.fetchall()
                if inbox:
                    columns = [desc[0] for desc in self.cur.description]
                    data = [dict(zip(columns, message)) for message in inbox]
                    message = "Successfully fetched the message from inbox"
                    logger(__name__).info(message)
                    return jsonify(data)
                else:
                    return jsonify({"Info": "Inbox is empty"}), 404

            elif request_type == 'sent':
                req_responder_id = request_id
                self.cur.execute("SELECT * FROM procurement_fulfillment WHERE req_responder_id = %s",
                                    (req_responder_id,))
                sent_box = self.cur.fetchall()
                columns = [desc[0] for desc in self.cur.description]
                data = [dict(zip(columns, message)) for message in sent_box]
                message = "Successfully fetched message from sent box"
                logger(__name__).info(message)
                return jsonify(data)

            else:
                return jsonify({"Info": "Invalid request"})
        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"

    def post(self):
        try:
            if "proc_req_id" and "proc_prod_id" and "proc_vendor_id" and "proc_order_date" and "proc_prod_order_quantity" and "proc_ful_status" and "proc_ful_comments" and "proc_ful_cost" and "requester_id" and "req_responder_id" and "created" and "created_by" not in request.json:
                raise Exception("details are missing")
            data = request.get_json()
            proc_req_id = data.get("proc_req_id")
            proc_prod_id = data.get("proc_prod_id")
            proc_vendor_id = data.get("proc_vendor_id")
            date = data.get("proc_order_date")
            proc_order_date = datetime.strptime(date, '%d/%m/%Y')
            proc_prod_order_quantity = data.get("proc_prod_order_quantity")
            proc_ful_status = data.get("proc_ful_status")
            proc_ful_comments = data.get("proc_ful_comments")
            proc_ful_cost = data.get("proc_ful_cost")
            requester_id = data.get("requester_id")
            req_responder_id = data.get("req_responder_id")
            created = datetime.utcnow()
            created_by = user_info()

            query = "INSERT INTO procurement_fulfillment (proc_req_id, proc_prod_id, proc_vendor_id, proc_order_date, " \
                    "proc_prod_order_quantity, proc_ful_status, proc_ful_comments, proc_ful_cost, requester_id, " \
                    "req_responder_id, created, created_by) " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            values = (proc_req_id, proc_prod_id, proc_vendor_id, proc_order_date, proc_prod_order_quantity,
                      proc_ful_status, proc_ful_comments, proc_ful_cost, requester_id, req_responder_id,
                      created, created_by)

            self.cur.execute(query, values)
            self.conn.commit()
            message = "Successfully added record to ProcurementFulfillment, responded to the request"
            logger(__name__).info(message)
            return "Responded Successfully"

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"

    def put(self, request_type, request_id):
        try:
            if request_type == 'sent':
                proc_ful_id = request_id

                query = "SELECT * FROM procurement_fulfillment WHERE proc_ful_id = %s"
                self.cur.execute(query, (proc_ful_id,))
                response = self.cur.fetchone()

                if response:
                    data = request.get_json()
                    date = data.get("proc_order_date", response[3])
                    proc_order_date = datetime.strptime(date, '%d/%m/%Y')
                    proc_prod_order_quantity = data.get("proc_prod_order_quantity", response[5])
                    proc_ful_status = data.get("proc_ful_status", response[6])
                    proc_ful_comments = data.get("proc_ful_comments", response[7])
                    proc_ful_cost = data.get("proc_ful_cost", response[8])
                    updated = datetime.utcnow()
                    updated_by = user_info()

                    update_query = "UPDATE procurement_fulfillment " \
                                   "SET proc_order_date = %s, proc_prod_order_quantity = %s, proc_ful_status = proc_ful_comments = %s, proc_ful_cost = %s, updated = %s, updated_by = %s" \
                                   " WHERE proc_ful_id = %s"

                    update_values = (proc_order_date, proc_prod_order_quantity, proc_ful_status, proc_ful_comments,
                                     proc_ful_cost, updated, updated_by, proc_ful_id)

                    self.cur.execute(update_query, update_values)
                    self.conn.commit()

                    message = "Response Updated Successfully"
                    logger(__name__).info(message)
                    return "Response Updated Successfully"
                else:
                    return jsonify({"error": "Response not found"}), 404
            else:
                return jsonify({"error": "Invalid request type"})

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"


procurement_fulfillment_view = ProcurementFulfillmentAPI.as_view("procurement_fulfillment_api")
app.add_url_rule("/procurement_fulfillment_class_view/<string:request_type>/<int:request_id>", view_func=procurement_fulfillment_view, methods=["GET", "PUT"])
app.add_url_rule("/procurement_fulfillment_class_view", view_func=procurement_fulfillment_view, methods=["POST"])
