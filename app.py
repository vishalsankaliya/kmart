import mysql.connector

from flask import Flask
from flask import redirect, url_for
from flask import request, session, render_template, flash

app = Flask(__name__)
app.secret_key = "mart123"

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1143",
        database="k_mart"
    )
    return conn


@app.route('/')
def index():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products LIMIT 8")
    featured_products = cursor.fetchall()

    cursor.execute("SELECT * FROM customer_reviews ORDER BY id DESC LIMIT 6")
    reviews = cursor.fetchall()

    cursor.close()
    conn.close()

    logged_in = 'user_id' in session

    return render_template(
        "index.html",
        featured_products=featured_products,
        reviews=reviews,
        logged_in=logged_in
    )


@app.route('/check')
def check():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE();")
    db = cursor.fetchone()

    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    return f"Database: {db}, Tables: {tables}"

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/appliance')
def appliance():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    category = request.args.get('category')
    brand = request.args.get('brand')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    query = """
                SELECT * FROM products 
                WHERE category IN ('Smart TVs','washing Machines','Refrigerators')
            """

    values = []

    if category:
        query += " AND category = %s"
        values.append(category)

    if brand:
        query += " AND brand = %s"
        values.append(brand)

    if min_price:
        query += " AND price >= %s"
        values.append(min_price)

    if max_price:
        query += " AND price <= %s"
        values.append(max_price)

    cursor.execute(query, values)
    products = cursor.fetchall()

    cursor.close()
    conn.close()


    return render_template("appliances.html", products=products)

@app.route("/search")
def search():

    query = request.args.get("search")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM products
        WHERE name LIKE %s
    """, ("%" + query + "%",))

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("search_results.html", products=results, query=query)

@app.route('/cart', methods=['GET', 'POST'])
def cart():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        product_id = request.form.get('product_id')

        cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = cursor.fetchone()

        if product:
            cursor.execute("SELECT * FROM cart WHERE product_id=%s", (product_id,))
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    "UPDATE cart SET quantity = quantity + 1 WHERE product_id=%s AND user_id=%s",
                    (product_id, session['user_id'])
                )
            else:
                cursor.execute("""
                    INSERT INTO cart (user_id,product_id, name, price, image, quantity)
                    VALUES (%s, %s, %s, %s,%s, %s)
                """, (
                    session['user_id'],
                    product['id'],
                    product['name'],
                    product['price'],
                    product['image'],
                    1
                ))

            conn.commit()

        return redirect(url_for('cart'))

    cursor.execute("SELECT * FROM cart")
    cart_items = cursor.fetchall()

    total_price = sum(float(item['price']) * int(item['quantity']) for item in cart_items)
    total_items = sum(int(item['quantity']) for item in cart_items)

    cursor.close()
    conn.close()

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total_price=total_price,
        total_items=total_items
    )


@app.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):


    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1️⃣ Product fetch karo
    cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cursor.fetchone()


    if product:

        cursor.execute("SELECT * FROM cart WHERE product_id=%s AND user_id=%s",
                       (product_id, session.get('user_id')))
        existing = cursor.fetchone()

        if existing:
            # Quantity increase karo
            cursor.execute(
                "UPDATE cart SET quantity = quantity + 1 WHERE product_id=%s",
                (product_id,)
            )
            print("UPDATED QUANTITY")

        else:
            # 3️⃣ Insert new product
            cursor.execute("""
                INSERT INTO cart (user_id, product_id, name, price, image, quantity)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                session['user_id'],
                product['id'],
                product['name'],
                product['price'],
                product['image'],
                1
            ))
            print("INSERTED NEW PRODUCT")

        conn.commit()   # 🔥 VERY IMPORTANT

    else:
        print("PRODUCT NOT FOUND")

    cursor.close()
    conn.close()

    return redirect(url_for('cart'))


