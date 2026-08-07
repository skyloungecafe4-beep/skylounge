from flask import Flask, jsonify, redirect, render_template_string, request, url_for
import os

app = Flask(__name__)

# Café ka Mukammal Menu (With Images)
menu_items = [
    {"id": 1, "name": "Lava Burger", "price": 1000, "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=500&q=80"},
    {"id": 2, "name": "Zinger Burger", "price": 450, "image": "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=500&q=80"},
    {"id": 3, "name": "Supreme Pizza", "price": 1550, "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=500&q=80"},
    {"id": 4, "name": "Mint Margarita", "price": 300, "image": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=500&q=80"},
    {"id": 5, "name": "Chicken Broast", "price": 600, "image": "https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?auto=format&fit=crop&w=500&q=80"},
    {"id": 6, "name": "French Fries", "price": 250, "image": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=500&q=80"},
    {"id": 7, "name": "Chocolate Brownie", "price": 350, "image": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=500&q=80"},
    {"id": 8, "name": "Cold Drink (500ml)", "price": 150, "image": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=500&q=80"}
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
        <title>Sky Lounge - Order Online</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white min-h-screen font-sans">
        <header class="bg-red-700 shadow-md py-4 px-6 flex justify-between items-center">
            <h1 class="text-2xl font-black tracking-wider text-white">✨ SKY LOUNGE</h1>
            <span class="text-xs bg-red-800 text-white font-medium px-3 py-1.5 rounded-full">Online Delivery Active</span>
        </header>

        <main class="max-w-6xl mx-auto p-6">
            <div class="mb-8 text-center md:text-left">
                <h2 class="text-3xl font-extrabold text-yellow-400">OUR FULL MENU</h2>
                <p class="text-gray-400 text-sm mt-1">Select an item to enter your delivery details!</p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
                {% for item in menu %}
                <div class="bg-gray-900 rounded-xl overflow-hidden border border-gray-800 shadow-xl flex flex-col justify-between hover:border-red-600 transition">
                    <div>
                        <img src="{{ item.image }}" alt="{{ item.name }}" class="w-full h-44 object-cover">
                        <div class="p-4">
                            <h3 class="text-lg font-bold text-white">{{ item.name }}</h3>
                            <p class="text-red-500 font-extrabold text-lg mt-1">Rs. {{ item.price }}</p>
                        </div>
                    </div>
                    <div class="p-4 pt-0">
                        <a href="/order-form?item={{ item.name }}&price={{ item.price }}" class="block text-center bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 rounded-lg shadow transition">Order Now</a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </main>
    </body>
    </html>
    """
    return render_template_string(html_code, menu=menu_items)

# --- 2. ORDER DETAILS FORM (Customer details input page) ---
@app.route("/order-form")
def order_form():
    item_name = request.args.get("item")
    item_price = request.args.get("price")
    
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Enter Details - Sky Lounge</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white flex items-center justify-center min-h-screen p-4">
        <div class="bg-gray-900 border border-gray-800 p-8 rounded-2xl shadow-2xl max-w-md w-full">
            <h2 class="text-2xl font-black text-yellow-400 mb-2">Delivery Information</h2>
            <p class="text-gray-400 text-sm mb-6">Ordering: <span class="text-white font-bold">{{ item }}</span> (Rs. {{ price }})</p>
            
            <form action="/place-order" method="POST" class="space-y-4">
                <input type="hidden" name="item_name" value="{{ item }}">
                <input type="hidden" name="item_price" value="{{ price }}">
                
                <div>
                    <label class="block text-sm text-gray-400 mb-1">Your Full Name</label>
                    <input type="text" name="customer_name" placeholder="e.g. Ali Khan" required class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white focus:outline-none focus:border-red-600">
                </div>
                <div>
                    <label class="block text-sm text-gray-400 mb-1">Phone Number</label>
                    <input type="text" name="customer_phone" placeholder="e.g. 03001234567" required class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white focus:outline-none focus:border-red-600">
                </div>
                <div>
                    <label class="block text-sm text-gray-400 mb-1">Delivery Address</label>
                    <textarea name="customer_address" placeholder="House #, Street, Area..." required rows="3" class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white focus:outline-none focus:border-red-600"></textarea>
                </div>
                
                <button type="submit" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-xl shadow transition">Confirm Order</button>
            </form>
            <div class="text-center mt-4">
                <a href="/" class="text-sm text-gray-500 hover:text-gray-300">Cancel & Go Back</a>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_code, item=item_name, price=item_price)

# --- 3. PLACE ORDER SUBMISSION ---
@app.route("/place-order", methods=["POST"])
def place_order():
    item_name = request.form.get("item_name")
    item_price = int(request.form.get("item_price"))
    c_name = request.form.get("customer_name")
    c_phone = request.form.get("customer_phone")
    c_address = request.form.get("customer_address")
    
    live_orders.append({
        "item": item_name,
        "price": item_price,
        "name": c_name,
        "phone": c_phone,
        "address": c_address
    })
    
    success_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Order Confirmed</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white flex items-center justify-center h-screen p-4">
        <div class="text-center bg-gray-900 border border-gray-800 p-8 rounded-2xl shadow-2xl max-w-md w-full">
            <h1 class="text-3xl font-black text-green-500 mb-2">Order Confirmed! 🎉</h1>
            <p class="text-gray-400 mb-6 text-sm">Aapka order mil gaya hai! Hum jald aapke diye gaye address par deliver kar dein ge.</p>
            <a href="/" class="block w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-xl transition">Back to Menu</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(success_html)

# --- 4. ADMIN DASHBOARD (URL: /admin) ---
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
                <a href="/" target="_blank" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold transition">Open Customer Portal</a>
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
                        <div class="space-y-4 max-h-[450px] overflow-y-auto">
                            {% for order in orders %}
                            <div class="bg-gray-700 p-4 rounded-lg border border-gray-600">
                                <div class="flex justify-between items-center mb-2">
                                    <h4 class="font-bold text-lg text-yellow-400">{{ order.item }} (Rs. {{ order.price }})</h4>
                                    <span class="bg-green-500 text-gray-900 text-xs px-2.5 py-1 rounded-full font-bold">New Order</span>
                                </div>
                                <div class="text-sm text-gray-300 space-y-1 border-t border-gray-600 pt-2">
                                    <p><strong>Name:</strong> {{ order.name }}</p>
                                    <p><strong>Phone:</strong> <a href="tel:{{ order.phone }}" class="text-blue-400 underline">{{ order.phone }}</a></p>
                                    <p><strong>Address:</strong> {{ order.address }}</p>
                                </div>
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
                        <input type="text" name="name" placeholder="Item Name (e.g. Zinger Burger)" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white">
                        <input type="number" name="price" placeholder="Price (e.g. 500)" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white">
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
    default_img = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=500&q=80"
    menu_items.append({"id": new_id, "name": name, "price": price, "image": default_img})
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