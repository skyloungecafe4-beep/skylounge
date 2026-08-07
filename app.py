from flask import Flask, jsonify, redirect, render_template_string, request, session, url_for
import os

app = Flask(__name__)
app.secret_key = "sky_lounge_final_v3_key"

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
        "image": "