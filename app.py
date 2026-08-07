from flask import Flask, redirect, render_template_string, request, session, url_for
import os
import base64
from database import load_data, save_data

app = Flask(__name__)
app.secret_key = "sky_lounge_vip_slider_key_v10"

# --- DEFAULT DATA BACKUP ---
DEFAULT_MENU = [
    {"id": 1, "category": "Burgers", "name": "Zinger Burger", "price": 450, "desc": "Crispy chicken fillet with special sauce.", "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=500"},
    {"id": 2, "category": "Pizza", "name": "Chicken Supreme (M)", "price_s": 800, "price_m": 1300, "price_l": 1900, "price": 1300, "desc": "Loaded with chicken, mushrooms, and olives.", "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=500"},
    {"id": 3, "category": "Starters", "name": "Hot Crispy Wings (5pc)", "price_5pc": 450, "price_10pc": 850, "price": 450, "desc": "Spicy and crunchy chicken wings.", "image": "https://images.unsplash.com/photo-1527477396000-e27163b481c2?q=80&w=500"}
]

DEFAULT_SLIDERS = [
    {"id": 1, "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?q=80&w=1920"},
    {"id": 2, "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=1920"},
    {"id": 3, "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=1920"}
]

def get_db_safe():
    db = load_data()
    if not db.get("menu"):
        db["menu"] = DEFAULT_MENU
    if not db.get("sliders") or len(db.get("sliders")) == 0:
        db["sliders"] = DEFAULT_SLIDERS
    save_data(db)
    return db

