from flask import Flask, jsonify, redirect, render_template_string, request, session, url_for
import os

app = Flask(__name__)
app.secret_key = "sky_lounge_cart_secret_key"

# Café ka Menu
menu_items = [
    {
        "id": 1, 
        "name": "Supreme Pizza", 
        "has_sizes": True, 
        "prices": {"Small": 600, "Medium": 1100, "Large": 1550}, 
        "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=500&q=80"
    },
    {
        "id": 2, 
        "name": "Zinger Burger", 
        "has_sizes": False, 
        "price": 450, 
        "image": "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=500&q=80"
    },
    {
        "id": 3, 
        "name": "Lava Burger", 
        "has_sizes": False, 
        "price": 1000, 
        "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=500&q=80"
    },
    {
        "id": 4, 
        "name": "Mint Margarita", 
        "has_sizes": False, 
        "price": 300, 
        "image": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=500&q=80"
    }
]

live_orders = []

# --- 1. CUSTOMER PORTAL ---
@app.route("/")
def customer_portal():
    if "cart" not in session:
        session["cart"] = []
    cart_count = sum(item["qty"] for item in session["cart"])
    
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sky Lounge - Online Menu</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white min-h-screen font-sans">
        <header class="bg-gradient-to-r from-red-900 via-red-700 to-black shadow-2xl py-8 px-6 text-center border-b border-red-800">
            <h1 class="text-5xl md:text-7xl font-black tracking-widest text-yellow-400 drop-shadow-lg">SKY LOUNGE</h1>
            <p class="text-gray-300 text-sm md:text-base mt-2 font-medium">Taste the Luxury • Order Fresh & Hot</p>
        </header>

        <div class="bg-red-600 sticky top-0 z-50 shadow-md py-3 px-6 flex justify-between items-center max-w-6xl mx-auto md:rounded-b-xl">
            <span class="font-bold text-lg">🛒 Your Bucket</span>
            <a href="/cart" class="bg-yellow-400 hover:bg-yellow-500 text-gray-950 px-4 py-2 rounded-lg font-black text-sm transition shadow">
                View Bucket ({{ cart_count }} items)
            </a>
        </div>

        <main class="max-w-6xl mx-auto p-6">
            <div class="mb-8">
                <h2 class="text-3xl font-extrabold text-white">Explore Menu</h2>
                <p class="text-gray-400 text-sm mt-1">Add multiple items to your bucket and checkout together!</p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
                {% for item in menu %}
                <div class="bg-gray-900 rounded-xl overflow-hidden border border-gray-800 shadow-xl flex flex-col justify-between hover:border-red-600 transition">
                    <div>
                        <img src="{{ item.image }}" alt="{{ item.name }}" class="w-full h-40 object-cover">
                        <div class="p-4">
                            <h3 class="text-lg font-bold text-white">{{ item.name }}</h3>
                            
                            {% if item.has_sizes %}
                                <div class="text-sm text-gray-300 mt-2 space-y-1">
                                    <p>S: <span class="text-red-400 font-bold">Rs. {{ item.prices.Small }}</span></p>
                                    <p>M: <span class="text-red-400 font-bold">Rs. {{ item.prices.Medium }}</span></p>
                                    <p>L: <span class="text-red-400 font-bold">Rs. {{ item.prices.Large }}</span></p>
                                </div>
                            {% else %}
                                <p class="text-red-500 font-extrabold text-lg mt-2">Rs. {{ item.price }}</p>
                            {% endif %}
                        </div>
                    </div>
                    
                    <div class="p-4 pt-0">
                        <form action="/add-to-cart" method="POST">
                            <input type="hidden" name="item_id" value="{{ item.id }}">
                            {% if item.has_sizes %}
                            <div class="mb-2">
                                <select name="size" class="w-full bg-gray-800 text-xs border border-gray-700 rounded p-2 text-white">
                                    <option value="Small">Small</option>
                                    <option value="Medium">Medium</option>
                                    <option value="Large">Large</option>
                                </select>
                            </div>
                            {% endif %}
                            <button type="submit" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 rounded-lg shadow transition text-sm">Add to Bucket</button>
                        </form>
                    </div>
                </div>
                {% endfor %}
            </div>
        </main>
    </body>
    </html>
    """
    return render_template_string(html_code, menu=menu_items, cart_count=cart_count)

# --- Add to Cart ---
@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    if "cart" not in session:
        session["cart"] = []
        
    item_id = int(request.form.get("item_id"))
    selected_item = next((item for item in menu_items if item["id"] == item_id), None)
    
    if selected_item:
        if selected_item.get("has_sizes"):
            size = request.form.get("size")
            price = selected_item["prices"][size]
            title = f"{selected_item['name']} ({size})"
        else:
            price = selected_item["price"]
            title = selected_item["name"]
            
        # Check if already in cart
        found = False
        for cart_item in session["cart"]:
            if cart_item["title"] == title:
                cart_item["qty"] += 1
                found = True
                break
        if not found:
            session["cart"].append({"title": title, "price": price, "qty": 1})
            
    return redirect(url_for("customer_portal"))

# --- View Cart (Bucket) ---
@app.route("/cart")
def view_cart():
    if "cart" not in session:
        session["cart"] = []
        
    cart = session["cart"]
    total_amount = sum(item["price"] * item["qty"] for item in cart)
    
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Your Bucket - Sky Lounge</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white min-h-screen p-6 font-sans">
        <div class="max-w-xl mx-auto bg-gray-900 border border-gray-800 p-6 rounded-2xl shadow-2xl">
            <h2 class="text-3xl font-black text-yellow-400 mb-4 text-center">🛒 Your Food Bucket</h2>
            
            {% if cart %}
                <div class="space-y-4 mb-6">
                    {% for item in cart %}
                    <div class="bg-gray-800 p-4 rounded-lg flex justify-between items-center border border-gray-700">
                        <div>
                            <h4 class="font-bold text-white">{{ item.title }}</h4>
                            <p class="text-xs text-gray-400">Rs. {{ item.price }} x {{ item.qty }}</p>
                        </div>
                        <span class="text-yellow-400 font-extrabold">Rs. {{ item.price * item.qty }}</span>
                    </div>
                    {% endfor %}
                </div>
                
                <div class="border-t border-gray-800 pt-4 mb-6 flex justify-between text-xl font-black">
                    <span>Total Amount:</span>
                    <span class="text-green-400">Rs. {{ total_amount }}</span>
                </div>
                
                <form action="/checkout" method="POST" class="space-y-4">
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">Your Full Name</label>
                        <input type="text" name="customer_name" placeholder="e.g. Ali Khan" required class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white">
                    </div>
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">Phone Number</label>
                        <input type="text" name="customer_phone" placeholder="e.g. 03001234567" required class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white">
                    </div>
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">Delivery Address</label>
                        <textarea name="customer_address" placeholder="House #, Street, Area..." required rows="2" class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white"></textarea>
                    </div>
                    
                    <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-xl shadow transition">Place Final Order</button>
                </form>
            {% else %}
                <p class="text-center text-gray-400 py-8">Your bucket is empty!</p>
            {% endif %}
            
            <div class="text-center mt-6">
                <a href="/" class="text-sm text-yellow-400 hover:underline">← Add More Items (Back to Menu)</a>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_code, cart=cart, total_amount=total_amount)

# --- Checkout & Place Order ---
@app.route("/checkout", methods=["POST"])
def checkout():
    if "cart" not in session or not session["cart"]:
        return redirect("/")
        
    c_name = request.form.get("customer_name")
    c_phone = request.form.get("customer_phone")
    c_address = request.form.get("customer_address")
    
    cart_items = session["cart"]
    total_amount = sum(item["price"] * item["qty"] for item in cart_items)
    
    # Format items description for admin
    items_desc = ", ".join([f"{item['qty']}x {item['title']}" for item in cart_items])
    
    live_orders.append({
        "item": items_desc,
        "price": total_amount,
        "name": c_name,
        "phone": c_phone,
        "address": c_address
    })
    
    # Clear cart after order
    session["cart"] = []
    
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
            <p class="text-gray-400 mb-6 text-sm">Aapka bucket order mil gaya hai! Jald deliver kar diya jaye ga.</p>
            <a href="/" class="block w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-xl transition">Back to Sky Lounge</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(success_html)

# --- ADMIN LOGIN & DASHBOARD ---
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        password = request.form.get("password")
        if password == "asad123":
            session["logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Galat Password!"
            
    login_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Admin Login - Sky Lounge</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white flex items-center justify-center h-screen p-4">
        <div class="bg-gray-900 border border-gray-800 p-8 rounded-2xl shadow-2xl max-w-sm w-full text-center">
            <h2 class="text-2xl font-black text-yellow-400 mb-2">🔒 Admin Login</h2>
            <form action="/admin" method="POST" class="space-y-4 mt-4">
                <input type="password" name="password" placeholder="Enter Password" required class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white text-center tracking-widest focus:outline-none focus:border-red-600">
                <button type="submit" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-xl shadow transition">Login</button>
            </form>
            <div class="mt-4"><a href="/" class="text-xs text-gray-500 hover:text-gray-300">← Back to Portal</a></div>
        </div>
    </body>
    </html>
    """
    return render_template_string(login_html, error=error)

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
        
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
                <a href="/admin/logout" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-semibold text-sm transition">Logout</a>
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
                    <h2 class="text-xl font-semibold mb-4 text-yellow-300">📦 Live Bucket Orders</h2>
                    {% if orders %}
                        <div class="space-y-4 max-h-[450px] overflow-y-auto">
                            {% for order in orders %}
                            <div class="bg-gray-700 p-4 rounded-lg border border-gray-600">
                                <div class="flex justify-between items-center mb-2">
                                    <h4 class="font-bold text-md text-yellow-400">Items: {{ order.item }}</h4>
                                    <span class="bg-green-500 text-gray-900 text-xs px-2.5 py-1 rounded-full font-bold">Rs. {{ order.price }}</span>
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
                    <form action="/admin/add-item" method="POST" class="space-y-3 mb-6">
                        <input type="text" name="name" placeholder="Item Name" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm">
                        <input type="number" name="price" placeholder="Price" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm">
                        <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-lg transition text-sm">Add Item</button>
                    </form>

                    <h3 class="text-lg font-semibold mb-3 text-gray-300">📋 Current Menu</h3>
                    <div class="space-y-2 max-h-56 overflow-y-auto">
                        {% for item in menu %}
                        <div class="flex justify-between items-center bg-gray-700 p-3 rounded-lg text-sm">
                            <span>{{ item.name }}</span>
                            <form action="/admin/delete-item/{{ item.id }}" method="POST">
                                <button type="submit" class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs font-semibold">Delete</button>
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

@app.route("/admin/add-item", methods=["POST"])
def add_item():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    name = request.form.get("name")
    price = int(request.form.get("price"))
    new_id = len(menu_items) + 1
    default_img = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=500&q=80"
    menu_items.append({"id": new_id, "name": name, "has_sizes": False, "price": price, "image": default_img})
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete-item/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    global menu_items
    menu_items = [m for m in menu_items if m["id"] != item_id]
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/logout")
def admin_logout():
    session.pop("logged_in", None)
    return redirect(url_for("admin_login"))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)