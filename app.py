from flask import Flask, redirect, render_template_string, request, session, url_for
import os
from database import load_data, save_data

app = Flask(__name__)
app.secret_key = "sky_lounge_category_fix_key"

# --- 1. CUSTOMER PORTAL (Categorized Menu) ---
@app.route("/")
def customer_portal():
    db = load_data()
    
    # Group items by category
    categories = {}
    for item in db["menu"]:
        cat = item.get("category", "Others")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

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

        <div class="bg-red-600 sticky top-0 z-40 shadow-md py-3 px-6 flex justify-between items-center max-w-6xl mx-auto md:rounded-b-xl">
            <span class="font-bold text-lg flex items-center gap-2">🛒 Your Bucket</span>
            <a href="/cart" class="bg-yellow-400 hover:bg-yellow-500 text-gray-950 px-4 py-2 rounded-lg font-black text-sm transition shadow flex items-center gap-1">
                View Bucket (<span id="cart-count">0</span>)
            </a>
        </div>

        <main class="max-w-6xl mx-auto p-6 space-y-12">
            {% for cat_name, items in categories.items() %}
            <section>
                <div class="border-b border-red-800 pb-2 mb-6">
                    <h2 class="text-3xl font-black tracking-wider text-yellow-400 uppercase">{{ cat_name }}</h2>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
                    {% for item in items %}
                    <div class="bg-gray-900 rounded-xl overflow-hidden border border-gray-800 shadow-xl flex flex-col justify-between hover:border-red-600 transition">
                        <div>
                            <img src="{{ item.image }}" alt="{{ item.name }}" class="w-full h-40 object-cover">
                            <div class="p-4">
                                <h3 class="text-lg font-bold text-white">{{ item.name }}</h3>
                                <p class="text-red-500 font-extrabold text-lg mt-1">Rs. {{ item.price }}</p>
                            </div>
                        </div>
                        
                        <div class="p-4 pt-0">
                            <a href="/item-detail?id={{ item.id }}" class="block text-center bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 rounded-lg shadow transition text-sm">Order Now</a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </section>
            {% endfor %}
        </main>

        <script>
            function updateCartCount() {
                let cart = [];
                try {
                    let savedCart = localStorage.getItem('sky_cart');
                    if (savedCart) {
                        cart = JSON.parse(savedCart);
                        if (!Array.isArray(cart)) cart = [];
                    }
                } catch (e) {
                    cart = [];
                }
                let totalQty = cart.reduce((sum, item) => sum + parseInt(item.qty || 0), 0);
                let countEl = document.getElementById('cart-count');
                if (countEl) countEl.innerText = totalQty;
            }
            updateCartCount();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_code, categories=categories)

# --- 2. ITEM DETAIL POPUP ---
@app.route("/item-detail")
def item_detail():
    db = load_data()
    try:
        item_id = int(request.args.get("id"))
    except:
        return redirect("/")
        
    selected_item = next((item for item in db["menu"] if item["id"] == item_id), None)
    if not selected_item:
        return redirect("/")
        
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{{ item.name }} - Sky Lounge</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-black/80 text-white min-h-screen flex items-center justify-center p-4">
        <div class="bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden relative">
            <a href="/" class="absolute top-4 right-4 bg-red-600 hover:bg-red-700 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold shadow z-10">✕</a>
            
            <img src="{{ item.image }}" alt="{{ item.name }}" class="w-full h-56 object-cover">
            
            <div class="p-6">
                <h2 class="text-2xl font-black text-yellow-400 mb-2">{{ item.name }}</h2>
                <p class="text-gray-300 text-sm mb-6 leading-relaxed">{{ item.desc }}</p>
                <p class="text-red-500 font-extrabold text-2xl mb-6">Rs. {{ item.price }}</p>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm text-gray-400 mb-1 font-semibold">Quantity</label>
                        <div class="flex items-center space-x-3">
                            <button type="button" onclick="decreaseQty()" class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-bold text-lg">-</button>
                            <input type="number" id="qty" value="1" min="1" max="10" readonly class="w-16 text-center bg-gray-800 border border-gray-700 rounded-lg py-2 text-white font-bold">
                            <button type="button" onclick="increaseQty()" class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-bold text-lg">+</button>
                        </div>
                    </div>
                    
                    <button onclick="addToCart()" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3.5 rounded-xl shadow-lg transition flex justify-center items-center gap-2">
                        <span>ADD TO BUCKET</span>
                    </button>
                </div>
            </div>
        </div>

        <script>
            function increaseQty() {
                let input = document.getElementById('qty');
                let val = parseInt(input.value);
                if(val < 10) input.value = val + 1;
            }
            function decreaseQty() {
                let input = document.getElementById('qty');
                let val = parseInt(input.value);
                if(val > 1) input.value = val - 1;
            }

            function addToCart() {
                let itemName = "{{ item.name }}";
                let itemPrice = parseFloat("{{ item.price }}");
                let itemQty = parseInt(document.getElementById('qty').value);

                let cart = [];
                try {
                    let savedCart = localStorage.getItem('sky_cart');
                    if (savedCart) {
                        cart = JSON.parse(savedCart);
                        if (!Array.isArray(cart)) cart = [];
                    }
                } catch (e) {
                    cart = [];
                }
                
                let existingItem = cart.find(i => i.name === itemName);
                if (existingItem) {
                    existingItem.qty = parseInt(existingItem.qty) + itemQty;
                } else {
                    cart.push({ name: itemName, price: itemPrice, qty: itemQty });
                }

                localStorage.setItem('sky_cart', JSON.stringify(cart));
                alert("Item added to your bucket successfully! 🎉");
                window.location.href = "/";
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_code, item=selected_item)

