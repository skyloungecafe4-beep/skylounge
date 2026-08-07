from flask import Flask, jsonify, redirect, render_template_string, request, url_for
import os

app = Flask(__name__)

# Café ka Menu aur Orders ki list (Database)
menu_items = [
    {"id": 1, "name": "Lava Burger", "price": 1000},
    {"id": 2, "name": "Zinger Burger", "price": 450},
    {"id": 3, "name": "Supreme Pizza", "price": 1550},
    {"id": 4, "name": "Mint Margarita", "price": 300},
]

live_orders = []

# --- 1. CUSTOMER PORTAL (Root URL: /) ---
@app.route("/")
def customer_portal():
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sky Lounge - Customer Portal</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-white min-h-screen p-6">
        <div class="max-w-2xl mx-auto">
            <header class="text-center mb-8">
                <h1 class="text-4xl font-bold text-yellow-400">✨ Sky Lounge Menu</h1>
                <p class="text-gray-400 mt-2">Choose your favorite item and place your order instantly!</p>
            </header>

            <div class="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
                <h2 class="text-2xl font-semibold mb-4 text-yellow-300">🍽️ Available Menu</h2>
                <div class="space-y-4">
                    {% for item in menu %}
                    <div class="flex justify-between items-center bg-gray-700 p-4 rounded-lg">
                        <div>
                            <h3 class="text-lg font-bold">{{ item.name }}</h3>
                            <p class="text-yellow-400">Rs. {{ item.price }}</p>
                        </div>
                        <form action="/place-order" method="POST">
                            <input type="hidden" name="item_name" value="{{ item.name }}">
                            <input type="hidden" name="item_price" value="{{ item.price }}">
                            <button type="submit" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-semibold transition">Order Now</button>
                        </form>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="text-center mt-6">
                <a href="/admin" class="text-sm text-gray-400 hover:text-yellow-400 underline">Switch to Admin Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_code, menu=menu_items)

# --- Customer Order Placing Route ---
@app.route("/place-order", methods=["POST"])
def place_order():
    item_name = request.form.get("item_name")
    item_price = int(request.form.get("item_price"))
    live_orders.append({"item": item_name, "price": item_price})
    
    success_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Order Placed</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-white flex items-center justify-center h-screen">
        <div class="text-center bg-gray-800 p-8 rounded-xl shadow-lg border border-gray-700 max-w-md">
            <h1 class="text-3xl font-bold text-green-400 mb-4">🎉 Order Placed Successfully!</h1>
            <p class="text-gray-300 mb-6">Your order for has been received and is being prepared.</p>
            <a href="/" class="bg-yellow-500 hover:bg-yellow-600 text-gray-900 px-6 py-3 rounded-lg font-bold transition">Order Something Else</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(success_html)

# --- 2. ADMIN DASHBOARD (URL: /admin) ---
@app.route("/admin")
def admin_dashboard():
    total_revenue = sum(order["price"] for order in live_orders)
    total_orders = len(live_orders)
    
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sky Lounge - Admin Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-white min-h-screen p-6">
        <div class="max-w-6xl mx-auto">
            <header class="flex justify-between items-center mb-8 border-b border-gray-700 pb-4">
                <h1 class="text-3xl font-bold text-yellow-400">✨ Sky Lounge Admin Dashboard</h1>
                <a href="/" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold transition">View Customer Portal</a>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="bg-gray-800 p-6 rounded-xl border border-gray-700">
                    <p class="text-gray-400">Total Live Orders</p>
                    <h3 class="text-3xl font-bold text-yellow-400">{{ total_orders }}</h3>
                </div>
                <div class="bg-gray-800 p-6 rounded-xl border border-gray-700">
                    <p class="text-gray-400">Total Revenue</p>
                    <h3 class="text-3xl font-bold text-green-400">Rs. {{ total_revenue }}</h3>
                </div>
                <div class="bg-gray-800 p-6 rounded-xl border border-gray-700">
                    <p class="text-gray-400">Active Menu Items</p>
                    <h3 class="text-3xl font-bold text-blue-400">{{ menu|length }}</h3>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="bg-gray-800 p-6 rounded-xl border border-gray-700">
                    <h2 class="text-xl font-semibold mb-4 text-yellow-300">📦 Live Customer Orders</h2>
                    {% if orders %}
                        <div class="space-y-3">
                            {% for order in orders %}
                            <div class="bg-gray-700 p-4 rounded-lg flex justify-between items-center">
                                <div>
                                    <h4 class="font-bold text-lg">{{ order.item }}</h4>
                                    <p class="text-yellow-400 text-sm">Rs. {{ order.price }}</p>
                                </div>
                                <span class="bg-green-500 text-gray-900 text-xs px-2.5 py-1 rounded-full font-bold">Pending</span>
                            </div>
                            {% endfor %}
                        </div>
                    {% else %}
                        <p class="text-gray-400">No pending orders right now.</p>
                    {% endif %}
                </div>

                <div class="bg-gray-800 p-6 rounded-xl border border-gray-700">
                    <h2 class="text-xl font-semibold mb-4 text-yellow-300">➕ Add New Menu Item</h2>
                    <form action="/add-item" method="POST" class="space-y-4 mb-6">
                        <input type="text" name="name" placeholder="Item Name (e.g. Pasta)" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white">
                        <input type="number" name="price" placeholder="Price (e.g. 800)" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white">
                        <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-lg transition">Add to Menu</button>
                    </form>

                    <h3 class="text-lg font-semibold mb-3 text-gray-300">📋 Current Menu</h3>
                    <div class="space-y-2 max-h-60 overflow-y-auto">
                        {% for item in menu %}
                        <div class="flex justify-between items-center bg-gray-700 p-3 rounded-lg">
                            <span>{{ item.name }} (Rs. {{ item.price }})</span>
                            <form action="/delete-item/{{ item.id }}" method="POST">
                                <button type="submit" class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm font-semibold">Delete</button>
                            </form>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_code, menu=menu_items, orders=live_orders, total_orders=total_orders, total_revenue=total_revenue)

# --- Add Item Route ---
@app.route("/add-item", methods=["POST"])
def add_item():
    name = request.form.get("name")
    price = int(request.form.get("price"))
    new_id = len(menu_items) + 1
    menu_items.append({"id": new_id, "name": name, "price": price})
    return redirect(url_for("admin_dashboard"))

# --- Delete Item Route ---
@app.route("/delete-item/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    global menu_items
    menu_items = [m for m in menu_items if m["id"] != item_id]
    return redirect(url_for("admin_dashboard"))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)