@app.route('/checkout')
def checkout():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 🔥 user specific cart data lao
    cursor.execute("SELECT * FROM cart WHERE user_id=%s", (session['user_id'],))
    cart_items = cursor.fetchall()

    cursor.execute("SELECT first_name, mobile FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()

    name = user['first_name']
    mobile = user['mobile']

    total = 0
    item_count = 0

    for item in cart_items:
        total += float(item['price']) * int(item['quantity'])
        item_count += int(item['quantity'])

    cursor.close()
    conn.close()

    return render_template(
        'checkout.html',
        cart=cart_items,
        total=total,
        item_count=item_count,
        name=name,
        mobile=mobile
    )

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/electronics')
def electronics():


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    category = request.args.get('category')
    brand = request.args.get('brand')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    query = """
            SELECT * FROM products 
            WHERE category IN ('Laptops','Cameras','Accessories')
        """

    values = []

    if category:
        query += " AND category = %s"
        values.append(category)

    if brand:
        query += " AND brand = %s"
        values.append(brand)

    if min_price:
        query += " AND price >= %s"
        values.append(min_price)

    if max_price:
        query += " AND price <= %s"
        values.append(max_price)

    cursor.execute(query, values)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("electronics.html", products=products)

@app.route('/home')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    category = request.args.get('category')

    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    query = """
                    SELECT * FROM products 
                    WHERE category IN ('Sofas','Beds','Decor','Lighting')
                """

    values = []

    if category:
        query += " AND category = %s"
        values.append(category)

    if min_price:
        query += " AND price >= %s"
        values.append(min_price)

    if max_price:
        query += " AND price <= %s"
        values.append(max_price)

    cursor.execute(query, values)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("home.html", products=products)

@app.route('/kids')
def kids():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    category = request.args.get('category')
    age = request.args.get('age')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    query = """
                    SELECT * FROM products 
                    WHERE category IN ('Toys','Clothing','School Supplies')
                """

    values = []

    if category:
        query += " AND category = %s"
        values.append(category)

    if age:
        query += " AND age = %s"
        values.append(age)

    if min_price:
        query += " AND price >= %s"
        values.append(min_price)

    if max_price:
        query += " AND price <= %s"
        values.append(max_price)

    cursor.execute(query, values)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("kids.html", products=products)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/profile')
def profile():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    user_id = session['user_id']

    cursor.execute("SELECT first_name, last_name, email, mobile, gender FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    print(user)

    cursor.close()
    conn.close()


    return render_template("profile.html", user=user)

@app.route('/update_profile', methods=['POST'])
def update_profile():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    mobile = request.form['mobile']
    gender = request.form['gender']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users 
        SET first_name=%s, last_name=%s, email=%s, mobile=%s, gender=%s
        WHERE id=%s
    """, (first_name, last_name, email, mobile, gender, user_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Profile updated successfully!", "success")
    return redirect(url_for('profile'))

@app.route('/men')
def men():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    category = request.args.get('category')

    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    query = """
                SELECT * FROM products 
                WHERE category IN ('T-Shirts','Jeans','Shoes','Watches')
            """

    values = []

    if category:
        query += " AND category = %s"
        values.append(category)

    if min_price:
        query += " AND price >= %s"
        values.append(min_price)

    if max_price:
        query += " AND price <= %s"
        values.append(max_price)

    cursor.execute(query, values)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("men.html", products=products)

@app.route('/submit_review', methods=['POST'])
def submit_review_form():

    name = request.form.get('username')
    review = request.form.get('review')
    rating = request.form.get('rating')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO reviews (name, review, rating) VALUES (%s,%s,%s)",
        (name, review, rating)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/')


@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['email']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO newsletter (email) VALUES (%s)", (email,))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Subscribed Successfully!")
    return redirect(url_for('index'))

@app.route("/add_customer_review", methods=["POST"])
def add_customer_review():

    name = request.form.get("name")
    message = request.form.get("message")
    rating = request.form.get("rating")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO customer_reviews (name,message,rating) VALUES (%s,%s,%s)",
        (name,message,rating)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/")

@app.route("/add_product_review/<int:product_id>", methods=["POST"])
def add_product_review(product_id):

    username = request.form.get("username")
    review = request.form.get("review")
    rating = request.form.get("rating")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO product_reviews (product_id,username,review,rating) VALUES (%s,%s,%s,%s)",
        (product_id,username,review,rating)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("product_detail", product_id=product_id))

@app.route('/remove_from_cart/<int:cart_id>')
def remove_from_cart(cart_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM cart WHERE id = %s", (cart_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('cart'))

@app.route("/product/<int:product_id>")
def product_detail(product_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cursor.fetchone()

    cursor.execute("SELECT * FROM product_reviews WHERE product_id=%s",(product_id,))
    reviews = cursor.fetchall()

    return render_template("product_details.html",product=product,reviews=reviews)

@app.route('/orders')
def orders():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM orders WHERE user_id=%s", (session['user_id'],))
    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("orders.html", orders=orders)

@app.route('/order_success', methods=['POST'])
def order_success():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # ✅ FIX: correct name
    payment_method = request.form.get('payment_method')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 🛒 cart data
    cursor.execute("SELECT * FROM cart WHERE user_id=%s", (user_id,))
    cart_items = cursor.fetchall()

    # 👤 user data
    cursor.execute("SELECT first_name, mobile FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    name = user['first_name']
    mobile = user['mobile']

    total = 0

    for item in cart_items:
        item_total = float(item['price']) * int(item['quantity'])
        total += item_total

        cursor.execute("""
            INSERT INTO orders 
            (user_id, mobile, product_name, quantity, price, total, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            mobile,
            item['name'],
            item['quantity'],
            item['price'],
            item_total,
            payment_method
        ))

    # 🧹 cart clear
    cursor.execute("DELETE FROM cart WHERE user_id=%s", (user_id,))

    conn.commit()
    cursor.close()
    conn.close()

    # ✅ FIX: name & mobile pass karo
    return render_template("order_success.html",
                           total=total,
                           name=name,
                           mobile=mobile)

@app.route('/otp')
def otp():
    return render_template('otp.html')


@app.route('/products')
def products():

    category = request.args.get('category')
    brand = request.args.getlist('brand')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    sort = request.args.get('sort')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
                SELECT * FROM products 
                WHERE category IN ('Laptops','Cameras','Accessories','Smart TVs','Washing Machines',
                'Refrigerators','T-Shirts','Jeans','Shoes','Watches','Dresses','Handbags','Jewelry',
                'Heels','Toys','Clothing','School Supplies','Sofas','Beds','Decor','Lighting',
                'Cricket','Football','Stationery','Pro Yoga')
            """

    values = []

    if category:
        query += " AND category = %s"
        values.append(category)

    if min_price:
        query += " AND price >= %s"
        values.append(min_price)

    if max_price:
        query += " AND price <= %s"
        values.append(max_price)

    cursor.execute(query, values)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("products.html", products=products)

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == "POST":

        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        else:
            return "Invalid email or password"

    return render_template("login.html")

@app.route('/wishlist')
def wishlist():

    user_id = session.get('user_id')

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT wishlist.id, products.name, products.price, products.image, products.id as product_id
        FROM wishlist
        JOIN products ON wishlist.product_id = products.id
        WHERE wishlist.user_id=%s
    """, (session['user_id'],))

    wishlist_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("wishlist.html", wishlist_items=wishlist_items)

