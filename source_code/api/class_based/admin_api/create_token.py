import jwt
from source_code import app
from flask import request, jsonify


@app.route("/create-token", methods=['GET'], endpoint='create_token')
def create_token():

    if "name" and "user_id" not in request.json:
        return jsonify("details are missing")

    user_id = request.json["user_id"]
    name = request.json["name"]
    encoded = jwt.encode(payload={
        "user_id": user_id,
        "name": name

    }, key='secret', algorithm='HS256')
    print("comments", type(encoded), encoded)

    return encoded