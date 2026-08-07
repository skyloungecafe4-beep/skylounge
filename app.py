from flask import Flask, redirect, render_template_string, request, session, url_for
import os
from database import load_data, save_data

app = Flask(__name__)
app.secret_key = "sky_lounge_livechat_key"

# --- 1. CUSTOMER PORTAL (With Live Chat & VIP UI) ---
@app.route("/")
def customer_portal():
    db = load_data()
    
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
        <header class="bg-gradient-to-r from-red-900 via-red-700 to-black shadow-2xl py-6 px-6 text-center border-b border-red-800">
            <h1 class="text-4xl md:text-6xl font-black tracking-widest text-yellow-400 drop-shadow-lg">SKY LOUNGE</h1>
            <p class="text-yellow-200 text-xs md:text-sm mt-1 font-semibold tracking-wider">📍 Saima Mor, Opp PSO Petrol Pump, Kasur</p>
            <p class="text-gray-300 text-xs md:text-sm mt-1 font-medium">Taste the Luxury • Order Fresh & Hot</p>
        </header>

        <div class="bg-red-600 sticky top-0 z-40 shadow-md py-3 px-6 flex justify-between items-center max-w-6xl mx-auto md:rounded-b-xl">
            <span class="font-bold text-lg flex items-center gap-2">🛒 Your Bucket</span>
            <a href="/cart" class="bg-yellow-400 hover:bg-yellow-500 text-gray-950 px-4 py-2 rounded-lg font-black text-sm transition shadow flex items-center gap-1">
                View Bucket (<span id="cart-count">0</span>)
            </a>
        </div>

        <main class="max-w-6xl mx-auto p-6 space-y-12 mb-20">
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
                                <p class="text-red-500 font-extrabold text-lg mt-1">
                                    {% if item.category == 'Pizza' %}
                                        From Rs. {{ item.price_s }}
                                    {% elif item.category == 'Starters' %}
                                        Rs. {{ item.price_5pc }} (5pc)
                                    {% else %}
                                        Rs. {{ item.price }}
                                    {% endif %}
                                </p>
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

        <div class="fixed bottom-6 right-6 z-50">
            <a href="https://wa.me/923093478600?text=Hello%20Sky%20Lounge,%20I%20want%20to%20ask%20something%20about%20menu." target="_blank" class="bg-green-600 hover:bg-green-500 text-white px-5 py-3.5 rounded-full shadow-2xl font-bold flex items-center gap-3 transition transform hover:scale-105 border-2 border-white/20">
                <span class="text-2xl">💬</span>
                <span class="text-sm tracking-wide">Live Chat with Us</span>
            </a>
        </div>

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
                <p class="text-gray-300 text-sm mb-4 leading-relaxed">{{ item.desc }}</p>
                
                <div class="space-y-4 mb-6">
                    {% if item.category == 'Pizza' %}
                    <div>
                        <label class="block text-sm text-gray-400 mb-1 font-semibold">Select Size</label>
                        <select id="pizza-size" onchange="updatePizzaPrice()" class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white font-bold">
                            <option value="S" data-price="{{ item.price_s }}">Small (S) - Rs. {{ item.price_s }}</option>
                            <option value="M" data-price="{{ item.price_m }}" selected>Medium (M) - Rs. {{ item.price_m }}</option>
                            <option value="L" data-price="{{ item.price_l }}">Large (L) - Rs. {{ item.price_l }}</option>
                        </select>
                    </div>
                    <p class="text-red-500 font-extrabold text-2xl" id="display-price">Rs. {{ item.price_m }}</p>

                    {% elif item.category == 'Starters' %}
                    <div>
                        <label class="block text-sm text-gray-400 mb-1 font-semibold">Select Portion / Pieces</label>
                        <select id="starter-pc" onchange="updateStarterPrice()" class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white font-bold">
                            <option value="5pc" data-price="{{ item.price_5pc }}">5 Pieces - Rs. {{ item.price_5pc }}</option>
                            <option value="10pc" data-price="{{ item.price_10pc }}">10 Pieces - Rs. {{ item.price_10pc }}</option>
                        </select>
                    </div>
                    <p class="text-red-500 font-extrabold text-2xl" id="display-price">Rs. {{ item.price_5pc }}</p>

                    {% else %}
                    <p class="text-red-500 font-extrabold text-2xl">Rs. {{ item.price }}</p>
                    {% endif %}

                    <div>
                        <label class="block text-sm text-gray-400 mb-1 font-semibold">Quantity</label>
                        <div class="flex items-center space-x-3">
                            <button type="button" onclick="decreaseQty()" class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-bold text-lg">-</button>
                            <input type="number" id="qty" value="1" min="1" max="10" readonly class="w-16 text-center bg-gray-800 border border-gray-700 rounded-lg py-2 text-white font-bold">
                            <button type="button" onclick="increaseQty()" class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-bold text-lg">+</button>
                        </div>
                    </div>
                </div>
                
                <button onclick="addToCart()" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3.5 rounded-xl shadow-lg transition flex justify-center items-center gap-2">
                    <span>ADD TO BUCKET</span>
                </button>
            </div>
        </div>

        <script>
            function updatePizzaPrice() {
                let select = document.getElementById('pizza-size');
                let price = select.options[select.selectedIndex].getAttribute('data-price');
                document.getElementById('display-price').innerText = "Rs. " + price;
            }
            function updateStarterPrice() {
                let select = document.getElementById('starter-pc');
                let price = select.options[select.selectedIndex].getAttribute('data-price');
                document.getElementById('display-price').innerText = "Rs. " + price;
            }
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
                let baseName = "{{ item.name }}";
                let itemCategory = "{{ item.category }}";
                let finalName = baseName;
                let itemPrice = parseFloat("{{ item.price if item.category not in ['Pizza', 'Starters'] else item.price_m }}");

                if (itemCategory === 'Pizza') {
                    let select = document.getElementById('pizza-size');
                    let sizeText = select.options[select.selectedIndex].text.split(' - ')[0];
                    finalName = baseName + " (" + sizeText + ")";
                    itemPrice = parseFloat(select.options[select.selectedIndex].getAttribute('data-price'));
                } else if (itemCategory === 'Starters') {
                    let select = document.getElementById('starter-pc');
                    let pcText = select.options[select.selectedIndex].text.split(' - ')[0];
                    finalName = baseName + " (" + pcText + ")";
                    itemPrice = parseFloat(select.options[select.selectedIndex].getAttribute('data-price'));
                }

                let itemQty = parseInt(document.getElementById('qty').value);
                let cart = JSON.parse(localStorage.getItem('sky_cart') || '[]');
                
                let existingItem = cart.find(i => i.name === finalName);
                if (existingItem) {
                    existingItem.qty = parseInt(existingItem.qty) + itemQty;
                } else {
                    cart.push({ name: finalName, price: itemPrice, qty: itemQty });
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
                        <input type="text" id="c_name" placeholder="e.g. Asad Ali" required class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white">
                    </div>
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">Phone Number</label>
                        <input type="text" id="c_phone" placeholder="e.g. 03093478600" required class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white">
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
                let cart = JSON.parse(localStorage.getItem('sky_cart') || '[]');
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
                let cart = JSON.parse(localStorage.getItem('sky_cart') || '[]');
                cart.splice(index, 1);
                localStorage.setItem('sky_cart', JSON.stringify(cart));
                loadCart();
            }

            function submitOrder(e) {
                e.preventDefault();
                let cart = JSON.parse(localStorage.getItem('sky_cart') || '[]');
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

# --- 5. VIP ORDER SUCCESS & WHATSAPP MODAL ---
@app.route("/order-success")
def order_success():
    c_name = request.args.get("name")
    items_desc = request.args.get("items")
    total_amount = request.args.get("total")
    c_address = request.args.get("address")
    c_phone = request.args.get("phone")
    
    success_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>VIP Order Confirmed - Sky Lounge</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white flex items-center justify-center min-h-screen p-4">
        <div class="bg-gradient-to-b from-gray-900 to-black border-2 border-yellow-500/50 p-8 rounded-3xl shadow-2xl max-w-lg w-full text-center relative overflow-hidden">
            
            <div class="absolute -top-10 -right-10 w-32 h-32 bg-yellow-500/20 rounded-full blur-2xl"></div>
            
            <div class="inline-flex items-center justify-center w-20 h-20 bg-yellow-400/10 border border-yellow-400 rounded-full text-yellow-400 text-4xl mb-4 shadow-inner">
                👑
            </div>

            <h1 class="text-3xl font-black text-yellow-400 tracking-wider mb-1">VIP ORDER CONFIRMED!</h1>
            <p class="text-red-400 text-sm font-semibold uppercase tracking-widest mb-6">Sky Lounge • Saima Mor, Kasur</p>
            
            <div class="bg-gray-800/80 border border-gray-700/80 p-5 rounded-2xl text-left space-y-2 mb-6 text-sm">
                <p class="text-gray-300"><strong>Customer:</strong> {c_name}</p>
                <p class="text-gray-300"><strong>Phone:</strong> {c_phone}</p>
                <p class="text-gray-300"><strong>Delivery Address:</strong> {c_address}</p>
                <div class="border-t border-gray-700 pt-2 mt-2">
                    <p class="text-yellow-300 font-bold">Ordered Items:</p>
                    <p class="text-gray-200">{items_desc}</p>
                </div>
                <div class="border-t border-gray-700 pt-2 flex justify-between items-center text-base font-black">
                    <span class="text-white">Total Amount:</span>
                    <span class="text-green-400 text-lg">Rs. {total_amount}</span>
                </div>
            </div>

            <p class="text-gray-400 text-xs mb-4">Aapka order receive ho gaya hai! Mazeed foran rabta karne ke liye WhatsApp button dabayein.</p>
            
            <a href="https://wa.me/923093478600?text=Hello%20Sky%20Lounge,%20My%20name%20is%20{c_name}.%20I%20ordered:%20{items_desc}.%20Total:%20Rs.{total_amount}.%20Address:%20{c_address}" 
               target="_blank" 
               class="block w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-black py-4 rounded-xl transition mb-3 shadow-lg flex items-center justify-center gap-2 text-base">
                <span>💬 Send Order via WhatsApp (VIP)</span>
            </a>

            <a href="/" class="block w-full bg-gray-800 hover:bg-gray-700 text-gray-300 font-bold py-3 rounded-xl transition text-sm">← Return to Sky Lounge Menu</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(success_html)

# --- 6. ADMIN PANEL ---
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
                    <form action="/admin/add-item" method="POST" class="space-y-3 mb-6" id="add-item-form">
                        <select name="category" id="cat-select" onchange="toggleCategoryFields()" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm">
                            <option value="" disabled selected>Select Category</option>
                            <option value="Burgers">Burgers</option>
                            <option value="Pizza">Pizza (S/M/L)</option>
                            <option value="Sandwich">Sandwich</option>
                            <option value="Pasta">Pasta</option>
                            <option value="Hot & Cold Bar">Hot & Cold Bar</option>
                            <option value="Wraps">Wraps</option>
                            <option value="Chinese">Chinese</option>
                            <option value="Starters">Starters (5pc/10pc)</option>
                        </select>
                        <input type="text" name="name" placeholder="Item Name" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm">
                        
                        <div id="price-normal-box">
                            <input type="number" name="price" placeholder="Price (e.g. 450)" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm">
                        </div>

                        <div id="price-pizza-box" style="display:none;" class="space-y-2">
                            <input type="number" name="price_s" placeholder="Small Size Price (S)" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm">
                            <input type="number" name="price_m" placeholder="Medium Size Price (M)" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm">
                            <input type="number" name="price_l" placeholder="Large Size Price (L)" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm">
                        </div>

                        <div id="price-starter-box" style="display:none;" class="space-y-2">
                            <input type="number" name="price_5pc" placeholder="5 Pieces Price (5pc)" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm">
                            <input type="number" name="price_10pc" placeholder="10 Pieces Price (10pc)" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm">
                        </div>

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
                                <button type="submit" class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs font-semibold">Delete</label>
                            </form>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>

        <script>
            function toggleCategoryFields() {
                let cat = document.getElementById('cat-select').value;
                let normalBox = document.getElementById('price-normal-box');
                let pizzaBox = document.getElementById('price-pizza-box');
                let starterBox = document.getElementById('price-starter-box');

                normalBox.style.display = 'none';
                pizzaBox.style.display = 'none';
                starterBox.style.display = 'none';

                if (cat === 'Pizza') {
                    pizzaBox.style.display = 'block';
                } else if (cat === 'Starters') {
                    starterBox.style.display = 'block';
                } else {
                    normalBox.style.display = 'block';
                }
            }
        </script>
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
    image = request.form.get("image")
    
    db = load_data()
    new_id = (max([m["id"] for m in db["menu"]]) + 1) if db["menu"] else 1
    
    newItem = {
        "id": new_id,
        "category": category,
        "name": name, 
        "desc": "Delicious freshly prepared meal.", 
        "image": image
    }

    if category == 'Pizza':
        try: newItem["price_s"] = float(request.form.get("price_s", 0))
        except: newItem["price_s"] = 0.0
        try: newItem["price_m"] = float(request.form.get("price_m", 0))
        except: newItem["price_m"] = 0.0
        try: newItem["price_l"] = float(request.form.get("price_l", 0))
        except: newItem["price_l"] = 0.0
        newItem["price"] = newItem["price_m"]
    elif category == 'Starters':
        try: newItem["price_5pc"] = float(request.form.get("price_5pc", 0))
        except: newItem["price_5pc"] = 0.0
        try: newItem["price_10pc"] = float(request.form.get("price_10pc", 0))
        except: newItem["price_10pc"] = 0.0
        newItem["price"] = newItem["price_5pc"]
    else:
        try: newItem["price"] = float(request.form.get("price", 0))
        except: newItem["price"] = 0.0

    db["menu"].append(newItem)
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