# --- 3. VIEW CART ---
@app.route("/cart")
def view_cart():
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
            
            <div id="cart-container"></div>

            <div id="checkout-form-section" style="display:none;" class="mt-6 border-t border-gray-800 pt-4">
                <form onsubmit="submitOrder(event)" class="space-y-4">
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">Your Full Name</label>
                        <input type="text" id="c_name" placeholder="e.g. Ali Khan" required class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white">
                    </div>
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">Phone Number</label>
                        <input type="text" id="c_phone" placeholder="e.g. 03001234567" required class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white">
                    </div>
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">Delivery Address</label>
                        <textarea id="c_address" placeholder="House #, Street, Area..." required rows="2" class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white"></textarea>
                    </div>
                    
                    <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-xl shadow transition">Place Final Order</button>
                </form>
            </div>
            
            <div class="text-center mt-6">
                <a href="/" class="text-sm text-yellow-400 hover:underline">← Add More Items (Back to Menu)</a>
            </div>
        </div>

        <script>
            function loadCart() {
                let cart = [];
                try {
                    let savedCart = localStorage.getItem('sky_cart');
                    if (savedCart) {
                        cart = JSON.parse(savedCart);
                        if (!Array.isArray(cart)) cart = [];
                    }
                } catch (e) {
                    cart = [];
                }

                let container = document.getElementById('cart-container');
                let checkoutSection = document.getElementById('checkout-form-section');

                if (cart.length === 0) {
                    container.innerHTML = '<p class="text-center text-gray-400 py-8">Your bucket is empty!</p>';
                    checkoutSection.style.display = 'none';
                    return;
                }

                checkoutSection.style.display = 'block';
                let html = '<div class="space-y-4 mb-6">';
                let totalAmount = 0;

                cart.forEach((item, index) => {
                    let qty = parseInt(item.qty || 1);
                    let price = parseFloat(item.price || 0);
                    let subtotal = price * qty;
                    totalAmount += subtotal;
                    
                    html += `
                        <div class="bg-gray-800 p-4 rounded-lg flex justify-between items-center border border-gray-700">
                            <div>
                                <h4 class="font-bold text-white">${item.name}</h4>
                                <p class="text-xs text-gray-400">Rs. ${price} x ${qty}</p>
                            </div>
                            <div class="flex items-center gap-4">
                                <span class="text-yellow-400 font-extrabold">Rs. ${subtotal}</span>
                                <button type="button" onclick="removeItem(${index})" class="text-red-500 hover:text-red-400 text-xs font-bold bg-gray-700 px-2 py-1 rounded">✕</button>
                            </div>
                        </div>
                    `;
                });

                html += `</div>
                    <div class="border-t border-gray-800 pt-4 flex justify-between text-xl font-black">
                        <span>Total Amount:</span>
                        <span class="text-green-400">Rs. ${totalAmount}</span>
                    </div>
                `;
                container.innerHTML = html;
            }

            function removeItem(index) {
                let cart = [];
                try {
                    cart = JSON.parse(localStorage.getItem('sky_cart')) || [];
                } catch(e) { cart = []; }
                
                cart.splice(index, 1);
                localStorage.setItem('sky_cart', JSON.stringify(cart));
                loadCart();
            }

            function submitOrder(e) {
                e.preventDefault();
                let cart = [];
                try {
                    cart = JSON.parse(localStorage.getItem('sky_cart')) || [];
                } catch(e) { cart = []; }

                let name = document.getElementById('c_name').value;
                let phone = document.getElementById('c_phone').value;
                let address = document.getElementById('c_address').value;

                let totalAmount = cart.reduce((sum, item) => sum + (parseFloat(item.price) * parseInt(item.qty)), 0);
                let itemsDesc = cart.map(i => `${i.qty}x ${i.name}`).join(', ');

                fetch('/save-order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, phone, address, items: itemsDesc, price: totalAmount })
                })
                .then(res => res.json())
                .then(data => {
                    if(data.success) {
                        localStorage.removeItem('sky_cart');
                        window.location.href = `/order-success?name=${encodeURIComponent(name)}&items=${encodeURIComponent(itemsDesc)}&total=${totalAmount}&phone=${phone}&address=${encodeURIComponent(address)}`;
                    }
                });
            }

            loadCart();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_code)

