from flask import Flask, redirect, render_template_string, request, session, url_for
import os
from database import load_data, save_data

app = Flask(__name__)
app.secret_key = "sky_lounge_cinemamor_key"

# --- DEFAULT MENU & DEALS ---
DEFAULT_MENU = [
    {"id": 1, "category": "Burgers", "name": "Zinger Burger", "price": 450, "desc": "Crispy chicken fillet with signature spicy mayo.", "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600"},
    {"id": 2, "category": "Burgers", "name": "Lava Double Cheese Burger", "price": 1000, "desc": "Juicy double patty dripping with liquid cheddar cheese.", "image": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=600"},
    {"id": 3, "category": "Pizza", "name": "Chicken Supreme Pizza", "price_s": 850, "price_m": 1350, "price_l": 1950, "price": 1350, "desc": "Loaded with smoked chicken, mushrooms, black olives & extra cheese.", "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600"},
    {"id": 4, "category": "Starters", "name": "Hot Crispy Wings", "price_5pc": 480, "price_10pc": 890, "price": 480, "desc": "Spicy, crunchy golden wings tossed in special hot sauce.", "image": "https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=600"},
    {"id": 5, "category": "Sandwich", "name": "Club Sandwich", "price": 550, "desc": "Triple-decker grilled sandwich with chicken, egg and fries.", "image": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=600"},
    {"id": 6, "category": "Pasta", "name": "Fettuccine Alfredo Pasta", "price": 850, "desc": "Creamy white sauce pasta topped with grilled chicken chunks.", "image": "https://images.unsplash.com/photo-1621996346565-e3d5d6281298?w=600"}
]

DEFAULT_DEALS = [
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80"
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

# --- 1. CUSTOMER PORTAL (Professional High-End Food UI) ---
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
    <html lang="en" class="scroll-smooth">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sky Lounge — Taste the Luxury | Kasur</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .scrollbar-hide::-webkit-scrollbar { display: none; }
            .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
        </style>
    </head>
    <body class="bg-black text-gray-100 min-h-screen font-sans selection:bg-red-600 selection:text-white">
        
        <header class="bg-zinc-950/90 backdrop-blur-md border-b border-red-900/40 sticky top-0 z-50 shadow-2xl">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex justify-between items-center">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-red-600 to-yellow-500 flex items-center justify-center font-black text-xl shadow-lg shadow-red-600/30">
                        SL
                    </div>
                    <div>
                        <h1 class="text-xl sm:text-2xl font-black tracking-wider text-white">SKY LOUNGE</h1>
                        <p class="text-yellow-400 text-[11px] font-medium tracking-wide">📍 Cinema Mor, Opp PSO Pump, Kasur</p>
                    </div>
                </div>
                
                <a href="/cart" class="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white px-5 py-2.5 rounded-2xl font-black text-sm shadow-lg shadow-red-600/40 flex items-center gap-2.5 transition transform active:scale-95">
                    <span class="text-lg">🛒</span>
                    <span>Bucket</span>
                    <span id="cart-count" class="bg-yellow-400 text-black text-xs font-black px-2 py-0.5 rounded-full">0</span>
                </a>
            </div>
        </header>

        <section class="max-w-7xl mx-auto px-4 sm:px-6 mt-6">
            <div class="flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory scrollbar-hide">
                {% for deal in deals %}
                <div class="min-w-[300px] sm:min-w-[450px] md:min-w-[550px] h-52 sm:h-64 snap-center rounded-3xl overflow-hidden border border-red-900/50 shadow-2xl flex-shrink-0 relative group">
                    <img src="{{ deal }}" alt="Sky Lounge Special Deal" class="w-full h-full object-cover group-hover:scale-105 transition duration-700">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex items-end p-6">
                        <span class="bg-red-600/90 backdrop-blur-sm text-white text-xs font-bold px-3 py-1.5 rounded-xl uppercase tracking-wider">🔥 Exclusive Deal</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>

        <main class="max-w-7xl mx-auto px-4 sm:px-6 my-8 space-y-12">
            
            <div class="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
                {% for cat_name in categories.keys() %}
                <a href="#cat-{{ loop.index }}" class="bg-zinc-900 border border-zinc-800 hover:border-red-600 text-zinc-300 hover:text-white px-5 py-2.5 rounded-2xl font-bold text-sm whitespace-nowrap transition shadow-md">
                    {{ cat_name }}
                </a>
                {% endfor %}
            </div>

            {% for cat_name, items in categories.items() %}
            <section id="cat-{{ loop.index }}" class="scroll-mt-28 pt-4">
                <div class="flex items-center justify-between border-b border-red-900/40 pb-3 mb-6">
                    <h2 class="text-2xl sm:text-3xl font-black text-yellow-400 uppercase tracking-wide flex items-center gap-3">
                        <span class="w-3 h-3 bg-red-600 rounded-full inline-block shadow-lg shadow-red-600"></span>
                        {{ cat_name }}
                    </h2>
                    <span class="text-xs font-semibold text-zinc-400 bg-zinc-900 px-3 py-1 rounded-full border border-zinc-800">{{ items|length }} Items Available</span>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {% for item in items %}
                    <div class="bg-zinc-900/90 backdrop-blur-sm rounded-3xl overflow-hidden border border-zinc-800/80 hover:border-red-600/80 shadow-2xl flex flex-col justify-between transition-all duration-300 group hover:-translate-y-1">
                        <div>
                            <div class="h-48 overflow-hidden relative">
                                <img src="{{ item.image }}" alt="{{ item.name }}" class="w-full h-full object-cover group-hover:scale-110 transition duration-500">
                                <div class="absolute top-3 right-3 bg-black/70 backdrop-blur-md px-3 py-1 rounded-full border border-white/10 text-[11px] font-bold text-yellow-400">
                                    {{ item.category }}
                                </div>
                            </div>
                            <div class="p-5">
                                <h3 class="text-lg font-black text-white group-hover:text-yellow-400 transition">{{ item.name }}</h3>
                                <p class="text-zinc-400 text-xs mt-1.5 line-clamp-2 leading-relaxed">{{ item.desc }}</p>
                                <div class="mt-4 flex items-baseline justify-between">
                                    <span class="text-zinc-500 text-[11px] uppercase font-semibold">Starting at</span>
                                    <span class="text-red-500 font-black text-xl">
                                        {% if item.category == 'Pizza' %}
                                            Rs. {{ item.get('price_m', item.get('price', 0)) }}
                                        {% elif item.category == 'Starters' %}
                                            Rs. {{ item.get('price_5pc', item.get('price', 0)) }}
                                        {% else %}
                                            Rs. {{ item.get('price', 0) }}
                                        {% endif %}
                                    </span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="p-5 pt-0">
                            <a href="/item-detail?id={{ item.id }}" class="block text-center bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white font-black py-3 rounded-2xl shadow-lg shadow-red-600/30 transition text-xs tracking-wider uppercase">
                                + Select & Customize
                            </a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </section>
            {% endfor %}
        </main>

        <div class="fixed bottom-6 right-6 z-50">
            <a href="https://wa.me/923093478600?text=Hello%20Sky%20Lounge,%20I%20want%20to%20order%20food." target="_blank" class="bg-emerald-600 hover:bg-emerald-500 text-white p-4 rounded-full shadow-2xl font-bold flex items-center justify-center transition-all transform hover:scale-110 border-2 border-white/20">
                <span class="text-2xl">💬</span>
            </a>
        </div>

        <footer class="bg-zinc-950 border-t border-zinc-900 mt-20 py-8 text-center text-zinc-500 text-xs">
            <p>© Sky Lounge Kasur • All Rights Reserved.</p>
        </footer>

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

# --- 2. ITEM DETAIL POPUP (Modal View) ---
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
        <title>{{ item.name }} — Sky Lounge</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-black/85 backdrop-blur-md text-white min-h-screen flex items-center justify-center p-4">
        <div class="bg-zinc-900 border border-zinc-800 rounded-3xl shadow-2xl max-w-md w-full overflow-hidden relative">
            <a href="/" class="absolute top-4 right-4 bg-zinc-800 hover:bg-red-600 text-white w-9 h-9 rounded-full flex items-center justify-center font-bold shadow transition z-10">✕</a>
            
            <div class="h-60 overflow-hidden relative">
                <img src="{{ item.image }}" alt="{{ item.name }}" class="w-full h-full object-cover">
            </div>
            
            <div class="p-6 space-y-5">
                <div>
                    <h2 class="text-2xl font-black text-yellow-400">{{ item.name }}</h2>
                    <p class="text-zinc-300 text-xs mt-1.5 leading-relaxed">{{ item.desc }}</p>
                </div>
                
                <div class="space-y-4">
                    {% if item.category == 'Pizza' %}
                    <div>
                        <label class="block text-xs font-semibold text-zinc-400 mb-1.5 uppercase tracking-wider">Select Size</label>
                        <select id="pizza-size" onchange="updatePizzaPrice()" class="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-3.5 text-white font-bold text-sm focus:outline-none focus:border-red-600">
                            <option value="Small (S)" data-price="{{ item.get('price_s', 0) }}">Small (S) — Rs. {{ item.get('price_s', 0) }}</option>
                            <option value="Medium (M)" data-price="{{ item.get('price_m', item.get('price', 0)) }}" selected>Medium (M) — Rs. {{ item.get('price_m', item.get('price', 0)) }}</option>
                            <option value="Large (L)" data-price="{{ item.get('price_l', 0) }}">Large (L) — Rs. {{ item.get('price_l', 0) }}</option>
                        </select>
                    </div>
                    <div class="flex items-center justify-between bg-zinc-950 p-4 rounded-2xl border border-zinc-800">
                        <span class="text-xs text-zinc-400 font-semibold">Total Price:</span>
                        <span class="text-red-500 font-black text-2xl" id="display-price">Rs. {{ item.get('price_m', item.get('price', 0)) }}</span>
                    </div>

                    {% elif item.category == 'Starters' %}
                    <div>
                        <label class="block text-xs font-semibold text-zinc-400 mb-1.5 uppercase tracking-wider">Select Portion</label>
                        <select id="starter-pc" onchange="updateStarterPrice()" class="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-3.5 text-white font-bold text-sm focus:outline-none focus:border-red-600">
                            <option value="5 Pieces" data-price="{{ item.get('price_5pc', item.get('price', 0)) }}">5 Pieces — Rs. {{ item.get('price_5pc', item.get('price', 0)) }}</option>
                            <option value="10 Pieces" data-price="{{ item.get('price_10pc', 0) }}">10 Pieces — Rs. {{ item.get('price_10pc', 0) }}</option>
                        </select>
                    </div>
                    <div class="flex items-center justify-between bg-zinc-950 p-4 rounded-2xl border border-zinc-800">
                        <span class="text-xs text-zinc-400 font-semibold">Total Price:</span>
                        <span class="text-red-500 font-black text-2xl" id="display-price">Rs. {{ item.get('price_5pc', item.get('price', 0)) }}</span>
                    </div>

                    {% else %}
                    <div class="flex items-center justify-between bg-zinc-950 p-4 rounded-2xl border border-zinc-800">
                        <span class="text-xs text-zinc-400 font-semibold">Total Price:</span>
                        <span class="text-red-500 font-black text-2xl" id="display-price">Rs. {{ item.get('price', 0) }}</span>
                    </div>
                    {% endif %}

                    <div>
                        <label class="block text-xs font-semibold text-zinc-400 mb-1.5 uppercase tracking-wider">Quantity</label>
                        <div class="flex items-center justify-between bg-zinc-950 p-2 rounded-2xl border border-zinc-800">
                            <button type="button" onclick="decreaseQty()" class="bg-zinc-800 hover:bg-zinc-700 text-white w-10 h-10 rounded-xl font-black text-lg transition">-</button>
                            <input type="number" id="qty" value="1" min="1" max="10" readonly class="w-16 text-center bg-transparent text-white font-black text-lg">
                            <button type="button" onclick="increaseQty()" class="bg-zinc-800 hover:bg-zinc-700 text-white w-10 h-10 rounded-xl font-black text-lg transition">+</button>
                        </div>
                    </div>
                </div>
                
                <button onclick="addToCart()" class="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white font-black py-4 rounded-2xl shadow-xl shadow-red-600/30 transition text-sm tracking-wider uppercase">
                    Add To Bucket 🛒
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
        <title>Your Food Bucket — Sky Lounge</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-black text-white min-h-screen p-4 flex items-center justify-center font-sans">
        <div class="max-w-lg w-full bg-zinc-900 border border-zinc-800 p-6 sm:p-8 rounded-3xl shadow-2xl">
            <h2 class="text-2xl font-black text-yellow-400 mb-6 text-center tracking-wide">🛒 Your Food Bucket</h2>
            
            <div id="cart-container"></div>

            <div id="checkout-form-section" style="display:none;" class="mt-6 border-t border-zinc-800 pt-6">
                <form onsubmit="submitOrder(event)" class="space-y-4">
                    <div>
                        <label class="block text-xs font-semibold text-zinc-400 mb-1 uppercase tracking-wider">Your Full Name</label>
                        <input type="text" id="c_name" placeholder="e.g. Asad Ali" required class="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-3.5 text-white text-sm focus:outline-none focus:border-red-600">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-zinc-400 mb-1 uppercase tracking-wider">Phone Number</label>
                        <input type="text" id="c_phone" placeholder="e.g. 03093478600" required class="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-3.5 text-white text-sm focus:outline-none focus:border-red-600">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-zinc-400 mb-1 uppercase tracking-wider">Delivery Address (Kasur)</label>
                        <textarea id="c_address" placeholder="House #, Street, Area..." required rows="2" class="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-3.5 text-white text-sm focus:outline-none focus:border-red-600"></textarea>
                    </div>
                    
                    <button type="submit" class="w-full bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 text-white font-black py-4 rounded-2xl shadow-xl shadow-emerald-600/30 transition text-sm uppercase tracking-wider">
                        Place Final Order 🚀
                    </button>
                </form>
            </div>
            
            <div class="text-center mt-6">
                <a href="/" class="text-xs font-bold text-yellow-400 hover:underline">← Add More Items (Back to Menu)</a>
            </div>
        </div>

        <script>
            function loadCart() {
                let cart = JSON.parse(localStorage.getItem('sky_cart') || '[]');
                let container = document.getElementById('cart-container');
                let checkoutSection = document.getElementById('checkout-form-section');

                if (cart.length === 0) {
                    container.innerHTML = '<p class="text-center text-zinc-500 py-8 text-sm">Your bucket is currently empty!</p>';
                    checkoutSection.style.display = 'none';
                    return;
                }

                checkoutSection.style.display = 'block';
                let html = '<div class="space-y-3 mb-6 max-h-60 overflow-y-auto pr-1">';
                let totalAmount = 0;

                cart.forEach((item, index) => {
                    let qty = parseInt(item.qty || 1);
                    let price = parseFloat(item.price || 0);
                    let subtotal = price * qty;
                    totalAmount += subtotal;
                    let displayTitle = item.name + (item.variant ? ` (${item.variant})` : '');
                    
                    html += `
                        <div class="bg-zinc-800/80 p-4 rounded-2xl flex justify-between items-center border border-zinc-700/60">
                            <div>
                                <h4 class="font-bold text-white text-sm">${displayTitle}</h4>
                                <p class="text-xs text-zinc-400 mt-0.5">Rs. ${price} × ${qty}</p>
                            </div>
                            <div class="flex items-center gap-4">
                                <span class="text-yellow-400 font-black text-sm">Rs. ${subtotal}</span>
                                <button type="button" onclick="removeItem(${index})" class="text-zinc-400 hover:text-red-500 text-xs font-bold bg-zinc-900 w-8 h-8 rounded-xl flex items-center justify-center transition">✕</button>
                            </div>
                        </div>
                    `;
                });

                html += `</div>
                    <div class="border-t border-zinc-800 pt-4 flex justify-between text-lg font-black">
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
        ui_items_html += f"<p class='text-zinc-300 border-b border-zinc-800 pb-1.5'>• <strong>{item['qty']}x</strong> {item['name']}{var_text} — <span class='text-yellow-400'>Rs. {sub}</span></p>"

    wa_message = f"🍔 *NEW VIP ORDER - SKY LOUNGE* 🍔\n📍 *Cinema Mor, Kasur*\n\n👤 *Customer Name:* {c_name}\n📞 *Phone:* {c_phone}\n🏠 *Address:* {c_address}\n\n🛒 *Ordered Items:*\n"
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
        <title>Order Confirmed — Sky Lounge</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-black text-white flex items-center justify-center min-h-screen p-4 font-sans">
        <div class="bg-zinc-900 border border-yellow-500/40 p-6 sm:p-8 rounded-3xl shadow-2xl max-w-md w-full text-center">
            <div class="inline-flex items-center justify-center w-20 h-20 bg-yellow-400/10 border border-yellow-400/50 rounded-full text-yellow-400 text-3xl mb-4 shadow-inner">
                👑
            </div>

            <h1 class="text-2xl font-black text-yellow-400 tracking-wider mb-1">ORDER CONFIRMED!</h1>
            <p class="text-red-500 text-xs font-semibold mb-6 uppercase tracking-widest">Sky Lounge • Cinema Mor, Kasur</p>
            
            <div class="bg-zinc-800/80 p-4 rounded-2xl text-left space-y-2 mb-6 text-xs border border-zinc-700/60">
                <p class="text-zinc-300"><strong>Customer:</strong> {c_name}</p>
                <p class="text-zinc-300"><strong>Phone:</strong> {c_phone}</p>
                <p class="text-zinc-300"><strong>Delivery Address:</strong> {c_address}</p>
                <div class="border-t border-zinc-700 pt-2 space-y-1.5">
                    <p class="text-yellow-300 font-bold mb-1">Ordered Items:</p>
                    {ui_items_html}
                </div>
                <div class="border-t border-zinc-700 pt-2 flex justify-between font-black text-sm">
                    <span class="text-white">Total Amount:</span>
                    <span class="text-green-400 text-base">Rs. {total_amount}</span>
                </div>
            </div>
            
            <a href="https://wa.me/923093478600?text={encoded_wa_msg}" target="_blank" class="block w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-black py-3.5 rounded-2xl transition mb-3 text-sm shadow-lg shadow-green-600/30">
                💬 Send Order via WhatsApp
            </a>

            <a href="/" class="block w-full bg-zinc-800 hover:bg-zinc-700 text-zinc-300 font-bold py-3 rounded-2xl transition text-xs">← Return to Menu</a>
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
        <title>Admin Login — Sky Lounge</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-black text-white flex items-center justify-center h-screen p-4 font-sans">
        <div class="bg-zinc-900 border border-zinc-800 p-8 rounded-3xl shadow-2xl max-w-sm w-full text-center">
            <h2 class="text-2xl font-black text-yellow-400 mb-2">🔒 Admin Login</h2>
            <p class="text-zinc-400 text-xs mb-4">Enter password to manage menu & deals</p>
            {% if error %}
            <p class="text-red-500 text-xs font-bold mb-3 bg-red-500/10 p-2 rounded-xl border border-red-500/20">{{ error }}</p>
            {% endif %}
            <form action="/admin" method="POST" class="space-y-4">
                <input type="password" name="password" placeholder="Enter Password" required class="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-3.5 text-white text-center tracking-widest text-sm focus:outline-none focus:border-red-600">
                <button type="submit" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3.5 rounded-2xl shadow-xl shadow-red-600/30 transition text-sm">Login Dashboard</button>
            </form>
            <div class="mt-6"><a href="/" class="text-xs text-zinc-500 hover:text-zinc-300 transition">← Back to Website</a></div>
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
        <title>Admin Dashboard — Sky Lounge</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-black text-white min-h-screen p-4 sm:p-8 font-sans">
        <div class="max-w-7xl mx-auto">
            <header class="flex justify-between items-center mb-8 border-b border-zinc-800 pb-4">
                <div>
                    <h1 class="text-2xl sm:text-3xl font-black text-yellow-400">✨ Sky Lounge Admin Dashboard</h1>
                    <p class="text-zinc-400 text-xs mt-1">Manage your restaurant items, banner deals & live customer orders.</p>
                </div>
                <a href="/admin/logout" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2.5 rounded-2xl font-semibold text-xs transition shadow">Logout</a>
            </header>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
                <div class="bg-zinc-900 p-6 rounded-3xl border border-zinc-800 shadow-xl">
                    <p class="text-zinc-400 text-xs uppercase tracking-wider font-semibold">Total Orders</p>
                    <h3 class="text-3xl font-black text-yellow-400 mt-1">{{ total_orders }}</h3>
                </div>
                <div class="bg-zinc-900 p-6 rounded-3xl border border-zinc-800 shadow-xl">
                    <p class="text-zinc-400 text-xs uppercase tracking-wider font-semibold">Total Revenue</p>
                    <h3 class="text-3xl font-black text-green-400 mt-1">Rs. {{ total_revenue }}</h3>
                </div>
                <div class="bg-zinc-900 p-6 rounded-3xl border border-zinc-800 shadow-xl">
                    <p class="text-zinc-400 text-xs uppercase tracking-wider font-semibold">Active Menu Items</p>
                    <h3 class="text-3xl font-black text-blue-400 mt-1">{{ menu|length }}</h3>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div class="bg-zinc-900 p-6 sm:p-8 rounded-3xl border border-zinc-800 shadow-xl">
                    <h2 class="text-lg font-black mb-4 text-yellow-300 flex items-center gap-2">📦 Live Bucket Orders</h2>
                    {% if orders %}
                        <div class="space-y-4 max-h-[500px] overflow-y-auto pr-2">
                            {% for order in orders %}
                            <div class="bg-zinc-950 p-4 rounded-2xl border border-zinc-800 text-xs space-y-2">
                                <div class="flex justify-between items-center">
                                    <span class="font-bold text-yellow-400 text-sm">{{ order.name }}</span>
                                    <span class="bg-green-500/20 text-green-400 border border-green-500/30 px-3 py-1 rounded-full font-black">Rs. {{ order.price }}</span>
                                </div>
                                <p class="text-zinc-300 bg-zinc-900 p-2.5 rounded-xl border border-zinc-800">{{ order.item }}</p>
                                <div class="text-zinc-400 space-y-0.5 pt-1">
                                    <p><strong>Phone:</strong> <a href="tel:{{ order.phone }}" class="text-blue-400 underline">{{ order.phone }}</a></p>
                                    <p><strong>Address:</strong> {{ order.address }}</p>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    {% else %}
                        <p class="text-zinc-500 text-xs py-8 text-center">No pending orders right now.</p>
                    {% endif %}
                </div>

                <div class="space-y-8">
                    <div class="bg-zinc-900 p-6 sm:p-8 rounded-3xl border border-zinc-800 shadow-xl">
                        <h2 class="text-lg font-black mb-4 text-yellow-300">📢 Add Banner Deal URL</h2>
                        <form action="/admin/add-deal" method="POST" class="space-y-3">
                            <input type="text" name="image_url" placeholder="Paste Deal Image URL (Unsplash/Imgur)" required class="w-full bg-zinc-950 border border-zinc-800 rounded-2xl p-3 text-white text-xs focus:outline-none focus:border-red-600">
                            <button type="submit" class="w-full bg-yellow-500 hover:bg-yellow-600 text-black font-black py-3 rounded-2xl transition text-xs uppercase tracking-wider">Add Banner Deal</button>
                        </form>
                    </div>

                    <div class="bg-zinc-900 p-6 sm:p-8 rounded-3xl border border-zinc-800 shadow-xl">
                        <h2 class="text-lg font-black mb-4 text-yellow-300">➕ Add New Menu Item</h2>
                        <form action="/admin/add-item" method="POST" class="space-y-3" id="add-item-form">
                            <select name="category" id="cat-select" onchange="toggleCategoryFields()" required class="w-full bg-zinc-950 border border-zinc-800 rounded-2xl p-3 text-white text-xs focus:outline-none focus:border-red-600">
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
                            <input type="text" name="name" placeholder="Item Name" required class="w-full bg-zinc-950 border border-zinc-800 rounded-2xl p-3 text-white text-xs focus:outline-none focus:border-red-600">
                            
                            <div id="price-normal-box">
                                <input type="number" name="price" placeholder="Price (e.g. 500)" class="w-full bg-zinc-950 border border-zinc-800 rounded-2xl p-3 text-white text-xs focus:outline-none focus:border-red-600">
                            </div>

                            <div id="price-pizza-box" style="display:none;" class="space-y-2">
                                <input type="number" name="price_s" placeholder="Small Price (S)" class="w-full bg-zinc-950 border border-zinc-800 rounded-2xl p-3 text-white text-xs focus:outline-none focus:border-red-600">
                                <input type="number" name="price_m" placeholder="Medium Price (M)" class="w-full bg-zinc-950 border border-zinc-800 rounded-2xl p-3 text-white text-xs focus:outline-none focus:border-red-600">
                                <input type="number" name="price_l" placeholder="Large Price (L)" class="w-full bg-zinc-950 border border-zinc-800 rounded-2xl p-3 text-white text-xs focus:outline-none focus:border-red-600">
                            </div>

                            <div id="price-starter-box" style="display:none;" class="space-y-2">
                                <input type="number" name="price_5pc" placeholder="5 Pieces Price" class="w-full bg-zinc-950 border border-zinc-800 rounded-2xl p-3 text-white text-xs focus:outline-none focus:border-red-600">
                                <input type="number" name="price_10pc" placeholder="10 Pieces Price" class="w-full bg-zinc-950 border border-zinc-800 rounded-2xl p-3 text-white text-xs focus:outline-none focus:border-red-600">
                            </div>

                            <input type="text" name="image" placeholder="Image URL" required class="w-full bg-zinc-950 border border-zinc-800 rounded-2xl p-3 text-white text-xs focus:outline-none focus:border-red-600">
                            <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-black py-3 rounded-2xl transition text-xs uppercase tracking-wider shadow">Add Item to Menu</button>
                        </form>

                        <h3 class="text-sm font-black mt-8 mb-3 text-zinc-300 uppercase tracking-wider">📋 Current Menu Management</h3>
                        <div class="space-y-2 max-h-48 overflow-y-auto pr-1">
                            {% for item in menu %}
                            <div class="flex justify-between items-center bg-zinc-950 p-3 rounded-2xl text-xs border border-zinc-800">
                                <div>
                                    <span class="font-bold text-yellow-400">[{{ item.category }}]</span> 
                                    <span class="text-zinc-200">{{ item.name }}</span>
                                </div>
                                <form action="/admin/delete-item/{{ item.id }}" method="POST">
                                    <button type="submit" class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-xl text-xs font-bold transition">Delete</button>
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
        except: newItem["price_5pc", 0] = 0.0
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