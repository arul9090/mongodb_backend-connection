import os

import certifi
from flask import Flask, redirect, render_template, request, url_for
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError


MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("MONGO_DB", "skillrank_db")


def create_mongo_client():
    options = {"serverSelectionTimeoutMS": 5000}

    if MONGO_URI.startswith("mongodb+srv://"):
        options["tlsCAFile"] = certifi.where()

    return MongoClient(MONGO_URI, **options)


app = Flask(__name__)
client = create_mongo_client()
db = client[DB_NAME]
users = db["users"]


@app.route("/")
def index():
    return render_template("index.html", users=list(users.find().sort("_id", -1)))


@app.post("/add")
def add_user():
    users.insert_one(
        {
            "name": request.form["name"],
            "age": int(request.form["age"]),
        }
    )
    return redirect(url_for("index"))


if __name__ == "__main__":
    try:
        client.admin.command("ping")
    except OperationFailure as exc:
        print("Error: MongoDB authentication failed.")
        print("Check your Atlas database username and password.")
        print("If your password contains symbols, URL-encode it before using it in MONGO_URI.")
        print(f"Details: {exc}")
    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        print("Error: Could not connect to MongoDB.")
        print(f"URI in use: {MONGO_URI}")
        print("For local MongoDB, make sure mongod is running.")
        print("For MongoDB Atlas, set MONGO_URI to your full connection string.")
        print(f"Details: {exc}")
    else:
        print("Connected to MongoDB.")
        app.run(debug=True)