# --- 4. SAVE ORDER ROUTE ---
@app.route("/save-order", methods=["POST"])
def save_order():
    data = request.json
    db = load_data()
    db["orders"].append({
        "item": data["items"],
        "price": data["price"],
        "name": data["name"],
        "phone": data["phone"],
        "address": data["address"]
    })
    save_data(db)
    return {"success": True}

# --- 5. ORDER SUCCESS & WHATSAPP ---
@app.route("/order-success")
def order_success():
    c_name = request.args.get("name")
    items_desc = request.args.get("items")
    total_amount = request.args.get("total")
    c_address = request.args.get("address")
    
    success_html = f"""
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
            
            <a href="https://wa.me/923001234567?text=Hello%20Sky%20Lounge,%20My%20name%20is%20{c_name}.%20I%20ordered:%20{items_desc}.%20Total:%20Rs.{total_amount}.%20Address:%20{c_address}" 
               target="_blank" 
               class="block w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-xl transition mb-3 shadow">
                💬 Send Order via WhatsApp
            </a>

            <a href="/" class="block w-full bg-gray-800 hover:bg-gray-700 text-white font-bold py-3 rounded-xl transition">Back to Sky Lounge</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(success_html)

# --- 6. ADMIN PANEL (With Category Selection) ---
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
        
    db = load_data()
    total_revenue = sum(order["price"] for order in db["orders"])
    total_orders = len(db["orders"])
    
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
                        <select name="category" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm">
                            <option value="" disabled selected>Select Category</option>
                            <option value="Burgers">Burgers</option>
                            <option value="Pizza">Pizza</option>
                            <option value="Sandwich">Sandwich</option>
                            <option value="Pasta">Pasta</option>
                            <option value="Hot & Cold Bar">Hot & Cold Bar</option>
                            <option value="Wraps">Wraps</option>
                            <option value="Chinese">Chinese</option>
                            <option value="Starters">Starters</option>
                        </select>
                        <input type="text" name="name" placeholder="Item Name (e.g. Zinger Burger)" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm">
                        <input type="number" name="price" placeholder="Price (e.g. 450)" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm">
                        <input type="text" name="image" placeholder="Image URL" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm">
                        <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-lg transition text-sm">Add Item to Menu</button>
                    </form>

                    <h3 class="text-lg font-semibold mb-3 text-gray-300">📋 Current Menu</h3>
                    <div class="space-y-2 max-h-56 overflow-y-auto">
                        {% for item in menu %}
                        <div class="flex justify-between items-center bg-gray-700 p-3 rounded-lg text-sm">
                            <div>
                                <span class="font-bold text-yellow-300">[{{ item.category }}]</span> 
                                <span class="truncate max-w-[150px]">{{ item.name }}</span>
                            </div>
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
    return render_template_string(html_code, menu=db["menu"], orders=db["orders"], total_orders=total_orders, total_revenue=total_revenue)

@app.route("/admin/add-item", methods=["POST"])
def add_item():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
        
    category = request.form.get("category", "Others")
    name = request.form.get("name")
    try:
        price = float(request.form.get("price"))
    except:
        price = 0.0
    image = request.form.get("image")
    
    db = load_data()
    new_id = (max([m["id"] for m in db["menu"]]) + 1) if db["menu"] else 1
    
    db["menu"].append({
        "id": new_id,
        "category": category,
        "name": name, 
        "desc": "Delicious freshly prepared meal.", 
        "price": price, 
        "image": image
    })
    save_data(db)
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete-item/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    
    db = load_data()
    db["menu"] = [m for m in db["menu"] if m["id"] != item_id]
    save_data(db)
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/logout")
def admin_logout():
    session.pop("logged_in", None)
    return redirect(url_for("admin_login"))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)