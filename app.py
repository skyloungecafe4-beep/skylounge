from flask import Flask, jsonify, redirect, render_template_string, request, url_for

app = Flask(__name__)

# Café ka Menu aur Orders ki list (Database)
menu_items = [
    {"id": 1, "name": "Lava Burger", "price": 1000},
    {"id": 2, "name": "Zinger Burger", "price": 450},
    {"id": 3, "name": "Supreme Pizza", "price": 1550},
    {"id": 4, "name": "Mint Margarita", "price": 300},
]

live_orders = []  # Yahan customer ke live orders save honge


@app.route("/")
def dashboard():
  total_revenue = sum(order["price"] for order in live_orders)
  return render_template_string(
      """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Sky Lounge - Live Management Dashboard</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            body { background: #0f172a; color: #f8fafc; display: flex; min-height: 100vh; }
            .sidebar { width: 260px; background: #1e293b; padding: 20px; border-right: 1px solid #334155; }
            .sidebar h2 { color: #fbbf24; text-align: center; margin-bottom: 30px; }
            .sidebar a { color: #94a3b8; text-decoration: none; padding: 12px; display: block; border-radius: 8px; margin-bottom: 10px; font-weight: bold; background: #334155; color: white; text-align: center;}
            .main { flex: 1; padding: 30px; overflow-y: auto; }
            .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
            .card { background: #1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155; }
            .card h3 { color: #94a3b8; font-size: 0.9rem; }
            .card .num { font-size: 1.8rem; color: #fbbf24; font-weight: bold; margin-top: 5px; }
            .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .box { background: #1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155; }
            .box h2 { color: #38bdf8; margin-bottom: 15px; font-size: 1.2rem; border-bottom: 1px solid #334155; padding-bottom: 8px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #334155; font-size: 0.95rem; }
            th { color: #94a3b8; }
            .btn { background: #ef4444; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-weight: bold; }
            .btn-green { background: #10b981; }
            input { padding: 8px; width: calc(100% - 20px); margin-bottom: 10px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2>✨ Sky Lounge</h2>
            <a href="/">📊 Admin Dashboard</a>
            <a href="/customer" target="_blank" style="background: #3b82f6;">🌐 Customer Portal</a>
        </div>
        <div class="main">
            <h1 style="margin-bottom: 20px;">Café Management Center</h1>
            
            <div class="stats">
                <div class="card"><h3>Total Live Orders</h3><div class="num">{{ orders|length }}</div></div>
                <div class="card"><h3>Total Revenue</h3><div class="num">Rs. {{ revenue }}</div></div>
                <div class="card"><h3>Active Menu Items</h3><div class="num">{{ menu|length }}</div></div>
            </div>

            <div class="grid-2">
                <div class="box">
                    <h2>📦 Live Customer Orders</h2>
                    {% if orders %}
                    <table>
                        <tr><th>Item Name</th><th>Price</th><th>Action</th></tr>
                        {% for o in orders %}
                        <tr>
                            <td>{{ o.name }}</td>
                            <td style="color: #34d399; font-weight: bold;">Rs. {{ o.price }}</td>
                            <td><a href="/complete-order/{{ loop.index0 }}" class="btn btn-green" style="text-decoration:none; font-size:0.8rem; padding:4px 8px;">Done</a></td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% else %}
                    <p style="color: #94a3b8; text-align: center; margin-top: 20px;">No pending orders right now.</p>
                    {% endif %}
                </div>

                <div class="box">
                    <h2>➕ Add New Menu Item</h2>
                    <form action="/add-item" method="POST">
                        <input type="text" name="name" placeholder="Item Name (e.g. Pasta)" required>
                        <input type="number" name="price" placeholder="Price (e.g. 800)" required>
                        <button type="submit" class="btn btn-green" style="width: 100%; padding: 10px;">Add to Menu</button>
                    </form>

                    <h2 style="margin-top: 20px;">📋 Current Menu (Remove)</h2>
                    <table>
                        {% for m in menu %}
                        <tr>
                            <td>{{ m.name }} (Rs. {{ m.price }})</td>
                            <td style="text-align: right;"><a href="/delete-item/{{ m.id }}" class="btn">Delete</a></td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """,
      orders=live_orders,
      menu=menu_items,
      revenue=total_revenue,
  )


# Customer Portal (Yahan se customer order karega)
@app.route("/customer")
def customer_portal():
  return render_template_string(
      """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Sky Lounge - Online Menu & Ordering</title>
        <style>
            body { background: #0b141a; color: white; font-family: Arial, sans-serif; padding: 30px; text-align: center; }
            h1 { color: #fbbf24; margin-bottom: 10px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; max-width: 900px; margin: 30px auto; }
            .item { background: #111b21; border: 1px solid #334155; padding: 20px; border-radius: 10px; }
            .price { color: #34d399; font-weight: bold; font-size: 1.2rem; margin: 10px 0; }
            .order-btn { background: #00a884; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; }
            .order-btn:hover { background: #008f72; }
        </style>
    </head>
    <body>
        <h1>✨ Sky Lounge Cafe ✨</h1>
        <p>Select your favorite food and place order instantly!</p>
        
        <div class="grid">
            {% for m in menu %}
            <div class="item">
                <h3>{{ m.name }}</h3>
                <div class="price">Rs. {{ m.price }}</div>
                <form action="/place-order/{{ m.id }}" method="POST">
                    <button type="submit" class="order-btn">Order Now 🛒</button>
                </form>
            </div>
            {% endfor %}
        </div>
        <br>
        <a href="/" style="color: #38bdf8;">Go to Admin Dashboard</a>
    </body>
    </html>
    """,
      menu=menu_items,
  )


# Order Place karne ka route
@app.route("/place-order/<int:item_id>", methods=["POST"])
def place_order(item_id):
  for item in menu_items:
    if item["id"] == item_id:
      live_orders.append(item)
      break
  return redirect(url_for("customer_portal"))


# Order complete/remove karne ka route
@app.route("/complete-order/<int:index>")
def complete_order(index):
  if 0 <= index < len(live_orders):
    live_orders.pop(index)
  return redirect(url_for("dashboard"))


# Naya item add karne ka route
@app.route("/add-item", methods=["POST"])
def add_item():
  name = request.form.get("name")
  price = int(request.form.get("price"))
  new_id = len(menu_items) + 1
  menu_items.append({"id": new_id, "name": name, "price": price})
  return redirect(url_for("dashboard"))


# Item delete karne ka route
@app.route("/delete-item/<int:item_id>")
def delete_item(item_id):
  global menu_items
  menu_items = [m for m in menu_items if m["id"] != item_id]
  return redirect(url_for("dashboard"))


if __name__ == "__main__":
  app.run(debug=True, port=5000)