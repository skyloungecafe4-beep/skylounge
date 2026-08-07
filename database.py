import json
import os

DB_FILE = "database.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return {"menu": [], "orders": []}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {"menu": [], "orders": []}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
