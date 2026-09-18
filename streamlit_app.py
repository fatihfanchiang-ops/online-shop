import streamlit as st
import uuid
import json
import os
from datetime import datetime

# File paths
PRODUCT_FILE = "products.json"
USER_FILE = "users.json"
ORDER_FILE = "orders.json"

# Load products
def load_products():
    if os.path.exists(PRODUCT_FILE):
        with open(PRODUCT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Replaced with public accessible images (no anti-leech)
        return [
            {"id": 1, "name": "Chocolate Bar", "price": 42, "stock": 90, "image": "https://images.unsplash.com/photo-1606312619070-d48b4c652a52?w=400"},
            {"id": 2, "name": "Cream Puff", "price": 36, "stock": 70, "image": "https://images.unsplash.com/photo-1550617931-e17a704bce7c?w=400"},
            {"id": 3, "name": "Bubble Tea", "price": 55, "stock": 85, "image": "https://images.unsplash.com/photo-1558857563-b371033873b8?w=400"},
            {"id": 4, "name": "Rice Ball", "price": 32, "stock": 60, "image": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400"},
            {"id": 5, "name": "Seaweed Snack", "price": 28, "stock": 100, "image": "https://images.unsplash.com/photo-1625944525533-473f1a3d54e7?w=400"}
        ]

def save_products(products_list):
    with open(PRODUCT_FILE, "w", encoding="utf-8") as f:
        json.dump(products_list, f, ensure_ascii=False, indent=2)

# Load user list, default admin account
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return [
            {"username": "admin", "password": "admin123", "role": "admin"}
        ]

def save_users(user_list):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(user_list, f, ensure_ascii=False, indent=2)

# Load orders
def load_orders():
    if os.path.exists(ORDER_FILE):
        with open(ORDER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def save_orders(order_list):
    with open(ORDER_FILE, "w", encoding="utf-8") as f:
        json.dump(order_list, f, ensure_ascii=False, indent=2)


# Initialize session state
if "products" not in st.session_state:
    st.session_state.products = load_products()

if "cart" not in st.session_state:
    st.session_state.cart = []

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "page" not in st.session_state:
    st.session_state.page = "home"

st.set_page_config(page_title="Community Convenience Store")

# Home Page: Select Identity
if st.session_state.page == "home":
    st.title("Welcome to Community Convenience Store")
    st.subheader("Please select an option")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Guest Register"):
            st.session_state.page = "guest_register"
            st.rerun()
    with col2:
        if st.button("Guest Login"):
            st.session_state.page = "guest_login"
            st.rerun()
    with col3:
        if st.button("Admin Login"):
            st.session_state.page = "admin_login"
            st.rerun()

# ========== Guest Register Page ==========
elif st.session_state.page == "guest_register":
    st.title("Guest Registration")
    username = st.text_input("Create Username")
    password = st.text_input("Create Password", type="password")
    users = load_users()
    if st.button("Register"):
        exist = any(u["username"] == username for u in users)
        if exist:
            st.error("This username already exists!")
        elif len(username.strip()) ==0 or len(password.strip()) ==0:
            st.warning("Username and password cannot be empty")
        else:
            users.append({"username": username, "password": password, "role": "guest"})
            save_users(users)
            st.success("Registration successful! Please go to login page to sign in.")
    if st.button("Back"):
        st.session_state.page = "home"
        st.rerun()

# ========== Guest Login Page ==========
elif st.session_state.page == "guest_login":
    st.title("Guest Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    users = load_users()
    if st.button("Login"):
        for user in users:
            if user["username"] == username and user["password"] == password and user["role"] == "guest":
                st.session_state.current_user = user
                st.session_state.page = "shop"
                st.success("Login successful, entering store!")
                st.rerun()
        st.error("Wrong username or password, or this is not a guest account.")
    if st.button("Back"):
        st.session_state.page = "home"
        st.rerun()

# ========== Admin Login Page ==========
elif st.session_state.page == "admin_login":
    st.title("Administrator Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    users = load_users()
    if st.button("Login"):
        for user in users:
            if user["username"] == username and user["password"] == password and user["role"] == "admin":
                st.session_state.current_user = user
                st.session_state.page = "shop"
                st.success("Administrator login successful!")
                st.rerun()
        st.error("Incorrect username or password")
    if st.button("Back"):
        st.session_state.page = "home"
        st.rerun()

# ========== Main Shop Page (After Login) ==========
elif st.session_state.page == "shop":
    user = st.session_state.current_user
    st.sidebar.markdown(f"Logged in: {user['username']} ({user['role']})")

    # Side menu
    menu_list = ["Store Homepage", "My Order History"]
    if user["role"] == "admin":
        menu_list = ["Store Homepage", "Product Management (Admin Portal)", "View All User Orders"]

    menu = st.sidebar.selectbox("Menu", menu_list)

    if st.sidebar.button("Logout"):
        st.session_state.current_user = None
        st.session_state.cart = []
        st.session_state.page = "home"
        st.rerun()

    # ---------- Admin Portal: Product Management ----------
    if menu == "Product Management (Admin Portal)":
        st.title("Product Management Admin Portal")
        st.subheader("Add / Edit Product")
        edit_id_input = st.text_input("Edit ID (Leave blank for new product)")
        name_input = st.text_input("Product Name")
        price_input = st.number_input("Price NT$", min_value=0, step=1)
        stock_input = st.number_input("Stock Quantity", min_value=0, step=1)
        image_url_input = st.text_input("Image URL")

        col_save, col_delete = st.columns(2)
        with col_save:
            if st.button("Save Product"):
                product_list = st.session_state.products
                if edit_id_input.strip() == "":
                    new_id = str(uuid.uuid4())
                    product_list.append({
                        "id": new_id,
                        "name": name_input,
                        "price": price_input,
                        "stock": stock_input,
                        "image": image_url_input
                    })
                    st.success(f"New product added: {name_input}")
                else:
                    for item in product_list:
                        if str(item["id"]) == edit_id_input:
                            item["name"] = name_input
                            item["price"] = price_input
                            item["stock"] = stock_input
                            item["image"] = image_url_input
                            st.success("Product information updated!")
                save_products(product_list)
                st.rerun()

        with col_delete:
            del_id_input = st.text_input("Enter product ID to delete")
            if st.button("Delete Product"):
                product_list = st.session_state.products
                product_list = [p for p in product_list if str(p["id"]) != del_id_input]
                st.session_state.products = product_list
                save_products(product_list)
                st.warning("Product deleted")
                st.rerun()

        st.subheader("All Product List (With Product Images)")
        for product in st.session_state.products:
            with st.expander(f"{product['name']}｜NT${product['price']}｜Stock:{product['stock']}"):
                st.write(f"Product ID: {product['id']}")
                st.write(f"Image link: {product['image']}")
                st.image(product["image"], width=200)

    # ---------- Admin: View All Orders ----------
    elif menu == "View All User Orders":
        st.title("Admin - All Order List")
        all_orders = load_orders()
        if len(all_orders) == 0:
            st.info("No orders yet")
        else:
            for order in all_orders:
                with st.expander(f"Order ID: {order['order_id']} | User: {order['username']} | Order Time: {order['order_time']} | Total NT${order['total']}"):
                    for item in order["items"]:
                        st.write(f"{item['name']} × {item['quantity']} = NT${item['price'] * item['quantity']}")

    # ---------- Guest: My Order History ----------
    elif menu == "My Order History":
        st.title("My Order History")
        all_orders = load_orders()
        my_orders = [o for o in all_orders if o["username"] == user["username"]]
        if len(my_orders) ==0:
            st.info("You have not placed any orders yet")
        else:
            for order in my_orders:
                with st.expander(f"Order ID: {order['order_id']} | Order Time: {order['order_time']} | Total NT${order['total']}"):
                    for item in order["items"]:
                        st.write(f"{item['name']} × {item['quantity']} = NT${item['price'] * item['quantity']}")

    # ---------- Store Homepage + Shopping Cart (Quantity Counter + Checkout Button) ----------
    elif menu == "Store Homepage":
        st.title("Community Convenience Store")
        st.subheader("Product List (With Product Images)")
        for product in st.session_state.products:
            with st.container(border=True):
                col_img, col_info = st.columns([1, 3])
                with col_img:
                    st.image(product["image"], width=120)
                with col_info:
                    st.markdown(f"**{product['name']}**")
                    st.write(f"Price NT$ {product['price']}")
                    st.write(f"Remaining Stock: {product['stock']}")
                    buy_qty = st.number_input("Purchase Quantity", min_value=1, max_value=product["stock"], value=1, key=f"qty_{product['id']}")
                    if st.button(f"Add to Cart #{product['id']}", key=f"add_{product['id']}"):
                        cart_item = {
                            "product_id": product["id"],
                            "name": product["name"],
                            "price": product["price"],
                            "quantity": buy_qty
                        }
                        st.session_state.cart.append(cart_item)
                        st.success(f"{product['name']} ×{buy_qty} added to cart")

        st.divider()
        st.subheader("🛒 Shopping Cart (Shows quantity of each ordered item)")
        total_price = 0
        for index, cart_item in enumerate(st.session_state.cart):
            item_total = cart_item["price"] * cart_item["quantity"]
            total_price += item_total
            st.write(f"{cart_item['name']} ×{cart_item['quantity']} — NT${item_total}")
            if st.button(f"Delete #{index}", key=f"del_cart_{index}"):
                del st.session_state.cart[index]
                st.rerun()

        st.markdown(f"### Total Amount: NT$ {total_price}")
        col_clear, col_checkout = st.columns(2)
        with col_clear:
            if st.button("Clear Cart"):
                st.session_state.cart = []
                st.rerun()
        with col_checkout:
            if st.button("✅ Checkout / Buy Now"):
                if len(st.session_state.cart) == 0:
                    st.warning("Cart is empty, cannot checkout!")
                else:
                    new_order = {
                        "order_id": str(uuid.uuid4()),
                        "username": user["username"],
                        "items": st.session_state.cart,
                        "total": total_price,
                        "order_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    orders = load_orders()
                    orders.append(new_order)
                    save_orders(orders)
                    st.success(f"Order submitted successfully! Order ID: {new_order['order_id']}. Admin has received your order. You can view your order in My Order History.")
                    st.info("Note: Email notification cannot be implemented on free Streamlit cloud.")
                    st.session_state.cart = []
                    st.rerun()
