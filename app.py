from flask import Flask, jsonify, redirect, render_template_string, request, session, url_for
import os

app = Flask(__name__)
app.secret_key = "sky_lounge_secret_key_xyz"  # Session chalane ke liye zaroori hai

# Café ka Menu (Items with Sizes/Prices)
menu_items = [
    {
        "id": 1, 
        "name": "Supreme Pizza", 
        "category": "Pizza",
        "has_sizes": True, 
        "prices": {"Small": 600, "Medium": 1100, "Large": 1550}, 
        "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=500&q=80"
    },
    {
        "id": 2, 
        "name": "Zinger Burger", 
        "category": "Burger",
        "has_sizes": False, 
        "price": 450, 
        "image": "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=500&q=80"
    },
    {
        "id": 3, 
        "name": "Lava Burger", 
        "category": "Burger",
        "has_sizes": False, 
        "price": 1000, 
        "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=500&q=80"
    },
    {
        "id": 4, 
        "name": "Mint Margarita", 
        "category": "Drink",
        "has_sizes": False, 
        "price": 300, 
        "image": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=500&q=80"
    }
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
                <h2 class="text-3xl font-extrabold text-yellow-400">OUR MENU</h2>
                <p class="text-gray-400 text-sm mt-1">Select your favorite meal and sizes!</p>
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
                        <a href="/order-form?id={{ item.id }}" class="block text-center bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 rounded-lg shadow transition">Order Now</a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </main>
    </body>
    </html>
    """
    return render_template_string(html_code, menu=menu_items)

# --- 2. ORDER DETAILS FORM ---
@app.route("/order-form")
def order_form():
    item_id = int(request.args.get("id"))
    selected_item = next((item for item in menu_items if item["id"] == item_id), None)
    
    if not selected_item:
        return redirect("/")
        
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
            <p class="text-gray-400 text-sm mb-4">Ordering: <span class="text-white font-bold">{{ item.name }}</span></p>
            
            <form action="/place-order" method="POST" class="space-y-4">
                <input type="hidden" name="item_id" value="{{ item.id }}">
                
                {% if item.has_sizes %}
                <div>
                    <label class="block text-sm text-gray-400 mb-1">Select Size</label>
                    <select name="size" class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white focus:outline-none focus:border-red-600">
                        <option value="Small">Small - Rs. {{ item.prices.Small }}</option>
                        <option value="Medium">Medium - Rs. {{ item.prices.Medium }}</option>
                        <option value="Large">Large - Rs. {{ item.prices.Large }}</option>
                    </select>
                </div>
                {% endif %}

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
                    <textarea name="customer_address" placeholder="House #, Street, Area..." required rows="2" class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white focus:outline-none focus:border-red-600"></textarea>
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
    return render_template_string(html_code, item=selected_item)

# --- 3. PLACE ORDER SUBMISSION ---
@app.route("/place-order", methods=["POST"])
def place_order():
    item_id = int(request.form.get("item_id"))
    selected_item = next((item for item in menu_items if item["id"] == item_id), None)
    
    c_name = request.form.get("customer_name")
    c_phone = request.form.get("customer_phone")
    c_address = request.form.get("customer_address")
    
    if selected_item["has_sizes"]:
        size = request.form.get("size")
        price = selected_item["prices"][size]
        item_title = f"{selected_item['name']} ({size})"
    else:
        price = selected_item["price"]
        item_title = selected_item["name"]
    
    live_orders.append({
        "item": item_title,
        "price": price,
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
            <p class="text-gray-400 mb-6 text-sm">Aapka order mil gaya hai! Jald deliver kar diya jaye ga.</p>
            <a href="/" class="block w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-xl transition">Back to Menu</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(success_html)

# --- 4. ADMIN LOGIN & DASHBOARD ---
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        password = request.form.get("password")
        # Yahan aap apna password change kar sakte hain (abhi "asad123" rakha hai)
        if password == "asad123":
            session["logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Galat Password! Dubara koshish karein."
            
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
            <p class="text-gray-400 text-sm mb-6">Enter password to access dashboard</p>
            
            {% if error %}
                <p class="text-red-500 text-xs mb-4 bg-red-950 p-2 rounded">{{ error }}</p>
            {% endif %}
            
            <form action="/admin" method="POST" class="space-y-4">
                <input type="password" name="password" placeholder="Enter Password" required class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white text-center tracking-widest focus:outline-none focus:border-red-600">
                <button type="submit" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-xl shadow transition">Login</button>
            </form>
            <div class="mt-4">
                <a href="/" class="text-xs text-gray-500 hover:text-gray-300">← Back to Customer Portal</a>
            </div>
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

            <div class="bg-gray-800 p-6 rounded-xl border border-gray-700">
                <h2 class="text-xl font-semibold mb-4 text-yellow-300">📦 Live Customer Orders</h2>
                {% if orders %}
                    <div class="space-y-4 max-h-[500px] overflow-y-auto">
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
        </div>
    </body>
    </html>
    """
    return render_template_string(html_code, menu=menu_items, orders=live_orders, total_orders=total_orders, total_revenue=total_revenue)

@app.route("/admin/logout")
def admin_logout():
    session.pop("logged_in", None)
    return redirect(url_for("admin_login"))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)