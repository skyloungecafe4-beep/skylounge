from flask import Flask, redirect, render_template_string, request, session, url_for
import os
import base64
from database import load_data, save_data

app = Flask(__name__)
app.secret_key = "sky_lounge_vip_slider_key_v12"

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
    if not isinstance(db, dict):
        db = {}
    if "menu" not in db or not db["menu"]:
        db["menu"] = DEFAULT_MENU
    if "sliders" not in db or not db["sliders"] or len(db["sliders"]) == 0:
        db["sliders"] = DEFAULT_SLIDERS
    if "orders" not in db:
        db["orders"] = []
    save_data(db)
    return db

# --- 1. CUSTOMER PORTAL ---
@app.route("/")
def customer_portal():
    db = get_db_safe()
    
    categories = {}
    for item in db.get("menu", DEFAULT_MENU):
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
            @media(min-width: 768px) { .slider-container { height: 420px; } }
            .slider-wrapper { display: flex; transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1); height: 100%; width: 100%; }
            .slide { min-width: 100%; height: 100%; flex-shrink: 0; }
            .slide img { width: 100%; height: 100%; object-fit: cover; }
            .slider-nav { position: absolute; bottom: 15px; left: 50%; transform: translateX(-50%); display: flex; gap: 8px; z-index: 10; }
            .nav-dot { width: 10px; height: 10px; background: rgba(255, 255, 255, 0.5); border-radius: 50%; cursor: pointer; transition: all 0.3s; }
            .nav-dot.active { background: #e11d48; width: 25px; border-radius: 5px; }
        </style>
    </head>
    <body class="bg-gray-950 text-white min-h-screen font-sans">
        
        <div class="bg-gray-900 border-b border-gray-800 py-3 px-4 flex justify-between items-center sticky top-0 z-50 shadow-md">
            <div class="flex items-center gap-2">
                <span class="text-sm font-black tracking-widest text-yellow-400 uppercase">⚡ SKY LOUNGE CAFE</span>
            </div>
            <a href="/cart" class="bg-red-600 hover:bg-red-500 text-white px-4 py-1.5 rounded-full font-black text-xs transition shadow flex items-center gap-1.5">
                🛒 BUCKET (<span id="cart-count">0</span>)
            </a>
        </div>

        <div class="max-w-7xl mx-auto px-4 pt-6 pb-2 space-y-4">
            
            <div class="bg-gradient-to-r from-red-950 via-gray-900 to-gray-950 py-6 px-4 text-center rounded-3xl border border-red-900/50 shadow-xl">
                <h1 class="text-3xl md:text-6xl font-black tracking-widest text-yellow-400 uppercase drop-shadow-lg">SKY LOUNGE CAFE</h1>
                <p class="text-gray-200 text-xs md:text-base mt-2 font-bold tracking-wide">📍 Cinema Mor, Opp PSO Petrol Pump, Kasur</p>
            </div>

            <div class="bg-gray-900 rounded-3xl overflow-hidden border border-yellow-500/25 shadow-2xl">
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
    return render_template_string(html_code, categories=categories, slider_list=slider_list)

# --- 2. ITEM DETAIL POPUP ---
@app.route("/item-detail")
def item_detail():
    db = get_db_safe()
    try: item_id = int(request.args.get("id"))
    except: return redirect("/")
        
    selected_item = next((item for item in db.get("menu", []) if item["id"] == item_id), None)
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