from flask import Flask, redirect, render_template_string, request, session, url_for
import os
from database import load_data, save_data
import urllib.parse
import json

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

    # Define slider images (REPLACE THESE WITH YOUR RESTAURANT PICS)
    slider_images = [
        "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?q=80&w=1920", # Restaurant Interior
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1920", # Dining Area
        "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?q=80&w=1920"  # Food Presentation
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
            /* Simple Slider Styles */
            .slider-container { position: relative; overflow: hidden; width: 100%; height: 350px; }
            .slider-wrapper { display: flex; transition: transform 0.5s ease-in-out; height: 100%; }
            .slide { min-width: 100%; height: 100%; }
            .slide img { width: 100%; height: 100%; object-fit: cover; }
            .slider-nav { position: absolute; bottom: 15px; left: 50%; transform: translateX(-50%); display: flex; gap: 8px; z-index: 10; }
            .nav-dot { width: 10px; height: 10px; background: rgba(255, 255, 255, 0.5); border-radius: 50%; cursor: pointer; }
            .nav-dot.active { background: #fff; }

            /* Fade-in animation for sections */
            @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
            section { animation: fadeIn 0.6s ease-out forwards; animation-delay: calc(0.1s * var(--i)); }
        </style>
    </head>
    <body class="bg-gray-950 text-white min-h-font-sans">
        
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
            
            <nav class="flex gap-3 overflow-x-auto pb-3 scrollbar-hide">
                {% for cat_name in categories.keys() %}
                <a href="#cat-{{ cat_name }}" class="bg-gray-900 hover:bg-gray-800 text-white px-5 py-2 rounded-full text-sm font-semibold whitespace-nowrap border border-gray-700 shadow">{{ cat_name }}</a>
                {% endfor %}
            </nav>

            {% for cat_name, items in categories.items() %}
            <section id="cat-{{ cat_name }}" style="--i: {{ loop.index }}">
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
                                <p class="text-gray-400 text-xs mt-1.5 leading-relaxed line-clamp-2">{{ item.desc }}</p>
                                <p class="text-red-500 font-extrabold text-2xl mt-3">
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
            // Slider Logic
            let slideIndex = 0;
            const slides = document.getElementById('slider-wrapper');
            const dots = document.querySelectorAll('.nav-dot');

            function showSlides() {
                slides.style.transform = `translateX(-${slideIndex * 100}%)`;
                dots.forEach(dot => dot.classList.remove('active'));
                dots[slideIndex].classList.add('active');
            }

            function currentSlide(n) {
                slideIndex = n;
                showSlides();
            }

            // Auto slide every 5 seconds
            setInterval(() => {
                slideIndex = (slideIndex + 1) % slides.children.length;
                showSlides();
            }, 5000);
            showSlides(); // Initial call

            // Cart Logic
            function updateCartCount() {
                let cart = JSON.parse(localStorage.getItem('sky_cart') || '[]');
                let totalQty = cart.reduce((sum, item) => sum + parseInt(item.qty || 0), 0);
                let countEl = document.getElementById('cart-count');
                countEl.innerText = totalQty;
            }
            updateCartCount();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_code, categories=categories, slider_images=slider_images)

# --- 2. ITEM DETAIL POPUP (VIP Style) ---
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
        <div class="bg-gray-900 border-2 border-yellow-500/20 rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden relative transform scale-100 transition-transform duration-300">
            <a href="/" class="absolute top-5 right-5 bg-red-600 hover:bg-red-500 text-white w-10 h-10 rounded-full flex items-center justify-center font-black shadow z-10 border-2 border-white/30">✕</a>
            
            <img src="{{ item.image }}" alt="{{ item.name }}" class="w-full h-64 object-cover">
            
            <div class="p-8">
                <h2 class="text-4xl font-black text-yellow-400 mb-2 tracking-wide">{{ item.name }}</h2>
                <p class="text-gray-300 text-sm mb-6 leading-relaxed">{{ item.desc }}</p>
                
                <div class="space-y-5 mb-8">
                    {% if item.category == 'Pizza' %}
                    <div>
                        <label class="block text-sm text-yellow-300 mb-2 font-bold tracking-wider">SELECT SIZE</label>
                        <select id="pizza-size" onchange="updatePizzaPrice()" class="w-full bg-gray-800 border border-gray-700 rounded-xl p-4 text-white font-black text-lg focus:ring-2 focus:ring-yellow-400 focus:border-yellow-400 transition">
                            <option value="Small (S)" data-price="{{ item.price_s }}">Small (S) - Rs. {{ item.price_s }}</option>
                            <option value="Medium (M)" data-price="{{ item.price_m }}" selected>Medium (M) - Rs. {{ item.price_m }}</option>
                            <option value="Large (L)" data-price="{{ item.price_l }}">Large (L) - Rs. {{ item.price_l }}</option>
                        </select>
                    </div>
                    <p class="text-red-500 font-black text-4xl tracking-tight" id="display-price">Rs. {{ item.price_m }}</p>

                    {% elif item.category == 'Starters' %}
                    <div>
                        <label class="block text-sm text-yellow-300 mb-2 font-bold tracking-wider">SELECT PORTION</label>
                        <select id="starter-pc" onchange="updateStarterPrice()" class="w-full