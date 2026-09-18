import streamlit as st
import uuid
import json
import os
from datetime import datetime

# 文件路径
PRODUCT_FILE = "products.json"
USER_FILE = "users.json"
ORDER_FILE = "orders.json"

# 加载商品
def load_products():
    if os.path.exists(PRODUCT_FILE):
        with open(PRODUCT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return [
            {"id": 1, "name": "77乳加巧克力", "price": 42, "stock": 90, "image": "https://img.pchome.com.tw/cs/items/DMAA0G-A9009X93P/000001_1684162444.jpg"},
            {"id": 2, "name": "义美小泡芙", "price": 36, "stock": 70, "image": "https://img.pchome.com.tw/cs/items/DMAA0I-A90B2B878/000001_1687521121.jpg"},
            {"id": 3, "name": "瓶装珍珠奶茶", "price": 55, "stock": 85, "image": "https://img.pchome.com.tw/cs/items/DMAA0G-A906CAB8R/000001_1682344553.jpg"},
            {"id": 4, "name": "御饭团", "price": 32, "stock": 60, "image": "https://img.pchome.com.tw/cs/items/DMAA0I-A90CX696F/000001_1688125660.jpg"},
            {"id": 5, "name": "海苔", "price": 28, "stock": 100, "image": "https://img.pchome.com.tw/cs/items/DMAA0G-A90A9Z72Y/000001_1685894225.jpg"}
        ]

def save_products(products_list):
    with open(PRODUCT_FILE, "w", encoding="utf-8") as f:
        json.dump(products_list, f, ensure_ascii=False, indent=2)

# 加载用户列表，默认内置管理员账号
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # 默认管理员
        return [
            {"username": "admin", "password": "admin123", "role": "admin"}
        ]

def save_users(user_list):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(user_list, f, ensure_ascii=False, indent=2)

# 加载订单
def load_orders():
    if os.path.exists(ORDER_FILE):
        with open(ORDER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def save_orders(order_list):
    with open(ORDER_FILE, "w", encoding="utf-8") as f:
        json.dump(order_list, f, ensure_ascii=False, indent=2)


# 会话状态初始化
if "products" not in st.session_state:
    st.session_state.products = load_products()

if "cart" not in st.session_state:
    st.session_state.cart = []

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "page" not in st.session_state:
    st.session_state.page = "home"

st.set_page_config(page_title="社区便利店")

# 首页：身份选择
if st.session_state.page == "home":
    st.title("欢迎来到社区便利店")
    st.subheader("请选择操作")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("访客注册"):
            st.session_state.page = "guest_register"
            st.rerun()
    with col2:
        if st.button("访客登录"):
            st.session_state.page = "guest_login"
            st.rerun()
    with col3:
        if st.button("管理员登录"):
            st.session_state.page = "admin_login"
            st.rerun()

# ========== 访客注册页面 ==========
elif st.session_state.page == "guest_register":
    st.title("访客注册")
    username = st.text_input("设置用户名")
    password = st.text_input("设置密码", type="password")
    users = load_users()
    if st.button("注册"):
        # 检查用户名是否重复
        exist = any(u["username"] == username for u in users)
        if exist:
            st.error("该用户名已存在！")
        elif len(username.strip()) ==0 or len(password.strip()) ==0:
            st.warning("用户名和密码不能为空")
        else:
            users.append({"username": username, "password": password, "role": "guest"})
            save_users(users)
            st.success("注册成功！请去登录页面登录")
    if st.button("返回"):
        st.session_state.page = "home"
        st.rerun()

# ========== 访客登录页面 ==========
elif st.session_state.page == "guest_login":
    st.title("访客登录")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    users = load_users()
    if st.button("登录"):
        for user in users:
            if user["username"] == username and user["password"] == password and user["role"] == "guest":
                st.session_state.current_user = user
                st.session_state.page = "shop"
                st.success("登录成功，进入商城！")
                st.rerun()
        st.error("用户名或密码错误，或者不是访客账号")
    if st.button("返回"):
        st.session_state.page = "home"
        st.rerun()

# ========== 管理员登录页面 ==========
elif st.session_state.page == "admin_login":
    st.title("管理员登录")
    username = st.text_input("账号")
    password = st.text_input("密码", type="password")
    users = load_users()
    if st.button("登录"):
        for user in users:
            if user["username"] == username and user["password"] == password and user["role"] == "admin":
                st.session_state.current_user = user
                st.session_state.page = "shop"
                st.success("管理员登录成功！")
                st.rerun()
        st.error("账号或密码错误")
    if st.button("返回"):
        st.session_state.page = "home"
        st.rerun()

# ========== 商城主页面（登录成功后） ==========
elif st.session_state.page == "shop":
    user = st.session_state.current_user
    st.sidebar.markdown(f"当前登录：{user['username']}（{user['role']}）")

    # 侧边菜单：管理员多【商品管理】【查看全部订单】，访客有【我的订单历史】
    menu_list = ["商城首页", "我的订单历史"]
    if user["role"] == "admin":
        menu_list = ["商城首页", "商品管理（后台）", "查看全部用户订单"]

    menu = st.sidebar.selectbox("功能菜单", menu_list)

    if st.sidebar.button("退出登录"):
        st.session_state.current_user = None
        st.session_state.cart = []
        st.session_state.page = "home"
        st.rerun()

    # ---------- 商品管理后台（Admin Portal 管理员门户） ----------
    if menu == "商品管理（后台）":
        st.title("商品管理后台 Admin Portal")
        st.subheader("新增 / 编辑商品")
        edit_id_input = st.text_input("编辑ID（新增商品时留空）")
        name_input = st.text_input("商品名称")
        price_input = st.number_input("价格 NT$", min_value=0, step=1)
        stock_input = st.number_input("库存数量", min_value=0, step=1)
        image_url_input = st.text_input("图片网址")

        col_save, col_delete = st.columns(2)
        with col_save:
            if st.button("保存商品"):
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
                    st.success(f"成功新增商品：{name_input}")
                else:
                    for item in product_list:
                        if str(item["id"]) == edit_id_input:
                            item["name"] = name_input
                            item["price"] = price_input
                            item["stock"] = stock_input
                            item["image"] = image_url_input
                            st.success("商品信息已更新！")
                save_products(product_list)
                st.rerun()

        with col_delete:
            del_id_input = st.text_input("输入要删除的商品ID")
            if st.button("删除商品"):
                product_list = st.session_state.products
                product_list = [p for p in product_list if str(p["id"]) != del_id_input]
                st.session_state.products = product_list
                save_products(product_list)
                st.warning("商品已删除")
                st.rerun()

        st.subheader("全部商品列表（带商品图片）")
        for product in st.session_state.products:
            with st.expander(f"{product['name']}｜NT${product['price']}｜库存:{product['stock']}"):
                st.write(f"商品ID：{product['id']}")
                st.write(f"图片链接：{product['image']}")
                st.image(product["image"], width=200)

    # ---------- 管理员：查看全部订单 ----------
    elif menu == "查看全部用户订单":
        st.title("管理员 - 所有订单列表")
        all_orders = load_orders()
        if len(all_orders) == 0:
            st.info("暂无任何订单")
        else:
            for order in all_orders:
                with st.expander(f"订单编号：{order['order_id']} | 用户：{order['username']} | 下单时间：{order['order_time']} | 总价 NT${order['total']}"):
                    for item in order["items"]:
                        st.write(f"{item['name']} × {item['quantity']} = NT${item['price'] * item['quantity']}")

    # ---------- 访客：我的订单历史 ----------
    elif menu == "我的订单历史":
        st.title("我的订单历史")
        all_orders = load_orders()
        # 筛选当前登录用户的订单
        my_orders = [o for o in all_orders if o["username"] == user["username"]]
        if len(my_orders) ==0:
            st.info("你还没有下过订单")
        else:
            for order in my_orders:
                with st.expander(f"订单编号：{order['order_id']} | 下单时间：{order['order_time']} | 总价 NT${order['total']}"):
                    for item in order["items"]:
                        st.write(f"{item['name']} × {item['quantity']} = NT${item['price'] * item['quantity']}")

    # ---------- 商城首页 + 购物车（增加数量计数器、结账按钮） ----------
    elif menu == "商城首页":
        st.title("社区便利店")
        st.subheader("商品列表（带商品图片）")
        # 选购商品，数量选择
        for product in st.session_state.products:
            with st.container(border=True):
                col_img, col_info = st.columns([1, 3])
                with col_img:
                    st.image(product["image"], width=120)
                with col_info:
                    st.markdown(f"**{product['name']}**")
                    st.write(f"售价 NT$ {product['price']}")
                    st.write(f"剩余库存: {product['stock']}")
                    buy_qty = st.number_input("购买数量", min_value=1, max_value=product["stock"], value=1, key=f"qty_{product['id']}")
                    if st.button(f"加入购物车 #{product['id']}", key=f"add_{product['id']}"):
                        # 加入购物车，保存数量
                        cart_item = {
                            "product_id": product["id"],
                            "name": product["name"],
                            "price": product["price"],
                            "quantity": buy_qty
                        }
                        st.session_state.cart.append(cart_item)
                        st.success(f"{product['name']} ×{buy_qty} 已加入购物车")

        st.divider()
        st.subheader("🛒 购物车（显示每件商品订购数量）")
        total_price = 0
        for index, cart_item in enumerate(st.session_state.cart):
            item_total = cart_item["price"] * cart_item["quantity"]
            total_price += item_total
            st.write(f"{cart_item['name']} ×{cart_item['quantity']} — NT${item_total}")
            if st.button(f"删除 #{index}", key=f"del_cart_{index}"):
                del st.session_state.cart[index]
                st.rerun()

        st.markdown(f"### 总金额：NT$ {total_price}")
        col_clear, col_checkout = st.columns(2)
        with col_clear:
            if st.button("清空购物车"):
                st.session_state.cart = []
                st.rerun()
        with col_checkout:
            if st.button("✅ 结账 / Buy Now"):
                if len(st.session_state.cart) == 0:
                    st.warning("购物车是空的，不能结账！")
                else:
                    # 创建订单
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
                    st.success(f"订单提交成功！订单编号：{new_order['order_id']}，管理员已收到订单，你可以在【我的订单历史】查看。")
                    st.info("⚠️ 邮件通知功能：Streamlit免费部署环境无法直接发送邮件，可以后续额外配置SMTP实现邮件发送。")
                    # 清空购物车
                    st.session_state.cart = []
                    st.rerun()
