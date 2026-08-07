from flask import Flask, jsonify, redirect, render_template_string, request, session, url_for
import os

app = Flask(__name__)
app.secret_key = "sky_lounge_final_secure_key"

# Café ka Menu
menu_items = [
    {
        "id": 1, 
        "name": "Supreme Pizza", 
        "desc": "Loaded with extra cheese, chicken tikka, mushrooms, and olives.",
        "has_sizes": True, 
        "prices": {"Small": 600, "Medium": 1100, "Large": 1550}, 
        "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=500&q=80"
    },
    {
        "id": 2, 
        "name": "Zinger Burger", 
        "desc": "Crispy chicken fillet with fresh lettuce and our signature mayo sauce.",
        "has_sizes": False, 
        "price": 450, 
        "image": "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=500&q=80"
    },
    {
        "id": 3, 
        "name": "Mighty Zinger", 
        "desc": "Double Zinger fillet with cheese, spicy mayo, and lettuce in a sesame bun.",
        "has_sizes": False, 
        "price": 770, 
        "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=500&q=80"
    },
    {
        "id": 4, 
        "name": "Mint Margarita", 
        "desc": "Refreshing chilled drink made with fresh mint and lime.",
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
        <header class="bg-gradient-to-r