@app.route('/remove_wishlist/<int:id>')
def remove_wishlist(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM wishlist WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('wishlist'))

@app.route('/add_to_wishlist/<int:product_id>')
def add_to_wishlist(product_id):

    user_id = session.get('user_id')   # SAFE METHOD

    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # already wishlist ma che ke nahi check
    cursor.execute(
        "SELECT * FROM wishlist WHERE user_id=%s AND product_id=%s",
        (user_id, product_id)
    )
    existing = cursor.fetchone()

    if not existing:
        cursor.execute(
            "INSERT INTO wishlist (user_id, product_id) VALUES (%s,%s)",
            (user_id, product_id)
        )
        conn.commit()

    cursor.close()
    conn.close()

    return redirect(request.referrer or url_for('products'))

@app.route('/sports')
def sports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    category = request.args.get('category')

    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    query = """
                    SELECT * FROM products 
                    WHERE category IN ('Cricket','Football','Stationery')
                """

    values = []

    if category:
        query += " AND category = %s"
        values.append(category)

    if min_price:
        query += " AND price >= %s"
        values.append(min_price)

    if max_price:
        query += " AND price <= %s"
        values.append(max_price)

    cursor.execute(query, values)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("sports.html", products=products)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        mobile = request.form['mobile']
        gender = request.form['gender']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO users (first_name, last_name, email, mobile, gender, password)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (first_name, last_name, email, mobile, gender, password))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/women')
def women():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    category = request.args.get('category')

    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    query = """
                    SELECT * FROM products 
                    WHERE category IN ('Dresses','Handbags','Jewelry','Heels')
                """

    values = []

    if category:
        query += " AND category = %s"
        values.append(category)

    if min_price:
        query += " AND price >= %s"
        values.append(min_price)

    if max_price:
        query += " AND price <= %s"
        values.append(max_price)

    cursor.execute(query, values)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("women.html", products=products)

@app.route('/careers')
def careers():
    return render_template("careers.html")

@app.route('/corporate')
def corporate():
    return render_template('corporate.html')

@app.route('/payments')
def payments():
    return render_template('payments.html')

@app.route('/shipping')
def shipping():
    return render_template('shipping.html')

@app.route('/cancellation')
def cancellation():
    return render_template("cancellation.html")

@app.route('/faq')
def faq():
    return render_template("faq.html")


@app.route('/terms')
def terms():
    return render_template("terms.html")

@app.route('/security')
def security():
    return render_template('security.html')

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/policy")
def policy():
    return render_template('policy.html')

if __name__ == '__main__':
    app.run(debug=True)
