from flask import Flask

app = Flask(__name__)

print("new")
from source_code.api.class_based.admin_api  import Inventory_details, Product_Details, Recurring_product_fullfillment, Status_type, Vendor_details, create_token
from source_code.api.class_based.user_api import Inventory_food_tracker, procurement_fulfillment, procurement_request

