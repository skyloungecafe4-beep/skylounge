from flask import Flask, redirect, render_template_string, request, session, url_for
import os
from database import load_data, save_data

app = Flask(__name__)
app.secret_key = "sky_lounge_vip_slider_key"

# --- DEFAULT DATA BACKUP ---
DEFAULT_MENU = [
    {"id": 1, "category": "Burgers", "name": "Zinger Burger", "price": 450, "desc": "Crispy chicken fillet with special sauce.", "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=500"},
    {"id": 2, "category": "Pizza", "name": "Chicken Supreme (M)", "price_s": 800, "price_m": 1300, "price_l": 1900, "price": 1300, "category": "Pizza", "desc": "Loaded with chicken, mushrooms, and olives.", "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=500"},
    {"id": 3, "category": "Starters", "name": "Hot Crispy Wings (5pc)", "price_5pc": 450, "price_10pc": 850, "price": 450, "desc": "Spicy and crunchy chicken wings.", "image": "https://images.unsplash.com/photo-1527477396000-e27163b481c2?q=80&w=500"}
]

def get_db_safe():
    db = load_data()
    if not db.get("menu"):
        db["menu"] = DEFAULT_MENU
        save_data(db)
    return db

# --- 1. CUSTOMER PORTAL (VIP Slider & Slide-in Menu) ---
@app.route("/")
def customer_portal():
    db = get_db_safe()
    
    categories = {}
    for item in db["menu"]:
        cat = item.get("category", "Others")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    slider_images = [
        "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?q=80&w=1920",
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1920",
        "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?q=80&w=1920"
    ]

    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sky Lounge VIP - Kasur</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .slider-container { position: relative; overflow: hidden; width: 100%; height: 350px; }
            .slider-wrapper { display: flex; transition: transform 0.5s ease-in-out; height: 100%; }
            .slide { min-width: 100%; height: 100%; }
            .slide img { width: 100%; height: 100%; object-fit: cover; }
            .slider-nav { position: absolute; bottom: 15px; left: 50%; transform: translateX(-50%); display: flex; gap: 8px; z-index: 10; }
            .nav-dot { width: 10px; height: 10px; background: rgba(255, 255, 255, 0.5); border-radius: 50%; cursor: pointer; }
            .nav-dot.active { background: #fff; }
        </style>
    </head>
    <body class="bg-gray-950 text-white min-h-screen font-sans">
        
        <header class="shadow-2xl border-b border-red-800 relative">
            <div class="bg-black/60 absolute inset-0 z-10"></div>
            <div class="slider-container z-0">
                <div class="slider-wrapper" id="slider-wrapper">
                    {% for img in slider_images %}
                    <div class="slide"><img src="{{ img }}" alt="Restaurant view"></div>
                    {% endfor %}
                </div>
                <div class="slider-nav">
                    {% for img in slider_images %}
                    <span class="nav-dot" onclick="currentSlide({{ loop.index0 }})"></span>
                    {% endfor %}
                </div>
            </div>
            <div class="absolute inset-0 z-20 flex flex-col items-center justify-center p-6 text-center">
                <h1 class="text-6xl md:text-8xl font-black tracking-widest text-yellow-400 drop-shadow-2xl">SKY LOUNGE</h1>
                <p class="text-yellow-200 text-sm md:text-base mt-2 font-semibold tracking-wider">📍 Cinema Mor, Opp PSO Petrol Pump, Kasur</p>
                <p class="text-white text-sm md:text-base mt-1 font-medium bg-red-600 px-3 py-1 rounded-full shadow-lg">TASTE THE LUXURY • ORDER FRESH & HOT</p>
            </div>
        </header>

        <div class="bg-red-600 sticky top-0 z-40 shadow-xl py-3 px-6 flex justify-between items-center max-w-7xl mx-auto md:rounded-b-xl border-b-2 border-yellow-400">
            <span class="font-black text-lg flex items-center gap-3 text-white">🛒 YOUR BUCKET</span>
            <a href="/cart" class="bg-yellow-400 hover:bg-yellow-300 text-gray-950 px-6 py-2.5 rounded-xl font-black text-sm transition shadow-2xl transform hover:scale-105 flex items-center gap-2">
                VIEW BUCKET (<span id="cart-count">0</span>)
            </a>
        </div>

        <main class="max-w-7xl mx-auto p-6 space-y-12 mb-24">
            
            <nav class="flex gap-3 overflow-x-auto pb-3">
                {% for cat_name in categories.keys() %}
                <a href="#cat-{{ cat_name }}" class="bg-gray-900 hover:bg-gray-800 text-white px-5 py-2 rounded-full text-sm font-semibold whitespace-nowrap border border-gray-700 shadow">{{ cat_name }}</a>
                {% endfor %}
            </nav>

            {% for cat_name, items in categories.items() %}
            <section id="cat-{{ cat_name }}">
                <div class="border-b-2 border-red-700 pb-2 mb-8">
                    <h2 class="text-4xl font-black tracking-wider text-yellow-400 uppercase">{{ cat_name }}</h2>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                    {% for item in items %}
                    <div class="bg-gray-900 rounded-2xl overflow-hidden border border-gray-700 shadow-2xl flex flex-col justify-between transform hover:-translate-y-2 hover:border-yellow-500 transition-all duration-300 group">
                        <div>
                            <img src="{{ item.image }}" alt="{{ item.name }}" class="w-full h-52 object-cover group-hover:scale-105 transition-transform duration-500">
                            <div class="p-5">
                                <h3 class="text-xl font-bold text-white group-hover:text-yellow-400 transition">{{ item.name }}</h3>
                                <p class="text-gray-400 text-xs mt-1.5 leading-relaxed line-clamp-2">{{ item.get('desc', 'Delicious item') }}</p>
                                <p class="text-red-500 font-extrabold text-2xl mt-3">
                                    {% if item.category == 'Pizza' %}
                                        From Rs. {{ item.get('price_s', 0) }}
                                    {% elif item.category == 'Starters' %}
                                        Rs. {{ item.get('price_5pc', 0) }} (5pc)
                                    {% else %}
                                        Rs. {{ item.get('price', 0) }}
                                    {% endif %}
                                </p>
                            </div>
                        </div>
                        
                        <div class="p-5 pt-0">
                            <a href="/item-detail?id={{ item.id }}" class="block text-center bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white font-black py-3.5 rounded-xl shadow-lg transition text-sm tracking-wider">ORDER NOW</a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </section>
            {% endfor %}
        </main>

        <div class="fixed bottom-6 right-6 z-50">
            <a href="https://wa.me/923093478600?text=Hello%20Sky%20Lounge,%20I%20want%20to%20ask%20something%20about%20menu." target="_blank" class="bg-green-600 hover:bg-green-500 text-white px-6 py-4 rounded-full shadow-2xl font-bold flex items-center gap-3 transition transform hover:scale-105 border-2 border-white/30">
                <span class="text-2xl">💬</span>
                <span class="text-sm tracking-wide font-black">LIVE CHAT</span>
            </a>
        </div>

        <script>
            let slideIndex = 0;
            const slides = document.getElementById('slider-wrapper');
            const dots = document.querySelectorAll('.nav-dot');

            function showSlides() {
                if(!slides) return;
                slides.style.transform = `translateX(-${slideIndex * 100}%)`;
                dots.forEach(dot => dot.classList.remove('active'));
                if(dots[slideIndex]) dots[slideIndex].classList.add('active');
            }

            function currentSlide(n) {
                slideIndex = n;
                showSlides();
            }

            setInterval(() => {
                if(slides && slides.children.length > 0) {
                    slideIndex = (slideIndex + 1) % slides.children.length;
                    showSlides();
                }
            }, 5000);
            showSlides();

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
    return render_template_string(html_code, categories=categories, slider_images=slider_images)

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
        <title>{{ item.name }} - Sky Lounge VIP</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-black/80 text-white min-h-screen flex items-center justify-center p-4">
        <div class="bg-gray-900 border-2 border-yellow-500/20 rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden relative">
            <a href="/" class="absolute top-5 right-5 bg-red-600 hover:bg-red-500 text-white w-10 h-10 rounded-full flex items-center justify-center font-black shadow z-10 border-2 border-white/30">✕</a>
            
            <img src="{{ item.image }}" alt="{{ item.name }}" class="w-full h-64 object-cover">
            
            <div class="p-8">
                <h2 class="text-4xl font-black text-yellow-400 mb-2 tracking-wide">{{ item.name }}</h2>
                <p class="text-gray-300 text-sm mb-6 leading-relaxed">{{ item.get('desc', 'Delicious item') }}</p>
                
                <div class="space-y-5 mb-8">
                    {% if item.category == 'Pizza' %}
                    <div>
                        <label class="block text-sm text-yellow-300 mb-2 font-bold tracking-wider">SELECT SIZE</label>
                        <select id="pizza-size" onchange="updatePizzaPrice()" class="w-full bg-gray-800 border border-gray-700 rounded-xl p-4 text-white font-black text-lg">
                            <option value="Small (S)" data-price="{{ item.get('price_s', 0) }}">Small (S) - Rs. {{ item.get('price_s', 0) }}</option>
                            <option value="Medium (M)" data-price="{{ item.get('price_m', item.get('price', 0)) }}" selected>Medium (M) - Rs. {{ item.get('price_m', item.get('price', 0)) }}</option>
                            <option value="Large (L)" data-price="{{ item.get('price_l', 0) }}">Large (L) - Rs. {{ item.get('price_l', 0) }}</option>
                        </select>
                    </div>
                    <p class="text-red-500 font-black text-4xl" id="display-price">Rs. {{ item.get('price_m', item.get('price', 0)) }}</p>

                    {% elif item.category == 'Starters' %}
                    <div>
                        <label class="block text-sm text-yellow-300 mb-2 font-bold tracking-wider">SELECT PORTION</label>
                        <select id="starter-pc" onchange="updateStarterPrice()" class="w-full bg-gray-800 border border-gray-700 rounded-xl p-4 text-white font-black text-lg">
                            <option value="5 Pieces" data-price="{{ item.get('price_5pc', 0) }}">5 Pieces - Rs. {{ item.get('price_5pc', 0) }}</option>
                            <option value="10 Pieces" data-price="{{ item.get('price_10pc', 0) }}">10 Pieces - Rs. {{ item.get('price_10pc', 0) }}</option>
                        </select>
                    </div>
                    <p class="text-red-500 font-black text-4xl" id="display-price">Rs. {{ item.get('price_5pc', 0) }}</p>

                    {% else %}
                    <p class="text-red-500 font-black text-4xl">Rs. {{ item.get('price', 0) }}</p>
                    {% endif %}

                    <div>
                        <label class="block text-sm text-yellow-300 mb-2 font-bold tracking-wider">QUANTITY</label>
                        <div class="flex items-center space-x-4">
                            <button type="button" onclick="decreaseQty()" class="bg-gray-800 hover:bg-gray-700 text-white w-12 h-12 rounded-xl font-black text-xl">-</button>
                            <input type="number" id="qty" value="1" min="1" max="10" readonly class="w-20 text-center bg-gray-800 border border-gray-700 rounded-xl py-3 text-white font-black text-xl">
                            <button type="button" onclick="increaseQty()" class="bg-gray-800 hover:bg-gray-700 text-white w-12 h-12 rounded-xl font-black text-xl">+</button>
                        </div>
                    </div>
                </div>
                
                <button onclick="addToCart()" class="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white font-black py-4 rounded-2xl shadow-2xl transition flex justify-center items-center gap-3 text-base tracking-wider">
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
        <title>Your Bucket - Sky Lounge VIP</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white min-h-screen p-6 font-sans flex items-center justify-center">
        <div class="max-w-xl w-full bg-gray-900 border border-gray-800 p-8 rounded-3xl shadow-2xl">
            <h2 class="text-3xl font-black text-yellow-400 mb-6 text-center tracking-wide">🛒 YOUR FOOD BUCKET</h2>
            
            <div id="cart-container"></div>

            <div id="checkout-form-section" style="display:none;" class="mt-6 border-t border-gray-800 pt-6">
                <form onsubmit="submitOrder(event)" class="space-y-4">
                    <div>
                        <label class="block text-sm text-yellow-300 mb-1 font-semibold">Your Full Name</label>
                        <input type="text" id="c_name" placeholder="e.g. Asad Ali" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3.5 text-white">
                    </div>
                    <div>
                        <label class="block text-sm text-yellow-300 mb-1 font-semibold">Phone Number</label>
                        <input type="text" id="c_phone" placeholder="e.g. 03093478600" required class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3.5 text-white">
                    </div>
                    <div>
                        <label class="block text-sm text-yellow-300 mb-1 font-semibold">Delivery Address</label>
                        <textarea id="c_address" placeholder="House #, Street, Area..." required rows="2" class="w-full bg-gray-800 border border-gray-700 rounded-xl p-3.5 text-white"></textarea>
                    </div>
                    
                    <button type="submit" class="w-full bg-green-600 hover:bg-green-500 text-white font-black py-4 rounded-xl shadow-xl transition text-base tracking-wider">PLACE FINAL ORDER</button>
                </form>
            </div>
            
            <div class="text-center mt-6">
                <a href="/" class="text-sm text-yellow-400 hover:underline font-semibold">← Add More Items (Back to Menu)</a>
            </div>
        </div>

        <script>
            function loadCart() {
                let cart = JSON.parse(localStorage.getItem('sky_cart') || '[]');
                let container = document.getElementById('cart-container');
                let checkoutSection = document.getElementById('checkout-form-section');

                if (cart.length === 0) {
                    container.innerHTML = '<p class="text-center text-gray-400 py-8 font-medium">Your bucket is empty!</p>';
                    checkoutSection.style.display = 'none';
                    return;
                }

                checkoutSection.style.display = 'block';
                let html = '<div class="space-y-4 mb-6 max-h-64 overflow-y-auto">';
                let totalAmount = 0;

                cart.forEach((item, index) => {
                    let qty = parseInt(item.qty || 1);
                    let price = parseFloat(item.price || 0);
                    let subtotal = price * qty;
                    totalAmount += subtotal;
                    let displayTitle = item.name + (item.variant ? ` (${item.variant})` : '');
                    
                    html += `
                        <div class="bg-gray-800 p-4 rounded-xl flex justify-between items-center border border-gray-700">
                            <div>
                                <h4 class="font-bold text-white text-base">${displayTitle}</h4>
                                <p class="text-xs text-gray-400">Rs. ${price} x ${qty}</p>
                            </div>
                            <div class="flex items-center gap-4">
                                <span class="text-yellow-400 font-black text-lg">Rs. ${subtotal}</span>
                                <button type="button" onclick="removeItem(${index})" class="text-red-500 hover:text-red-400 text-xs font-black bg-gray-700 w-8 h-8 rounded-lg flex items-center justify-center">✕</button>
                            </div>
                        </div>
                    `;
                });

                html += `</div>
                    <div class="border-t border-gray-800 pt-4 flex justify-between text-2xl font-black">
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
        ui_items_html += f"<p class='text-gray-200 border-b border-gray-700/50 pb-1'>• <strong>{item['qty']}x</strong> {item['name']}{var_text} — <span class='text-yellow-400'>Rs. {sub}</span></p>"

    wa_message = f"🍔 *NEW ORDER - SKY LOUNGE* 🍔\n📍 *Cinema Mor, Kasur*\n\n👤 *Customer Name:* {c_name}\n📞 *Phone:* {c_phone}\n🏠 *Address:* {c_address}\n\n🛒 *Ordered Items:*\n"
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
        <title>VIP Order Confirmed - Sky Lounge</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white flex items-center justify-center min-h-screen p-4">
        <div class="bg-gradient-to-b from-gray-900 to-black border-2 border-yellow-500/50 p-8 rounded-3xl shadow-2xl max-w-lg w-full text-center relative">
            <div class="inline-flex items-center justify-center w-20 h-20 bg-yellow-400/10 border border-yellow-400 rounded-full text-yellow-400 text-4xl mb-4">👑</div>
            <h1 class="text-3xl font-black text-yellow-400 tracking-wider mb-1">VIP ORDER CONFIRMED!</h1>
            <p class="text-red-400 text-sm font-semibold uppercase tracking-widest mb-6">Sky Lounge • Cinema Mor, Kasur</p>
            
            <div class="bg-gray-800/80 border border-gray-700 p-5 rounded-2xl text-left space-y-2 mb-6 text-sm">
                <p class="text-gray-300"><strong>Customer:</strong> {c_name}</p>
                <p class="text-gray-300"><strong>Phone:</strong> {c_phone}</p>
                <p class="text-gray-300"><strong>Delivery Address:</strong> {c_address}</p>
                <div class="border-t border-gray-700 pt-2 mt-2 space-y-1.5">
                    <p class="text-yellow-300 font-bold mb-1">Ordered Items:</p>
                    {ui_items_html}
                </div>
                <div class="border-t border-gray-700 pt-2 flex justify-between items-center text-base font-black mt-3">
                    <span class="text-white">Total Amount:</span>
                    <span class="text-green-400 text-lg">Rs. {total_amount}</span>
                </div>
            </div>

            <a href="https://wa.me/923093478600?text={encoded_wa_msg}" target="_blank" class="block w-full bg-green-600 hover:bg-green-500 text-white font-black py-4 rounded-xl transition mb-3 shadow-lg text-base">💬 Send Order via WhatsApp (VIP)</a>
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
        <title>Admin Login - Sky Lounge</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white flex items-center justify-center h-screen p-4">
        <div class="bg-gray-900 border border-gray-800 p-8 rounded-2xl shadow-2xl max-w-sm w-full text-center">
            <h2 class="text-2xl font-black text-yellow-400 mb-2">🔒 Admin Login</h2>
            <form action="/admin" method="POST" class="space-y-4 mt-4">
                <input type="password" name="password" placeholder="Enter Password" required class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white text-center tracking-widest">
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
    if not session.get("logged_in"): return redirect(url_for("admin_login"))
    db = get_db_safe()
    total_revenue = sum(order["price"] for order in db["orders"])
    total_orders = len(db["orders"])
    
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Sky Lounge - Admin Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-white min-h-screen p-6">
        <div class="max-w-6xl mx-auto">
            <header class="flex justify-between items-center mb-8 border-b border-gray-700 pb-4">
                <h1 class="text-3xl font-bold text-yellow-400">✨ Sky Lounge Admin Dashboard</h1>
                <a href="/admin/logout" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-semibold text-sm">Logout</a>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="bg-gray-800 p-6 rounded-xl border border-gray-700"><p class="text-gray-400">Total Live Orders</p><h3 class="text-3xl font-bold text-yellow-400">{{ total_orders }}</h3></div>
                <div class="bg-gray-800 p-6 rounded-xl border border-gray-700"><p class="text-gray-400">Total Revenue</p><h3 class="text-3xl font-bold text-green-400">Rs. {{ total_revenue }}</h3></div>
                <div class="bg-gray-800 p-6 rounded-xl border border-gray-700"><p class="text-gray-400">Active Menu Items</p><h3 class="text-3xl font-bold text-blue-400">{{ menu|length }}</h3></div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="bg-gray-800 p-6 rounded-xl border border-gray-700">
                    <h2 class="text-xl font-semibold mb-4 text-yellow-300">📦 Live Bucket Orders</h2>
                    {% if orders %}
                        <div class="space-y-4 max-h-[450px] overflow-y-auto">
                            {% for order in orders %}
                            <div class="bg-gray-700 p-4 rounded-lg border border-gray-600">
                                <div class="flex justify-between items-center mb-2"><h4 class="font-bold text-md text-yellow-400">Order Items:</h4><span class="bg-green-500 text-gray-900 text-xs px-2.5 py-1 rounded-full font-bold">Rs. {{ order.price }}</span></div>
                                <p class="text-sm text-gray-200 bg-gray-800 p-2.5 rounded mb-3">{{ order.item }}</p>
                                <div class="text-sm text-gray-300 space-y-1 border-t border-gray-600 pt-2">
                                    <p><strong>Name:</strong> {{ order.name }}</p>
                                    <p><strong>Phone:</strong> <a href="tel:{{ order.phone }}" class="text-blue-400 underline">{{ order.phone }}</a></p>
                                    <p><strong>Address:</strong> {{ order.address }}</p>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    {% else %}<p class="text-gray-400">No pending orders right now.</p>{% endif %}
                </div>

                <div class="bg-gray-800 p-6 rounded-xl border border-gray-700">
                    <h2 class="text-xl font-semibold mb-4 text-yellow-300">➕ Add New Menu Item</h2>
                    <form action="/admin/add-item" method="POST" class="space-y-3 mb-6">
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
                        
                        <div id="price-normal-box"><input type="number" name="price" placeholder="Price (e.g. 450)" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white text-sm"></div>
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
                        <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-lg text-sm">Add Item to Menu</button>
                    </form>

                    <h3 class="text-lg font-semibold mb-3 text-gray-300">📋 Current Menu</h3>
                    <div class="space-y-2 max-h-56 overflow-y-auto">
                        {% for item in menu %}
                        <div class="flex justify-between items-center bg-gray-700 p-3 rounded-lg text-sm">
                            <div><span class="font-bold text-yellow-300">[{{ item.category }}]</span> {{ item.name }}</div>
                            <form action="/admin/delete-item/{{ item.id }}" method="POST"><button type="submit" class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs font-semibold">Delete</button></form>
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
    return render_template_string(html_code, menu=db["menu"], orders=db["orders"], total_orders=total_orders, total_revenue=total_revenue)

@app.route("/admin/add-item", methods=["POST"])
def add_item():
    if not session.get("logged_in"): return redirect(url_for("admin_login"))
    category = request.form.get("category", "Others")
    db = get_db_safe()
    new_id = (max([m["id"] for m in db["menu"]]) + 1) if db["menu"] else 1
    
    newItem = {"id": new_id, "category": category, "name": request.form.get("name"), "desc": "Delicious freshly prepared meal.", "image": request.form.get("image")}

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