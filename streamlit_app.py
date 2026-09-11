import streamlit as st
import uuid
import json
import os

# 持久化文件路径
JSON_FILE = "products.json"

# 加载商品（从json文件读取，如果不存在就用默认商品）
def load_products():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # 默认便利店商品，台币NT$
        return [
            {"id": 1, "name": "77乳加巧克力", "price": 42, "stock": 90, "image": "https://img.pchome.com.tw/cs/items/DMAA0G-A9009X93P/000001_1684162444.jpg"},
            {"id": 2, "name": "义美小泡芙", "price": 36, "stock": 70, "image": "https://img.pchome.com.tw/cs/items/DMAA0I-A90B2B878/000001_1687521121.jpg"},
            {"id": 3, "name": "瓶装珍珠奶茶", "price": 55, "stock": 85, "image": "https://img.pchome.com.tw/cs/items/DMAA0G-A906CAB8R/000001_1682344553.jpg"},
            {"id": 4, "name": "御饭团", "price": 32, "stock": 60, "image": "https://img.pchome.com.tw/cs/items/DMAA0I-A90CX696F/000001_1688125660.jpg"},
            {"id": 5, "name": "海苔", "price": 28, "stock": 100, "image": "https://img.pchome.com.tw/cs/items/DMAA0G-A90A9Z72Y/000001_1685894225.jpg"}
        ]

# 保存商品到json文件
def save_products(products_list):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(products_list, f, ensure_ascii=False, indent=2)

# ========== 初始化会话状态 ==========
if "products" not in st.session_state:
    st.session_state.products = load_products()

if "cart" not in st.session_state:
    st.session_state.cart = []

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# 侧边栏菜单
menu = st.sidebar.selectbox("功能菜单", ["商城首页", "商品管理(后台)", "管理员登录"])

# 登录页面
if menu == "管理员登录":
    st.title("管理员登录")
    username = st.text_input("账号")
    password = st.text_input("密码", type="password")
    if st.button("登录"):
        if username == "admin" and password == "admin123":
            st.session_state.is_admin = True
            st.success("登录成功，可以进入商品管理后台！")
        else:
            st.error("账号或密码错误")

# 商品管理后台（新增、编辑、删除商品）
elif menu == "商品管理(后台)":
    st.title("商品管理后台")
    if not st.session_state.is_admin:
        st.warning("请先登录管理员账号！")
    else:
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
                    # 新增商品
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
                    # 修改已有商品
                    for item in product_list:
                        if str(item["id"]) == edit_id_input:
                            item["name"] = name_input
                            item["price"] = price_input
                            item["stock"] = stock_input
                            item["image"] = image_url_input
                            st.success("商品信息更新完成！")
                # 保存到文件
                save_products(product_list)
                st.rerun()

        with col_delete:
            del_id_input = st.text_input("输入需要删除的商品ID")
            if st.button("删除商品"):
                product_list = st.session_state.products
                product_list = [p for p in product_list if str(p["id"]) != del_id_input]
                st.session_state.products = product_list
                save_products(product_list)
                st.warning("商品已删除")
                st.rerun()

        st.subheader("全部商品列表")
        for product in st.session_state.products:
            with st.expander(f"{product['name']}｜NT${product['price']}｜库存:{product['stock']}"):
                st.write(f"商品ID：{product['id']}")
                st.write(f"图片链接：{product['image']}")
                st.image(product["image"], width=200)

# 商城首页 + 购物车
elif menu == "商城首页":
    st.title("社区便利店")
    st.subheader("商品列表")
    for product in st.session_state.products:
        with st.container(border=True):
            col_img, col_info = st.columns([1, 3])
            with col_img:
                st.image(product["image"], width=120)
            with col_info:
                st.markdown(f"**{product['name']}**")
                st.write(f"售价 NT$ {product['price']}")
                st.write(f"剩余库存: {product['stock']}")
                if st.button(f"加入购物车 #{product['id']}", key=f"add_{product['id']}"):
                    st.session_state.cart.append(product)
                    st.success(f"{product['name']} 已加入购物车")

    st.divider()
    st.subheader("🛒 购物车")
    total_price = 0
    for cart_item in st.session_state.cart:
        st.write(f"{cart_item['name']} — NT${cart_item['price']}")
        total_price += cart_item["price"]
    st.markdown(f"### 总金额：NT$ {total_price}")
    if st.button("清空购物车"):
        st.session_state.cart = []
        st.rerun()