# --- 1. CUSTOMER PORTAL ---
@app.route("/")
def customer_portal():
    db = get_db_safe()
    
    categories = {}
    for item in db["menu"]:
        cat = item.get("category", "Others")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    slider_list = db.get("sliders", DEFAULT_SLIDERS)

    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sky Lounge Cafe - Kasur</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .slider-container { position: relative; overflow: hidden; width: 100%; height: 260px; }
            @media(min-width: 768px) { .slider-container { height: 400px; } }
            .slider-wrapper { display: flex; transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1); height: 100%; width: 100%; }
            .slide { min-width: 100%; height: 100%; flex-shrink: 0; }
            .slide img { width: 100%; height: 100%; object-fit: cover; }
            .slider-nav { position: absolute; bottom: 15px; left: 50%; transform: translateX(-50%); display: flex; gap: 8px; z-index: 10; }
            .nav-dot { width: 10px; height: 10px; background: rgba(255, 255, 255, 0.5); border-radius: 50%; cursor: pointer; transition: all 0.3s; }
            .nav-dot.active { background: #e11d48; width: 25px; border-radius: 5px; }
        </style>
    </head>
    <body class="bg-gray-950 text-white min-h-screen font-sans">
        
        <div class="bg-gray-900 border-b border-gray-800 py-2.5 px-4 flex justify-between items-center sticky top-0 z-50 shadow-md">
            <div class="flex items-center gap-2">
                <span class="text-xs font-black tracking-widest text-yellow-400 uppercase">⚡ Sky Lounge Cafe</span>
            </div>
            <a href="/cart" class="bg-red-600 hover:bg-red-500 text-white px-4 py-1.5 rounded-full font-black text-xs transition shadow flex items-center gap-1.5">
                🛒 BUCKET (<span id="cart-count">0</span>)
            </a>
        </div>

        <div class="max-w-7xl mx-auto px-4 pt-6 pb-2">
            <div class="bg-gradient-to-b from-gray-900 to-gray-950 rounded-3xl overflow-hidden border border-yellow-500/20 shadow-2xl">
                
                <div class="py-5 px-4 text-center bg-gray-900/90 backdrop-blur border-b border-gray-800">
                    <h1 class="text-3xl md:text-5xl font-black tracking-widest text-yellow-400 uppercase drop-shadow">SKY LOUNGE CAFE</h1>
                    <p class="text-gray-300 text-xs md:text-sm mt-1.5 font-semibold">📍 Cinema Mor, Opp PSO Petrol Pump, Kasur</p>
                </div>

                <div class="slider-container bg-black" id="main-slider">
                    <div class="slider-wrapper" id="slider-wrapper">
                        {% for s in slider_list %}
                        <div class="slide"><img src="{{ s.image }}" alt="Cafe Menu Slide"></div>
                        {% endfor %}
                    </div>
                    <div class="slider-nav" id="slider-dots">
                        {% for s in slider_list %}
                        <span class="nav-dot {% if loop.first %}active{% endif %}" onclick="currentSlide({{ loop.index0 }})"></span>
                        {% endfor %}
                    </div>
                </div>

            </div>
        </div>

        <main class="max-w-7xl mx-auto p-4 md:p-6 space-y-10 mb-20">
            
            <nav class="flex gap-2 overflow-x-auto pb-2 scrollbar-none">
                {% for cat_name in categories.keys() %}
                <a href="#cat-{{ cat_name }}" class="bg-gray-900 hover:bg-red-600 text-gray-300 hover:text-white px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap border border-gray-800 transition shadow">{{ cat_name }}</a>
                {% endfor %}
            </nav>

            {% for cat_name, items in categories.items() %}
            <section id="cat-{{ cat_name }}" class="pt-4">
                <div class="border-l-4 border-red-600 pl-3 mb-6">
                    <h2 class="text-2xl md:text-3xl font-black tracking-wider text-yellow-400 uppercase">{{ cat_name }}</h2>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    {% for item in items %}
                    <div class="bg-gray-900 rounded-2xl overflow-hidden border border-gray-800 shadow-xl flex flex-col justify-between group hover:border-yellow-500/50 transition-all">
                        <div>
                            <img src="{{ item.image }}" alt="{{ item.name }}" class="w-full h-48 object-cover group-hover:scale-105 transition duration-500">
                            <div class="p-4">
                                <h3 class="text-lg font-bold text-white group-hover:text-yellow-400 transition">{{ item.name }}</h3>
                                <p class="text-gray-400 text-xs mt-1 line-clamp-2">{{ item.get('desc', 'Freshly prepared meal') }}</p>
                                <p class="text-red-500 font-black text-xl mt-3">
                                    {% if item.category == 'Pizza' %}
                                        From Rs. {{ item.get('price_s', 0) }}
                                    {% elif item.category == 'Starters' %}
                                        Rs. {{ item.get('price_5pc', 0) }}
                                    {% else %}
                                        Rs. {{ item.get('price', 0) }}
                                    {% endif %}
                                </p>
                            </div>
                        </div>
                        
                        <div class="p-4 pt-0">
                            <a href="/item-detail?id={{ item.id }}" class="block text-center bg-red-600 hover:bg-red-500 text-white font-black py-2.5 rounded-xl shadow transition text-xs tracking-wider">+ ADD TO BUCKET</a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </section>
            {% endfor %}
        </main>

        <div class="fixed bottom-5 right-5 z-50">
            <a href="https://wa.me/923093478600?text=Hello%20Sky%20Lounge%20Cafe,%20I%20want%20to%20order." target="_blank" class="bg-green-600 hover:bg-green-500 text-white p-3.5 rounded-full shadow-2xl flex items-center justify-center transition transform hover:scale-110 border-2 border-white/20">
                <span class="text-xl">💬</span>
            </a>
        </div>

        <script>
            let slideIndex = 0;
            const slidesWrapper = document.getElementById('slider-wrapper');
            const totalSlides = slidesWrapper ? slidesWrapper.children.length : 0;
            const dots = document.querySelectorAll('.nav-dot');

            function showSlides() {
                if(!slidesWrapper || totalSlides === 0) return;
                if(slideIndex >= totalSlides) slideIndex = 0;
                if(slideIndex < 0) slideIndex = totalSlides - 1;
                
                slidesWrapper.style.transform = `translateX(-${slideIndex * 100}%)`;
                dots.forEach((dot, idx) => {
                    if(dot) {
                        if(idx === slideIndex) dot.classList.add('active');
                        else dot.classList.remove('active');
                    }
                });
            }

            function currentSlide(n) {
                slideIndex = n;
                showSlides();
            }

            if(totalSlides > 1) {
                setInterval(() => {
                    slideIndex = (slideIndex + 1) % totalSlides;
                    showSlides();
                }, 4000);
            }

            function updateCartCount() {
                let cart = JSON.parse(localStorage.getItem('sky_cart') || '[]');
                let totalQty = cart.reduce((sum, item) => sum + parseInt(item.qty || 0), 0);
                let countEl = document.getElementById('cart-count');
                if(countEl) countEl.innerText = totalQty;
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
    db = get_db_safe()
    try: item_id = int(request.args.get("id"))
    except: return redirect("/")
        
    selected_item = next((item for item in db["menu"] if item["id"] == item_id), None)
    if not selected_item: return redirect("/")
        
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{{ item.name }} - Sky Lounge Cafe</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-black/85 text-white min-h-screen flex items-center justify-center p-4">
        <div class="bg-gray-900 border border-yellow-500/30 rounded-3xl shadow-2xl max-w-md w-full overflow-hidden relative">
            <a href="/" class="absolute top-4 right-4 bg-red-600 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold shadow z-10">✕</a>
            
            <img src="{{ item.image }}" alt="{{ item.name }}" class="w-full h-56 object-cover">
            
            <div class="p-6">
                <h2 class="text-2xl font-black text-yellow-400 mb-1">{{ item.name }}</h2>
                <p class="text-gray-300 text-xs mb-4 leading-relaxed">{{ item.get('desc', 'Delicious item') }}</p>
                
                <div class="space-y-4 mb-6">
                    {% if item.category == 'Pizza' %}
                    <div>
                        <label class="block text-xs text-yellow-300 mb-1 font-bold">SELECT SIZE</label>
                        <select id="pizza-size" onchange="updatePizzaPrice()" class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-white font-bold text-sm">
                            <option value="Small (S)" data-price="{{ item.get('price_s', 0) }}">Small (S) - Rs. {{ item.get('price_s', 0) }}</option>
                            <option value="Medium (M)" data-price="{{ item.get('price_m', item.get('price', 0)) }}" selected>Medium (M) - Rs. {{ item.get('price_m', item.get('price', 0)) }}</option>
                            <option value="Large (L)" data-price="{{ item.get('price_l', 0) }}">Large (L) - Rs. {{ item.get('price_l', 0) }}</option>
                        </select>
                    </div>
                    <p class="text-red-500 font-black text-2xl" id="display-price">Rs. {{ item.get('price_m', item.get('price', 0)) }}</p>

                    {% elif item.category == 'Starters' %}
                    <div>
                        <label class="block text-xs text-yellow-300 mb-1 font-bold">SELECT PORTION</label>
                        <select id="starter-pc" onchange="updateStarterPrice()" class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-white font-bold text-sm">
                            <option value="5 Pieces" data-price="{{ item.get('price_5pc', 0) }}">5 Pieces - Rs. {{ item.get('price_5pc', 0) }}</option>
                            <option value="10 Pieces" data-price="{{ item.get('price_10pc', 0) }}">10 Pieces - Rs. {{ item.get('price_10pc', 0) }}</option>
                        </select>
                    </div>
                    <p class="text-red-500 font-black text-2xl" id="display-price">Rs. {{ item.get('price_5pc', 0) }}</p>

                    {% else %}
                    <p class="text-red-500 font-black text-2xl">Rs. {{ item.get('price', 0) }}</p>
                    {% endif %}

                    <div>
                        <label class="block text-xs text-yellow-300 mb-1 font-bold">QUANTITY</label>
                        <div class="flex items-center space-x-3">
                            <button type="button" onclick="decreaseQty()" class="bg-gray-800 text-white w-10 h-10 rounded-xl font-bold text-lg">-</button>
                            <input type="number" id="qty" value="1" min="1" max="10" readonly class="w-16 text-center bg-gray-800 border border-gray-700 rounded-xl py-2 text-white font-bold text-lg">
                            <button type="button" onclick="increaseQty()" class="bg-gray-800 text-white w-10 h-10 rounded-xl font-bold text-lg">+</button>
                        </div>
                    </div>
                </div>
                
                <button onclick="addToCart()" class="w-full bg-red-600 hover:bg-red-500 text-white font-black py-3.5 rounded-xl shadow transition text-sm tracking-wider">
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
                if(parseInt(input.value) < 10) input.value = parseInt(input.value) + 1;
            }
            function decreaseQty() {
                let input = document.getElementById('qty');
                if(parseInt(input.value) > 1) input.value = parseInt(input.value) - 1;
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
        <title>Your Bucket - Sky Lounge Cafe</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white min-h-screen p-4 font-sans flex items-center justify-center">
        <div class="max-w-lg w-full bg-gray-900 border border-gray-800 p-6 rounded-3xl shadow-2xl">
            <h2 class="text-2xl font-black text-yellow-400 mb-4 text-center">🛒 YOUR FOOD BUCKET</h2>
            
            <div id="cart-container"></div>

            <div id="checkout-form-section" style="display:none;" class="mt-4 border-t border-gray-800 pt-4">
                <form onsubmit="submitOrder(event)" class="space-y-3">
                    <div>
                        <label class="block text-xs text-yellow-300 mb-1 font-semibold">Your Full Name</label>
                        <input type="text" id="c_name" placeholder="e.g. Asad Ali" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-white text-sm">
                    </div>
                    <div>
                        <label class="block text-xs text-yellow-300 mb-1 font-semibold">Phone Number</label>
                        <input type="text" id="c_phone" placeholder="e.g. 03093478600" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-white text-sm">
                    </div>
                    <div>
                        <label class="block text-xs text-yellow-300 mb-1 font-semibold">Delivery Address</label>
                        <textarea id="c_address" placeholder="House #, Street, Area..." required rows="2" class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-white text-sm"></textarea>
                    </div>
                    
                    <button type="submit" class="w-full bg-green-600 hover:bg-green-500 text-white font-black py-3.5 rounded-xl shadow transition text-sm">PLACE FINAL ORDER</button>
                </form>
            </div>
            
            <div class="text-center mt-4">
                <a href="/" class="text-xs text-yellow-400 hover:underline font-semibold">← Back to Menu</a>
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
                let html = '<div class="space-y-3 mb-4 max-h-48 overflow-y-auto">';
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
                                <span class="text-yellow-400 font-bold">Rs. ${subtotal}</span>
                                <button type="button" onclick="removeItem(${index})" class="text-red-500 text-xs font-bold bg-gray-700 w-7 h-7 rounded-lg flex items-center justify-center">✕</button>
                            </div>
                        </div>
                    `;
                });

                html += `</div>
                    <div class="border-t border-gray-800 pt-3 flex justify-between text-lg font-black">
                        <span>Total:</span>
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

# --- 4. SAVE ORDER ROUTE ---
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

# --- 5. ORDER SUCCESS & WHATSAPP MESSAGE ---
@app.route("/order-success")
def order_success():
    import urllib.parse
    import json
    c_name = request.args.get("name")
    total_amount = request.args.get("total")
    c_address = request.args.get("address")
    c_phone = request.args.get("phone")
    
    try: cart_items = json.loads(request.args.get("items", "[]"))
    except: cart_items = []

    ui_items_html = ""
    for item in cart_items:
        sub = float(item['price']) * int(item['qty'])
        var_text = f" ({item['variant']})" if item.get('variant') else ""
        ui_items_html += f"<p class='text-gray-200 border-b border-gray-700/50 pb-1 text-xs'>• <strong>{item['qty']}x</strong> {item['name']}{var_text} — <span class='text-yellow-400'>Rs. {sub}</span></p>"

    wa_message = f"🍔 *NEW ORDER - SKY LOUNGE CAFE* 🍔\n📍 *Cinema Mor, Kasur*\n\n👤 *Customer Name:* {c_name}\n📞 *Phone:* {c_phone}\n🏠 *Address:* {c_address}\n\n🛒 *Ordered Items:*\n"
    for item in cart_items:
        sub = float(item['price']) * int(item['qty'])
        var_text = f" ({item['variant']})" if item.get('variant') else ""
        wa_message += f"▪ {item['qty']}x {item['name']}{var_text} - Rs.{sub}\n"
    wa_message += f"\n💰 *Total Amount:* Rs. {total_amount}\n\n_Please confirm and dispatch order quickly!_"
    
    encoded_wa_msg = urllib.parse.quote(wa_message)
    
    success_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Order Confirmed - Sky Lounge Cafe</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white flex items-center justify-center min-h-screen p-4">
        <div class="bg-gray-900 border border-yellow-500/40 p-6 rounded-3xl shadow-2xl max-w-md w-full text-center">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-yellow-400/10 border border-yellow-400 rounded-full text-yellow-400 text-2xl mb-3">👑</div>
            <h1 class="text-2xl font-black text-yellow-400 mb-1">ORDER CONFIRMED!</h1>
            <p class="text-red-400 text-xs font-semibold mb-4">Sky Lounge Cafe • Kasur</p>
            
            <div class="bg-gray-800 p-4 rounded-2xl text-left space-y-2 mb-5 text-xs">
                <p class="text-gray-300"><strong>Customer:</strong> {c_name}</p>
                <p class="text-gray-300"><strong>Phone:</strong> {c_phone}</p>
                <p class="text-gray-300"><strong>Address:</strong> {c_address}</p>
                <div class="border-t border-gray-700 pt-2 mt-2 space-y-1">
                    <p class="text-yellow-300 font-bold mb-1">Items:</p>
                    {ui_items_html}
                </div>
                <div class="border-t border-gray-700 pt-2 flex justify-between font-black text-sm mt-2">
                    <span>Total:</span>
                    <span class="text-green-400">Rs. {total_amount}</span>
                </div>
            </div>

            <a href="https://wa.me/923093478600?text={encoded_wa_msg}" target="_blank" class="block w-full bg-green-600 hover:bg-green-500 text-white font-black py-3 rounded-xl transition mb-2.5 shadow text-sm">💬 Send Order via WhatsApp</a>
            <a href="/" class="block w-full bg-gray-800 hover:bg-gray-700 text-gray-300 font-bold py-2.5 rounded-xl transition text-xs">← Back to Menu</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(success_html)

# --- 6. ADMIN PANEL (WITH DIRECT UPLOAD FEATURE RESTORED) ---
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == "asad123":
            session["logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Galat Password!"
            
    login_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Admin Login - Sky Lounge Cafe</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white flex items-center justify-center h-screen p-4">
        <div class="bg-gray-900 border border-gray-800 p-8 rounded-2xl shadow-2xl max-w-sm w-full text-center">
            <h2 class="text-2xl font-black text-yellow-400 mb-2">🔒 Admin Login</h2>
            <form action="/admin" method="POST" class="space-y-4 mt-4">
                <input type="password" name="password" placeholder="Enter Password" required class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white text-center tracking-widest text-sm">
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
    if not session.get("logged_in"): return redirect(url_for("admin_login"))
    db = get_db_safe()
    total_revenue = sum(order["price"] for order in db["orders"])
    total_orders = len(db["orders"])
    
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Sky Lounge Cafe - Admin Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-white min-h-screen p-4 md:p-6">
        <div class="max-w-6xl mx-auto">
            <header class="flex justify-between items-center mb-6 border-b border-gray-800 pb-4">
                <h1 class="text-xl md:text-2xl font-bold text-yellow-400">✨ Admin Dashboard</h1>
                <a href="/admin/logout" class="bg-red-600 text-white px-3 py-1.5 rounded-lg font-semibold text-xs">Logout</a>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div class="bg-gray-800 p-4 rounded-xl border border-gray-700"><p class="text-gray-400 text-xs">Total Orders</p><h3 class="text-2xl font-bold text-yellow-400">{{ total_orders }}</h3></div>
                <div class="bg-gray-800 p-4 rounded-xl border border-gray-700"><p class="text-gray-400 text-xs">Total Revenue</p><h3 class="text-2xl font-bold text-green-400">Rs. {{ total_revenue }}</h3></div>
                <div class="bg-gray-800 p-4 rounded-xl border border-gray-700"><p class="text-gray-400 text-xs">Menu Items</p><h3 class="text-2xl font-bold text-blue-400">{{ menu|length }}</h3></div>
            </div>

            <div class="bg-gray-800 p-4 rounded-xl border border-gray-700 mb-6">
                <h2 class="text-lg font-semibold mb-3 text-yellow-300">🖼️ Upload Slider Images (Direct from Device)</h2>
                <form action="/admin/add-slider" method="POST" enctype="multipart/form-data" class="flex flex-col sm:flex-row gap-2 mb-4">
                    <input type="file" name="image_file" accept="image/*" required class="flex-1 bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-xs file:mr-4 file:py-1 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-yellow-500 file:text-gray-950 hover:file:bg-yellow-400">
                    <button type="submit" class="bg-yellow-500 hover:bg-yellow-400 text-gray-950 font-bold px-4 py-2 rounded-lg text-xs">Upload Slide</button>
                </form>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 max-h-48 overflow-y-auto">
                    {% for slide in sliders %}
                    <div class="bg-gray-700 p-2 rounded-lg border border-gray-600 flex flex-col gap-2">
                        <img src="{{ slide.image }}" class="w-full h-24 object-cover rounded">
                        <form action="/admin/delete-slider/{{ slide.id }}" method="POST">
                            <button type="submit" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-1 rounded text-[10px]">Delete Slide</button>
                        </form>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-gray-800 p-4 rounded-xl border border-gray-700">
                    <h2 class="text-lg font-semibold mb-3 text-yellow-300">📦 Live Orders</h2>
                    {% if orders %}
                        <div class="space-y-3 max-h-[400px] overflow-y-auto">
                            {% for order in orders %}
                            <div class="bg-gray-700 p-3 rounded-lg border border-gray-600 text-xs">
                                <div class="flex justify-between items-center mb-1"><h4 class="font-bold text-yellow-400">Items:</h4><span class="bg-green-500 text-gray-900 px-2 py-0.5 rounded font-bold">Rs. {{ order.price }}</span></div>
                                <p class="text-gray-200 bg-gray-800 p-2 rounded mb-2">{{ order.item }}</p>
                                <div class="text-gray-300 space-y-0.5 border-t border-gray-600 pt-1">
                                    <p><strong>Name:</strong> {{ order.name }}</p>
                                    <p><strong>Phone:</strong> <a href="tel:{{ order.phone }}" class="text-blue-400 underline">{{ order.phone }}</a></p>
                                    <p><strong>Address:</strong> {{ order.address }}</p>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    {% else %}<p class="text-gray-400 text-xs">No pending orders.</p>{% endif %}
                </div>

                <div class="bg-gray-800 p-4 rounded-xl border border-gray-700">
                    <h2 class="text-lg font-semibold mb-3 text-yellow-300">➕ Add Menu Item (Direct Image Upload)</h2>
                    <form action="/admin/add-item" method="POST" enctype="multipart/form-data" class="space-y-2 mb-4">
                        <select name="category" id="cat-select" onchange="toggleCategoryFields()" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-xs">
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
                        <input type="text" name="name" placeholder="Item Name" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-xs">
                        
                        <div id="price-normal-box"><input type="number" name="price" placeholder="Price (e.g. 450)" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-xs"></div>
                        <div id="price-pizza-box" style="display:none;" class="space-y-2">
                            <input type="number" name="price_s" placeholder="Small Size Price (S)" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-xs">
                            <input type="number" name="price_m" placeholder="Medium Size Price (M)" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-xs">
                            <input type="number" name="price_l" placeholder="Large Size Price (L)" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-xs">
                        </div>
                        <div id="price-starter-box" style="display:none;" class="space-y-2">
                            <input type="number" name="price_5pc" placeholder="5 Pieces Price (5pc)" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-xs">
                            <input type="number" name="price_10pc" placeholder="10 Pieces Price (10pc)" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-xs">
                        </div>

                        <div>
                            <label class="block text-[10px] text-gray-400 mb-1">Select Item Image File:</label>
                            <input type="file" name="image_file" accept="image/*" required class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-xs file:mr-4 file:py-1 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-green-600 file:text-white hover:file:bg-green-500">
                        </div>
                        <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-lg text-xs">Add Item</button>
                    </form>

                    <h3 class="text-sm font-semibold mb-2 text-gray-300">📋 Current Menu</h3>
                    <div class="space-y-1.5 max-h-40 overflow-y-auto">
                        {% for item in menu %}
                        <div class="flex justify-between items-center bg-gray-700 p-2 rounded-lg text-xs">
                            <div><span class="font-bold text-yellow-300">[{{ item.category }}]</span> {{ item.name }}</div>
                            <form action="/admin/delete-item/{{ item.id }}" method="POST"><button type="submit" class="bg-red-600 text-white px-2 py-0.5 rounded text-[10px]">Delete</button></form>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
        <script>
            function toggleCategoryFields() {
                let cat = document.getElementById('cat-select').value;
                document.getElementById('price-normal-box').style.display = (cat === 'Pizza' || cat === 'Starters') ? 'none' : 'block';
                document.getElementById('price-pizza-box').style.display = (cat === 'Pizza') ? 'block' : 'none';
                document.getElementById('price-starter-box').style.display = (cat === 'Starters') ? 'block' : 'none';
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_code, menu=db["menu"], sliders=db.get("sliders", []), orders=db["orders"], total_orders=total_orders, total_revenue=total_revenue)

@app.route("/admin/add-slider", methods=["POST"])
def add_slider():
    if not session.get("logged_in"): return redirect(url_for("admin_login"))
    
    file = request.files.get("image_file")
    if file and file.filename != '':
        img_bytes = file.read()
        encoded_img = base64.b64encode(img_bytes).decode('utf-8')
        img_url = f"data:image/jpeg;base64,{encoded_img}"
        
        db = get_db_safe()
        sliders = db.get("sliders", [])
        new_id = (max([s["id"] for s in sliders]) + 1) if sliders else 1
        sliders.append({"id": new_id, "image": img_url})
        db["sliders"] = sliders
        save_data(db)
        
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete-slider/<int:slide_id>", methods=["POST"])
def delete_slider(slide_id):
    if not session.get("logged_in"): return redirect(url_for("admin_login"))
    db = get_db_safe()
    db["sliders"] = [s for s in db.get("sliders", []) if s["id"] != slide_id]
    save_data(db)
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/add-item", methods=["POST"])
def add_item():
    if not session.get("logged_in"): return redirect(url_for("admin_login"))
    category = request.form.get("category", "Others")
    
    img_url = "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=500"
    file = request.files.get("image_file")
    if file and file.filename != '':
        img_bytes = file.read()
        encoded_img = base64.b64encode(img_bytes).decode('utf-8')
        img_url = f"data:image/jpeg;base64,{encoded_img}"

    db = get_db_safe()
    new_id = (max([m["id"] for m in db["menu"]]) + 1) if db["menu"] else 1
    
    newItem = {"id": new_id, "category": category, "name": request.form.get("name"), "desc": "Delicious freshly prepared meal.", "image": img_url}

    if category == 'Pizza':
        newItem["price_s"] = float(request.form.get("price_s") or 0)
        newItem["price_m"] = float(request.form.get("price_m") or 0)
        newItem["price_l"] = float(request.form.get("price_l") or 0)
        newItem["price"] = newItem["price_m"]
    elif category == 'Starters':
        newItem["price_5pc"] = float(request.form.get("price_5pc") or 0)
        newItem["price_10pc"] = float(request.form.get("price_10pc") or 0)
        newItem["price"] = newItem["price_5pc"]
    else:
        newItem["price"] = float(request.form.get("price") or 0)

    db["menu"].append(newItem)
    save_data(db)
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete-item/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    if not session.get("logged_in"): return redirect(url_for("admin_login"))
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