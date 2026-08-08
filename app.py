from flask import Flask, redirect, render_template_string, request, session, url_for
import os
from database import load_data, save_data

app = Flask(__name__)
app.secret_key = "sky_lounge_cinemamor_key"

# --- DEFAULT MENU & DEALS ---
DEFAULT_MENU = [
    {"id": 1, "category": "Burgers", "name": "Zinger Burger", "price": 450, "desc": "Crispy chicken fillet with special sauce.", "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500"},
    {"id": 2, "category": "Burgers", "name": "Lava Burger", "price": 1000, "desc": "Juicy double patty dripping with cheese.", "image": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=500"},
    {"id": 3, "category": "Pizza", "name": "Chicken Supreme", "price_s": 800, "price_m": 1300, "price_l": 1900, "price": 1300, "desc": "Loaded with chicken, mushrooms, and olives.", "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500"},
    {"id": 4, "category": "Starters", "name": "Hot Crispy Wings", "price_5pc": 450, "price_10pc": 850, "price": 450, "desc": "Spicy and crunchy chicken wings.", "image": "https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=500"}
]

DEFAULT_DEALS = [
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500&auto=format&fit=crop&q=60",
    "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=500&auto=format&fit=crop&q=60"
]

def get_db_safe():
    db = load_data()
    if not db.get("menu"):
        db["menu"] = DEFAULT_MENU
        save_data(db)
    if not db.get("deals"):
        db["deals"] = DEFAULT_DEALS
        save_data(db)
    return db

# --- 1. CUSTOMER PORTAL (KFC Style Layout) ---
@app.route("/")
def customer_portal():
    db = get_db_safe()
    
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
        <title>Sky Lounge VIP - Kasur</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white min-h-screen font-sans pb-24">
        
        <header class="bg-black border-b border-red-900 sticky top-0 z-50 shadow-xl">
            <div class="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
                <div>
                    <h1 class="text-2xl md:text-3xl font-black tracking-wider text-red-600">SKY LOUNGE</h1>
                    <p class="text-yellow-400 text-[10px] md:text-xs font-semibold">📍 Cinema Mor, Kasur</p>
                </div>
                <a href="/cart" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl font-bold text-sm shadow flex items-center gap-2 transition">
                    🛒 Bucket (<span id="cart-count">0</span>)
                </a>
            </div>
        </header>

        <div class="max-w-6xl mx-auto px-4 mt-4">
            <div class="flex gap-4 overflow-x-auto pb-3 snap-x snap-mandatory scrollbar-none">
                {% for deal in deals %}
                <div class="min-w-[300px] md:min-w-[400px] h-44 snap-center rounded-2xl overflow-hidden border border-red-800 shadow-2xl flex-shrink-0 relative group">
                    <img src="{{ deal }}" alt="Special Deal" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
                </div>
                {% endfor %}
            </div>
        </div>

        <main class="max-w-6xl mx-auto px-4 mt-6 space-y-10">
            
            <section>
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-xl md:text-2xl font-black text-white tracking-wide border-l-4 border-red-600 pl-3">EXPLORE MENU</h2>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                    {% for cat_name, items in categories.items() %}
                    <a href="#cat-{{ loop.index }}" class="bg-gray-900 border border-gray-800 hover:border-red-600 rounded-2xl p-4 text-center transition shadow-lg flex flex-col items-center justify-center gap-2 group">
                        <div class="w-14 h-14 bg-red-600/10 text-red-500 rounded-full flex items-center justify-center text-2xl font-black group-hover:bg-red-600 group-hover:text-white transition">
                            🍔
                        </div>
                        <span class="font-bold text-sm text-gray-200 group-hover:text-yellow-400 transition">{{ cat_name }}</span>
                    </a>
                    {% endfor %}
                </div>
            </section>

            {% for cat_name, items in categories.items() %}
            <section id="cat-{{ loop.index }}" class="pt-4">
                <div class="border-b border-red-900/60 pb-2 mb-6">
                    <h2 class="text-2xl font-black text-yellow-400 uppercase tracking-wider">{{ cat_name }}</h2>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
                    {% for item in items %}
                    <div class="bg-gray-900 rounded-2xl overflow-hidden border border-gray-800 shadow-xl flex flex-col justify-between hover:border-red-600 transition group">
                        <div>
                            <div class="overflow-hidden h-40">
                                <img src="{{ item.image }}" alt="{{ item.name }}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
                            </div>
                            <div class="p-4">
                                <h3 class="text-base font-bold text-white line-clamp-1">{{ item.name }}</h3>
                                <p class="text-gray-400 text-xs mt-1 line-clamp-2">{{ item.desc }}</p>
                                <p class="text-red-500 font-black text-lg mt-2">
                                    {% if item.category == 'Pizza' %}
                                        Rs. {{ item.get('price_m', item.get('price', 0)) }}
                                    {% elif item.category == 'Starters' %}
                                        Rs. {{ item.get('price_5pc', item.get('price', 0)) }}
                                    {% else %}
                                        Rs. {{ item.get('price', 0) }}
                                    {% endif %}
                                </p>
                            </div>
                        </div>
                        
                        <div class="p-4 pt-0">
                            <a href="/item-detail?id={{ item.id }}" class="block text-center bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 rounded-xl shadow transition text-xs tracking-wider">SELECT & ORDER</a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </section>
            {% endfor %}
        </main>

        <div class="fixed bottom-6 right-6 z-50">
            <a href="https://wa.me/923093478600?text=Hello%20Sky%20Lounge,%20I%20want%20to%20place%20an%20order." target="_blank" class="bg-green-600 hover:bg-green-500 text-white p-4 rounded-full shadow-2xl font-bold flex items-center justify-center transition transform hover:scale-110 border-2 border-white/20">
                <span class="text-2xl">💬</span>
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
    return render_template_string(html_code, categories=categories, deals=db["deals"])

# --- 2. ITEM DETAIL POPUP ---
@app.route("/item-detail")
def item_detail():
    db = get_db_safe()
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
        <div class="bg-gray-900 border border-gray-800 rounded-3xl shadow-2xl max-w-md w-full overflow-hidden relative">
            <a href="/" class="absolute top-4 right-4 bg-red-600 hover:bg-red-700 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold shadow z-10">✕</a>
            
            <img src="{{ item.image }}" alt="{{ item.name }}" class="w-full h-52 object-cover">
            
            <div class="p-6">
                <h2 class="text-2xl font-black text-yellow-400 mb-1">{{ item.name }}</h2>
                <p class="text-gray-300 text-xs mb-4 leading-relaxed">{{ item.desc }}</p>
                
                <div class="space-y-4 mb-6">
                    {% if item.category == 'Pizza' %}
                    <div>
                        <label class="block text-xs text-gray-400 mb-1 font-semibold">SELECT SIZE</label>
                        <select id="pizza-size" onchange="updatePizzaPrice()" class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-white font-bold text-sm">
                            <option value="Small (S)" data-price="{{ item.get('price_s', 0) }}">Small (S) - Rs. {{ item.get('price_s', 0) }}</option>
                            <option value="Medium (M)" data-price="{{ item.get('price_m', item.get('price', 0)) }}" selected>Medium (M) - Rs. {{ item.get('price_m', item.get('price', 0)) }}</option>
                            <option value="Large (L)" data-price="{{ item.get('price_l', 0) }}">Large (L) - Rs. {{ item.get('price_l', 0) }}</option>
                        </select>
                    </div>
                    <p class="text-red-500 font-black text-xl" id="display-price">Rs. {{ item.get('price_m', item.get('price', 0)) }}</p>

                    {% elif item.category == 'Starters' %}
                    <div>
                        <label class="block text-xs text-gray-400 mb-1 font-semibold">SELECT PORTION</label>
                        <select id="starter-pc" onchange="updateStarterPrice()" class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-white font-bold text-sm">
                            <option value="5 Pieces" data-price="{{ item.get('price_5pc', item.get('price', 0)) }}">5 Pieces - Rs. {{ item.get('price_5pc', item.get('price', 0)) }}</option>
                            <option value="10 Pieces" data-price="{{ item.get('price_10pc', 0) }}">10 Pieces - Rs. {{ item.get('price_10pc', 0) }}</option>
                        </select>
                    </div>
                    <p class="text-red-500 font-black text-xl" id="display-price">Rs. {{ item.get('price_5pc', item.get('price', 0)) }}</p>

                    {% else %}
                    <p class="text-red-500 font-black text-xl">Rs. {{ item.get('price', 0) }}</p>
                    {% endif %}

                    <div>
                        <label class="block text-xs text-gray-400 mb-1 font-semibold">QUANTITY</label>
                        <div class="flex items-center space-x-3">
                            <button type="button" onclick="decreaseQty()" class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-xl font-bold text-lg">-</button>
                            <input type="number" id="qty" value="1" min="1" max="10" readonly class="w-16 text-center bg-gray-800 border border-gray-700 rounded-xl py-2 text-white font-bold">
                            <button type="button" onclick="increaseQty()" class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-xl font-bold text-lg">+</button>
                        </div>
                    </div>
                </div>
                
                <button onclick="addToCart()" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3.5 rounded-2xl shadow-lg transition text-sm">
                    ADD TO BUCKET
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
                let variant = "";
                let itemPrice = parseFloat("{{ item.get('price', item.get('price_m', item.get('price_5pc', 0))) }}");

                if (itemCategory === 'Pizza') {
                    let select = document.getElementById('pizza-size');
                    variant = select.value;
                    itemPrice = parseFloat(select.options[select.selectedIndex].getAttribute('data-price'));
                } else if (itemCategory === 'Starters') {
                    let select = document.getElementById('starter-pc');
                    variant = select.value;
                    itemPrice = parseFloat(select.options[select.selectedIndex].getAttribute('data-price'));
                }

                let itemQty = parseInt(document.getElementById('qty').value);
                let cart = JSON.parse(localStorage.getItem('sky_cart') || '[]');
                
                let existingItem = cart.find(i => i.name === baseName && i.variant === variant);
                if (existingItem) {
                    existingItem.qty = parseInt(existingItem.qty) + itemQty;
                } else {
                    cart.push({ name: baseName, variant: variant, price: itemPrice, qty: itemQty });
                }

                localStorage.setItem('sky_cart', JSON.stringify(cart));
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
    <body class="bg-gray-950 text-white min-h-screen p-4 font-sans flex items-center justify-center">
        <div class="max-w-md w-full bg-gray-900 border border-gray-800 p-6 rounded-3xl shadow-2xl">
            <h2 class="text-2xl font-black text-yellow-400 mb-4 text-center">🛒 Your Food Bucket</h2>
            
            <div id="cart-container"></div>

            <div id="checkout-form-section" style="display:none;" class="mt-4 border-t border-gray-800 pt-4">
                <form onsubmit="submitOrder(event)" class="space-y-3">
                    <div>
                        <label class="block text-xs text-gray-400 mb-1">Your Full Name</label>
                        <input type="text" id="c_name" placeholder="e.g. Asad Ali" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-white text-sm">
                    </div>
                    <div>
                        <label class="block text-xs text-gray-400 mb-1">Phone Number</label>
                        <input type="text" id="c_phone" placeholder="e.g. 03093478600" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-white text-sm">
                    </div>
                    <div>
                        <label class="block text-xs text-gray-400 mb-1">Delivery Address</label>
                        <textarea id="c_address" placeholder="House #, Street, Area..." required rows="2" class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-white text-sm"></textarea>
                    </div>
                    
                    <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-xl shadow transition text-sm">Place Final Order</button>
                </form>
            </div>
            
            <div class="text-center mt-4">
                <a href="/" class="text-xs text-yellow-400 hover:underline">← Back to Menu</a>
            </div>
        </div>

        <script>
            function loadCart() {
                let cart = JSON.parse(localStorage.getItem('sky_cart') || '[]');
                let container = document.getElementById('cart-container');
                let checkoutSection = document.getElementById('checkout-form-section');

                if (cart.length === 0) {
                    container.innerHTML = '<p class="text-center text-gray-400 py-6 text-sm">Your bucket is empty!</p>';
                    checkoutSection.style.display = 'none';
                    return;
                }

                checkoutSection.style.display = 'block';
                let html = '<div class="space-y-3 mb-4 max-h-60 overflow-y-auto">';
                let totalAmount = 0;

                cart.forEach((item, index) => {
                    let qty = parseInt(item.qty || 1);
                    let price = parseFloat(item.price || 0);
                    let subtotal = price * qty;
                    totalAmount += subtotal;
                    let displayTitle = item.name + (item.variant ? ` (${item.variant})` : '');
                    
                    html += `
                        <div class="bg-gray-800 p-3 rounded-xl flex justify-between items-center border border-gray-700 text-sm">
                            <div>
                                <h4 class="font-bold text-white">${displayTitle}</h4>
                                <p class="text-xs text-gray-400">Rs. ${price} x ${qty}</p>
                            </div>
                            <div class="flex items-center gap-3">
                                <span class="text-yellow-400 font-black">Rs. ${subtotal}</span>
                                <button type="button" onclick="removeItem(${index})" class="text-red-500 hover:text-red-400 text-xs font-bold bg-gray-700 px-2 py-1 rounded">✕</button>
                            </div>
                        </div>
                    `;
                });

                html += `</div>
                    <div class="border-t border-gray-800 pt-3 flex justify-between text-lg font-black">
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
                
                let itemsDescArray = cart.map(i => `${i.qty}x ${i.name}` + (i.variant ? ` (${i.variant})` : '') + ` - Rs.${i.price * i.qty}`);
                let itemsDesc = itemsDescArray.join(', ');

                fetch('/save-order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, phone, address, items: itemsDesc, price: totalAmount })
                })
                .then(res => res.json())
                .then(data => {
                    if(data.success) {
                        localStorage.removeItem('sky_cart');
                        window.location.href = `/order-success?name=${encodeURIComponent(name)}&items=${encodeURIComponent(JSON.stringify(cart))}&total=${totalAmount}&phone=${phone}&address=${encodeURIComponent(address)}`;
                    }
                });
            }

            loadCart();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_code)

@app.route("/save-order", methods=["POST"])
def save_order():
    data = request.json
    db = get_db_safe()
    db["orders"].append({
        "item": data["items"],
        "price": data["price"],
        "name": data["name"],
        "phone": data["phone"],
        "address": data["address"]
    })
    save_data(db)
    return {"success": True}

# --- 4. ORDER SUCCESS ---
@app.route("/order-success")
def order_success():
    import json
    c_name = request.args.get("name")
    total_amount = request.args.get("total")
    c_address = request.args.get("address")
    c_phone = request.args.get("phone")
    
    try:
        cart_items = json.loads(request.args.get("items", "[]"))
    except:
        cart_items = []

    ui_items_html = ""
    for item in cart_items:
        sub = float(item['price']) * int(item['qty'])
        var_text = f" ({item['variant']})" if item.get('variant') else ""
        ui_items_html += f"<p class='text-gray-200 border-b border-gray-700/50 pb-1'>• <strong>{item['qty']}x</strong> {item['name']}{var_text} — <span class='text-yellow-400'>Rs. {sub}</span></p>"

    wa_message = f"🍔 *NEW ORDER - SKY LOUNGE* 🍔\n📍 *Cinema Mor, Kasur*\n\n👤 *Customer Name:* {c_name}\n📞 *Phone:* {c_phone}\n🏠 *Address:* {c_address}\n\n🛒 *Ordered Items:*\n"
    for item in cart_items:
        sub = float(item['price']) * int(item['qty'])
        var_text = f" ({item['variant']})" if item.get('variant') else ""
        wa_message += f"▪ {item['qty']}x {item['name']}{var_text} - Rs.{sub}\n"
    
    wa_message += f"\n💰 *Total Amount:* Rs. {total_amount}\n\n_Please confirm and dispatch order quickly!_"
    
    import urllib.parse
    encoded_wa_msg = urllib.parse.quote(wa_message)
    
    success_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Order Confirmed - Sky Lounge</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white flex items-center justify-center min-h-screen p-4">
        <div class="bg-gray-900 border border-yellow-500/40 p-6 rounded-3xl shadow-2xl max-w-md w-full text-center">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-yellow-400/10 border border-yellow-400 rounded-full text-yellow-400 text-3xl mb-3">
                👑
            </div>

            <h1 class="text-2xl font-black text-yellow-400 tracking-wider mb-1">ORDER CONFIRMED!</h1>
            <p class="text-red-400 text-xs font-semibold mb-4">Sky Lounge • Cinema Mor, Kasur</p>
            
            <div class="bg-gray-800 p-4 rounded-2xl text-left space-y-2 mb-4 text-xs">
                <p><strong>Customer:</strong> {c_name}</p>
                <p><strong>Phone:</strong> {c_phone}</p>
                <p><strong>Address:</strong> {c_address}</p>
                <div class="border-t border-gray-700 pt-2 space-y-1">
                    <p class="text-yellow-300 font-bold">Items:</p>
                    {ui_items_html}
                </div>
                <div class="border-t border-gray-700 pt-2 flex justify-between font-black text-sm">
                    <span>Total:</span>
                    <span class="text-green-400">Rs. {total_amount}</span>
                </div>
            </div>
            
            <a href="https://wa.me/923093478600?text={encoded_wa_msg}" target="_blank" class="block w-full bg-green-600 hover:bg-green-500 text-white font-black py-3 rounded-xl transition mb-2 text-sm shadow">
                💬 Send Order via WhatsApp
            </a>

            <a href="/" class="block w-full bg-gray-800 hover:bg-gray-700 text-gray-300 font-bold py-2.5 rounded-xl transition text-xs">← Back to Menu</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(success_html)

# --- 5. ADMIN PANEL ---
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
                <input type="password" name="password" placeholder="Enter Password" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-white text-center tracking-widest text-sm">
                <button type="submit" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-xl shadow transition text-sm">Login</button>
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
        
    db = get_db_safe()
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
                <h1 class="text-2xl font-bold text-yellow-400">✨ Sky Lounge Admin Dashboard</h1>
                <a href="/admin/logout" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl font-semibold text-xs transition">Logout</a>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="bg-gray-800 p-6 rounded-2xl border border-gray-700">
                    <p class="text-gray-400 text-xs">Total Orders</p>
                    <h3 class="text-3xl font-bold text-yellow-400">{{ total_orders }}</h3>
                </div>
                <div class="bg-gray-800 p-6 rounded-2xl border border-gray-700">
                    <p class="text-gray-400 text-xs">Total Revenue</p>
                    <h3 class="text-3xl font-bold text-green-400">Rs. {{ total_revenue }}</h3>
                </div>
                <div class="bg-gray-800 p-6 rounded-2xl border border-gray-700">
                    <p class="text-gray-400 text-xs">Menu Items</p>
                    <h3 class="text-3xl font-bold text-blue-400">{{ menu|length }}</h3>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="bg-gray-800 p-6 rounded-2xl border border-gray-700">
                    <h2 class="text-lg font-semibold mb-4 text-yellow-300">📦 Live Orders</h2>
                    {% if orders %}
                        <div class="space-y-4 max-h-[400px] overflow-y-auto">
                            {% for order in orders %}
                            <div class="bg-gray-700 p-4 rounded-xl border border-gray-600 text-sm">
                                <div class="flex justify-between items-center mb-2">
                                    <h4 class="font-bold text-yellow-400">Items:</h4>
                                    <span class="bg-green-500 text-gray-950 text-xs px-2 py-0.5 rounded-full font-black">Rs. {{ order.price }}</span>
                                </div>
                                <p class="text-xs text-gray-200 bg-gray-800 p-2 rounded mb-2">{{ order.item }}</p>
                                <div class="text-xs text-gray-300 space-y-1">
                                    <p><strong>Name:</strong> {{ order.name }}</p>
                                    <p><strong>Phone:</strong> {{ order.phone }}</p>
                                    <p><strong>Address:</strong> {{ order.address }}</p>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    {% else %}
                        <p class="text-gray-400 text-sm">No pending orders.</p>
                    {% endif %}
                </div>

                <div class="space-y-6">
                    <div class="bg-gray-800 p-6 rounded-2xl border border-gray-700">
                        <h2 class="text-lg font-semibold mb-3 text-yellow-300">📢 Add Banner Deal URL</h2>
                        <form action="/admin/add-deal" method="POST" class="space-y-3">
                            <input type="text" name="image_url" placeholder="Paste Image URL" required class="w-full bg-gray-700 border border-gray-600 rounded-xl p-2.5 text-white text-xs">
                            <button type="submit" class="w-full bg-yellow-500 hover:bg-yellow-600 text-gray-950 font-bold py-2 rounded-xl transition text-xs">Add Deal Banner</button>
                        </form>
                    </div>

                    <div class="bg-gray-800 p-6 rounded-2xl border border-gray-700">
                        <h2 class="text-lg font-semibold mb-3 text-yellow-300">➕ Add New Menu Item</h2>
                        <form action="/admin/add-item" method="POST" class="space-y-3" id="add-item-form">
                            <select name="category" id="cat-select" onchange="toggleCategoryFields()" required class="w-full bg-gray-700 border border-gray-600 rounded-xl p-2.5 text-white text-xs">
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
                            <input type="text" name="name" placeholder="Item Name" required class="w-full bg-gray-700 border border-gray-600 rounded-xl p-2.5 text-white text-xs">
                            
                            <div id="price-normal-box">
                                <input type="number" name="price" placeholder="Price (e.g. 450)" class="w-full bg-gray-700 border border-gray-600 rounded-xl p-2.5 text-white text-xs">
                            </div>

                            <div id="price-pizza-box" style="display:none;" class="space-y-2">
                                <input type="number" name="price_s" placeholder="Small Size Price" class="w-full bg-gray-700 border border-gray-600 rounded-xl p-2.5 text-white text-xs">
                                <input type="number" name="price_m" placeholder="Medium Size Price" class="w-full bg-gray-700 border border-gray-600 rounded-xl p-2.5 text-white text-xs">
                                <input type="number" name="price_l" placeholder="Large Size Price" class="w-full bg-gray-700 border border-gray-600 rounded-xl p-2.5 text-white text-xs">
                            </div>

                            <div id="price-starter-box" style="display:none;" class="space-y-2">
                                <input type="number" name="price_5pc" placeholder="5 Pieces Price" class="w-full bg-gray-700 border border-gray-600 rounded-xl p-2.5 text-white text-xs">
                                <input type="number" name="price_10pc" placeholder="10 Pieces Price" class="w-full bg-gray-700 border border-gray-600 rounded-xl p-2.5 text-white text-xs">
                            </div>

                            <input type="text" name="image" placeholder="Image URL" required class="w-full bg-gray-700 border border-gray-600 rounded-xl p-2.5 text-white text-xs">
                            <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2.5 rounded-xl transition text-xs">Add Item</button>
                        </form>

                        <h3 class="text-base font-semibold mt-6 mb-3 text-gray-300">📋 Current Menu</h3>
                        <div class="space-y-2 max-h-40 overflow-y-auto">
                            {% for item in menu %}
                            <div class="flex justify-between items-center bg-gray-700 p-2.5 rounded-xl text-xs">
                                <div>
                                    <span class="font-bold text-yellow-300">[{{ item.category }}]</span> {{ item.name }}
                                </div>
                                <form action="/admin/delete-item/{{ item.id }}" method="POST">
                                    <button type="submit" class="bg-red-600 hover:bg-red-700 text-white px-2.5 py-1 rounded-lg text-xs font-bold">Delete</button>
                                </form>
                            </div>
                            {% endfor %}
                        </div>
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

@app.route("/admin/add-deal", methods=["POST"])
def add_deal():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    image_url = request.form.get("image_url")
    if image_url:
        db = get_db_safe()
        if "deals" not in db:
            db["deals"] = []
        db["deals"].append(image_url)
        save_data(db)
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/add-item", methods=["POST"])
def add_item():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
        
    category = request.form.get("category", "Others")
    name = request.form.get("name")
    image = request.form.get("image")
    
    db = get_db_safe()
    new_id = (max([m["id"] for m in db["menu"]]) + 1) if db["menu"] else 1
    
    newItem = {
        "id": new_id,
        "category": category,
        "name": name, 
        "desc": "Freshly prepared delicious item.", 
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
    
    db = get_db_safe()
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