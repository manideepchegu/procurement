from datetime import datetime

from flask import request, jsonify
from flask.views import MethodView

from source_code import app
from source_code.api.settings import logger, user_info, connection
import psycopg2


class ProcurementRequestAPI(MethodView):
    def __init__(self):
        self.cur, self.conn = connection()

    def get(self, request_type, request_id):
        try:
            if request_type == 'inbox':
                req_responder_id = request_id
                query = "SELECT * FROM procurement_fulfillment WHERE req_responder_id = %s"
                self.cur.execute(query, (req_responder_id,))
                inbox = self.cur.fetchall()
                data =[]
                if inbox:
                    feed = {
                        'proc_req_id': inbox[0],
                        'proc_prod_id': inbox[1],
                        'proc_vendor_id': inbox[2],
                        'proc_order_date': inbox[3],
                        'proc_prod_order_quantity': inbox[4],
                        'proc_ful_status': inbox[5],
                        'proc_ful_comments': inbox[6],
                        'proc_ful_cost': inbox[7],
                        'requester_id': inbox[8],
                        'req_responder_id': inbox[9],
                        'created': inbox[10],
                        'created_by': inbox[11]

                    }

                    data.append(feed)

                    message = "Successfully fetched the message from inbox"
                    logger(__name__).info(message)
                    return jsonify(data)

                else:
                    return jsonify({"Info": "Inbox is empty"}), 404

            elif request_type == 'sent':
                requester_id = request_id

                query = "SELECT * FROM procurement_fulfillment WHERE requester_id = %s"
                self.cur.execute(query, (requester_id,))
                sent_box = self.cur.fetchall()
                data=[]
                if sent_box:
                    feed = {
                            'proc_req_id': sent_box[0],
                            'proc_prod_id': sent_box[1],
                            'proc_vendor_id': sent_box[2],
                            'proc_order_date': sent_box[3],
                            'proc_prod_order_quantity': sent_box[4],
                            'proc_ful_status': sent_box[5],
                            'proc_ful_comments': sent_box[6],
                            'proc_ful_cost': sent_box[7],
                            'requester_id': sent_box[8],
                            'req_responder_id': sent_box[9],
                            'created': sent_box[10],
                            'created_by': sent_box[11]

                    }
                    data.append(feed)

                    message = f"Successfully fetched message from sent box"
                    logger(__name__).info(message)
                    return jsonify(data)

                else:
                    return jsonify({"Info": "Sent box is empty"}), 404

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
            if "req_title" and "req_product_id" and "req_prod_quantity" and "req_due_date" and "req_comments" and "req_status" and "requester_id" and "req_responder_id" and "created" and "created_by" not in request.json:
                raise Exception("details are missing")

            data = request.get_json()
            req_title = data.get("req_title")
            req_product_id = data.get("req_product_id")
            req_prod_quantity = data.get("req_prod_quantity")
            date = data.get("req_due_date")
            req_due_date = datetime.strptime(date, '%d/%m/%Y')
            req_comments = data.get("req_comments")
            req_status = data.get("req_status")
            requester_id = data.get("requester_id")
            req_responder_id = data.get("req_responder_id")
            created = datetime.utcnow()
            created_by = user_info()

            cur = self.conn.cursor()

            # Insert data into ProcurementRequest table
            cur.execute("INSERT INTO ProcurementRequest (req_title, req_product_id, req_prod_quantity, req_due_date, req_comments, req_status, requester_id, req_responder_id, created, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (req_title, req_product_id, req_prod_quantity, req_due_date, req_comments, req_status, requester_id, req_responder_id, created, created_by))

            self.conn.commit()
            cur.close()
            self.conn.close()

            message = "Successfully added record to ProcurementRequest"
            logger(__name__).info(message)
            return "Responded Successfully"

        except psycopg2.Error as e:
            # Handle psycopg2 exceptions
            return "psycopg2 error"

        except Exception as e:
            # Handle any other non-psycopg2 exceptions
            return "Other error:"


procurement_request_view = ProcurementRequestAPI.as_view("procurement_request_api")
app.add_url_rule("/procurement_request_class_view/<string:request_type>/<int:request_id>", view_func=procurement_request_view, methods=["GET"])
app.add_url_rule("/procurement_request_class_view", view_func=procurement_request_view, methods=["POST"])
