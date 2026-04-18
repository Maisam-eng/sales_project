from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
import mysql.connector
from datetime import datetime
from functools import wraps
import decimal

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="your_password",
        database="cosmetics_store_db"
    )
 
  
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You have to log in first', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    cursor.execute("SELECT * FROM Product WHERE is_trending = 1 LIMIT 5") 
    trending = cursor.fetchall()

    cursor.execute("SELECT * FROM Product WHERE num_of_purchases >= 100 ORDER BY num_of_purchases DESC LIMIT 5") 
    best_selling = cursor.fetchall()

    cursor.close()
    return render_template('index.html', trending=trending, best_selling=best_selling)


@app.route('/products')
def products_home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    max_price = request.args.get("max_price")
    if max_price:
        try:
            max_price_val = float(max_price)
            if max_price_val < 0:
                flash("Max price cannot be negative.", "warning")
                cursor.close()
                conn.close()
                return redirect(url_for('products_home'))
        except ValueError:
            flash("Max price must be a number.", "warning")
            cursor.close()
            conn.close()
            return redirect(url_for('products_home'))
    show_trending = request.args.get("trending") == "1"
    show_best_selling = request.args.get("best_selling") == "1"

    filters = []
    if max_price:
        filters.append(f"price <= {max_price}")
    if show_trending:
        filters.append("is_trending = 1")
    if show_best_selling:
        filters.append("num_of_purchases >= 100")

    query = "SELECT * FROM Product"
    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY num_of_purchases DESC"

    cursor.execute(query)
    products = cursor.fetchall()
    cursor.close()

    return render_template("products.html",
                           products=products,
                           max_price=max_price,
                           trending=show_trending,
                           best_selling=show_best_selling)



def get_skincare_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    max_price = request.args.get("max_price")
    if max_price:
        try:
            max_price_val = float(max_price)
            if max_price_val < 0:
                flash("Max price cannot be negative.", "warning")
                cursor.close()
                conn.close()
                return redirect(url_for('skincare'))
        except ValueError:
            flash("Max price must be a number.", "warning")
            cursor.close()
            conn.close()
            return redirect(url_for('products_home'))
    show_trending = request.args.get("trending") == "1"
    show_best_selling = request.args.get("best_selling") == "1"
    skin_type = request.args.get("skin_type")

    natural_or_organic = request.args.get("natural_or_organic") == "1"
    fragrance_free = request.args.get("fragrance_free") == "1"
    product_type = request.args.get("type")

    filters = []
    joins = []

    if skin_type:
        joins.append("JOIN Skincare_Skin_Type sst ON sst.product_id = sp.product_id")

        filters.append(f"(sst.skin_type = '{skin_type}' OR sst.skin_type = 'all')")

    if max_price:
        filters.append(f"p.price <= {max_price}")
    if show_trending:
        filters.append("p.is_trending = 1")
    if show_best_selling:
        filters.append("p.num_of_purchases >= 100")
    if product_type:
        filters.append(f"sp.type = '{product_type}'")
    if natural_or_organic:
        filters.append("sp.natural_or_organic = 1")
    if fragrance_free:
        filters.append("sp.fragrance_free = 1")

    base_query = f"""
        SELECT DISTINCT p.*
        FROM Product p
        JOIN Skincare_Product sp ON p.product_id = sp.product_id
        {' '.join(joins)}
    """

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    cursor.execute(base_query)
    products = cursor.fetchall()
    cursor.close()

    return render_template("skincare.html",
                           category_name="Skincare",
                           products=products,
                           max_price=max_price,
                           trending=show_trending,
                           best_selling=show_best_selling,
                           skin_type=skin_type,
                           natural_or_organic=natural_or_organic,
                           fragrance_free=fragrance_free,
                           product_type=product_type)

# ......
def get_category_products(category_table, template_name, category_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    max_price = request.args.get("max_price")
    show_trending = request.args.get("trending") == "1"
    show_best_selling = request.args.get("best_selling") == "1"

    filters = []
    if max_price:
        filters.append(f"p.price <= {max_price}")
    if show_trending:
        filters.append("p.is_trending = 1")
    if show_best_selling:
        filters.append("p.num_of_purchases >= 100")

    base_query = f"""
        SELECT p.*
        FROM Product p
        JOIN {category_table} c ON p.product_id = c.product_id
    """

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    cursor.execute(base_query)

    products = cursor.fetchall()
    cursor.close()

    return render_template(template_name,
                           category_name=category_name,
                           products=products,
                           max_price=max_price,
                           trending=show_trending,
                           best_selling=show_best_selling)


@app.route('/products/skincare')
def skincare():
    return get_skincare_products()


@app.route('/products/haircare')
def haircare():
    return get_haircare_products()


@app.route('/products/fragrance')
def fragrance():
    return get_fragrance_products()



@app.route("/product/<int:product_id>")
def product_detail(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    cursor.execute("SELECT * FROM Product WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    if not product:
        return "Product not found", 404

    category = None

    # === Skincare Section ===
    cursor.execute("SELECT * FROM Skincare_Product WHERE product_id = %s", (product_id,))
    skincare = cursor.fetchone()
    if skincare:
        category = "Skincare"
        product.update(skincare)

        def get_list(query, column_name):
            cursor.execute(query, (product_id,))
            return [row[column_name] for row in cursor.fetchall()]

        product["skin_types"] = get_list("SELECT skin_type FROM Skincare_Skin_Type WHERE product_id = %s", "skin_type")
        product["ingredients"] = get_list("SELECT ingredient FROM Skincare_Ingredient WHERE product_id = %s", "ingredient")

    # === Haircare Section ===
    cursor.execute("SELECT * FROM Hair_Product WHERE product_id = %s", (product_id,))
    haircare = cursor.fetchone()
    if haircare:
        category = "Haircare"
        product.update(haircare)

        def get_list(query, column_name):
            cursor.execute(query, (product_id,))
            return [row[column_name] for row in cursor.fetchall()]

        product["hair_types"] = get_list("SELECT hair_type FROM Hair_Hair_Type WHERE product_id = %s", "hair_type")
        product["scalp_types"] = get_list("SELECT scalp_type FROM Hair_Scalp_Type WHERE product_id = %s", "scalp_type")
        product["ingredients"] = get_list("SELECT ingredient FROM Hair_Ingredient WHERE product_id = %s", "ingredient")

    # === Fragrance Section ===
    cursor.execute("SELECT * FROM Fragrance WHERE product_id = %s", (product_id,))
    fragrance = cursor.fetchone()
    if fragrance:
        category = "Fragrance"
        product.update(fragrance)

        def get_list(query, column_name):
            cursor.execute(query, (product_id,))
            return [row[column_name] for row in cursor.fetchall()]

        product["seasons"] = get_list("SELECT season FROM Fragrance_Season WHERE product_id = %s", "season")
        product["times"] = get_list("SELECT recommended_time FROM Fragrance_Time WHERE product_id = %s", "recommended_time")
        product["scent_notes"] = get_list("SELECT scent_note FROM Fragrance_Scent_Note WHERE product_id = %s", "scent_note")
        product["genders"] = get_list("SELECT gender FROM Fragrance_Gender WHERE product_id = %s", "gender")

    cursor.close()
    return render_template("product_detail.html", product=product, category=category)


def calculate_total(cart_items):
    total = decimal.Decimal("0.00")
    for item in cart_items:
        total += item["price"] * item["quantity"]
    return total



@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash('You have to log in first', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        #get product_id and action from the form
        product_id = request.form.get('product_id')
        action = request.form.get('action')
    #get the cart_id from the Shopping_Cart table
        cursor.execute('SELECT cart_id FROM Shopping_Cart WHERE customer_id = %s', (user_id,))
        cart = cursor.fetchone()
        if not cart:
            flash('Cart not found', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('cart'))

        cart_id = cart['cart_id']

        # get the quantity of the product in the cart
        cursor.execute('SELECT quantity FROM Cart_Product WHERE cart_id = %s AND product_id = %s', (cart_id, product_id))
        cart_product = cursor.fetchone()
        if not cart_product:
            flash('Product not found in cart', 'warning')
            cursor.close()
            conn.close()
            return redirect(url_for('cart'))

        current_quantity = cart_product['quantity']

        if action == 'increase':
            new_quantity = current_quantity + 1
            cursor.execute('UPDATE Cart_Product SET quantity = %s WHERE cart_id = %s AND product_id = %s',
                           (new_quantity, cart_id, product_id))
            conn.commit()
           

        elif action == 'decrease':
            if current_quantity > 1:
                new_quantity = current_quantity - 1
                cursor.execute('UPDATE Cart_Product SET quantity = %s WHERE cart_id = %s AND product_id = %s',
                               (new_quantity, cart_id, product_id))
                conn.commit()
            else:
                # quantity is 1 and we decrease it remove the product from the cart
                cursor.execute('DELETE FROM Cart_Product WHERE cart_id = %s AND product_id = %s', (cart_id, product_id))
                conn.commit()
               

        elif action == 'delete':
            cursor.execute('DELETE FROM Cart_Product WHERE cart_id = %s AND product_id = %s', (cart_id, product_id))
            conn.commit()
            flash('Product removed from cart', 'success')

        else:
            flash('Unknown action', 'danger')

        cursor.close()
        conn.close()
        return redirect(url_for('cart'))

    # GET request: Show cart
    cursor.execute('''
        SELECT p.product_id, p.pname, p.price, cp.quantity
        FROM Shopping_Cart sc
        JOIN Cart_Product cp ON sc.cart_id = cp.cart_id
        JOIN Product p ON cp.product_id = p.product_id
        WHERE sc.customer_id = %s
    ''', (user_id,))

    cart_items = cursor.fetchall()
    cursor.close()
    conn.close()

    total_price = sum(item['price'] * item['quantity'] for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


@app.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = request.form.get('product_id')
    action = request.form.get('action')
    
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']

    if not product_id or not action:
        flash("Error in request, please try again.")
        return redirect(url_for('cart'))  # Show cart page

    # Ensure the product exists in the cart before modifying
    if product_id not in cart:
        flash("the product is not in the cart.")
        return redirect(url_for('cart'))

    if action == 'increase':
        cart[product_id] += 1

    elif action == 'decrease':
        if cart[product_id] > 1:
            cart[product_id] -= 1
        else:
            # quantity is 1 and we decrease it, we remove the product from the cart
            cart.pop(product_id)

    elif action == 'delete':
        cart.pop(product_id)

    else:
        flash("Unknown action.")
        return redirect(url_for('cart'))

    # save changes to the session
    session['cart'] = cart

    flash("Cart updated successfully.")
    return redirect(url_for('cart'))

from datetime import datetime

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash("You have to log in first.", "warning")
        return redirect(url_for('login'))

    selected_product_ids = request.form.getlist('product_ids')
    if not selected_product_ids:
        flash("Please select at least one product.", "error")
        return redirect(url_for('cart'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT branch_id, b_name FROM Branch')
    branches = cursor.fetchall()

    cursor.execute('SELECT employee_id, employee_name FROM Employee WHERE branch_id IS NOT NULL')
    employees = cursor.fetchall()

    cursor.close()
    conn.close()

    # get user data from session
    customer_id = session['user_id']
    customer_name = session.get('user_name', '')

    return render_template('checkout.html',
                           branches=branches,
                           employees=employees,
                           selected_product_ids=selected_product_ids,
                           customer_id=customer_id,
                           customer_name=customer_name)


@app.route('/finalize_checkout', methods=['POST'])
def finalize_checkout():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash("You have to log in first.", 'warning')
        return redirect(url_for('login'))

    customer_id = session['user_id']

    # get data from the form
    product_ids = request.form.getlist('product_ids')
    branch_id = request.form.get('branch_id')
    address_text = request.form.get('address')
    address_type = request.form.get('address_type')
    employee_id = request.form.get('employee_id')
    payment_method = request.form.get('payment_method')

    if not all([product_ids, branch_id, address_text, address_type, employee_id, payment_method]):
        flash("Please fill in all required fields.", "error")
        return redirect(url_for('cart'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # add new address for the customer
    cursor.execute('SELECT MAX(address_id) AS max_id FROM Customer_Address')
    row = cursor.fetchone()
    next_address_id = 1 if row['max_id'] is None else row['max_id'] + 1

    cursor.execute('''
        INSERT INTO Customer_Address (address_id, customer_id, address, address_type)
        VALUES (%s, %s, %s, %s)
    ''', (next_address_id, customer_id, address_text, address_type))

    # get current cart_id for the customer
    cursor.execute('SELECT cart_id FROM Shopping_Cart WHERE customer_id = %s', (customer_id,))
    cart_row = cursor.fetchone()
    cart_id = cart_row['cart_id'] if cart_row else None

    # get selected product data from cart
    format_strings = ','.join(['%s'] * len(product_ids))
    cursor.execute(f'''
        SELECT p.product_id, p.pname, p.price, cp.quantity
        FROM Shopping_Cart sc
        JOIN Cart_Product cp ON sc.cart_id = cp.cart_id
        JOIN Product p ON cp.product_id = p.product_id
        WHERE sc.customer_id = %s AND p.product_id IN ({format_strings})
    ''', (customer_id, *product_ids))
    ordered_products = cursor.fetchall()

    total_price = sum(item['price'] * item['quantity'] for item in ordered_products)

    # create new order with cart_id
    now = datetime.now()
    cursor.execute('SELECT MAX(order_id) AS max_id FROM Sales_Order')
    row = cursor.fetchone()
    order_id = 1 if row['max_id'] is None else row['max_id'] + 1

    cursor.execute('''
        INSERT INTO Sales_Order (order_id, cart_id, order_date, total_price, payment_status, credit_card_details, address_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (order_id, cart_id, now, total_price, 'Pending', payment_method, next_address_id))

    # add products to Order_Line
    for item in ordered_products:
        cursor.execute('''
            INSERT INTO Order_Line (order_id, product_id, quantity, price_at_order_time)
            VALUES (%s, %s, %s, %s)
        ''', (order_id, item['product_id'], item['quantity'], item['price']))

    # add assignment to order
    cursor.execute('''
        INSERT INTO Order_Assignment (order_id, customer_id, employee_id, assigned_date)
        VALUES (%s, %s, %s, %s)
    ''', (order_id, customer_id, employee_id, now))

    # add payment
    cursor.execute('SELECT MAX(payment_id) AS max_id FROM Payment')
    row = cursor.fetchone()
    payment_id = 1 if row['max_id'] is None else row['max_id'] + 1

    cursor.execute('''
        INSERT INTO Payment (payment_id, order_id, amount, payment_date, payment_method, payment_status)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (payment_id, order_id, total_price, now.date(), payment_method, 'Paid'))

    conn.commit()
    cursor.close()
    conn.close()

    return render_template('order_summary.html',
                           order_id=order_id,
                           address=address_text,
                           branch_id=branch_id,
                           payment_method=payment_method,
                           total_price=total_price,
                           ordered_products=ordered_products)

@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    if 'customer_id' not in session:
        flash("You have to log in first.", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # get order data
    cursor.execute('SELECT * FROM Sales_Order WHERE order_id = %s', (order_id,))
    order = cursor.fetchone()

    # get branch data
    cursor.execute('SELECT * FROM Branch WHERE branch_id = %s', (order['branch_id'],))
    branch = cursor.fetchone()

    # get address data
    cursor.execute('SELECT * FROM Customer_Address WHERE address_id = %s', (order['address_id'],))
    address = cursor.fetchone()

    # get employee data
    cursor.execute('''
        SELECT e.employee_id, e.employee_name
        FROM Employee e
        JOIN Order_Assignment oa ON e.employee_id = oa.employee_id
        WHERE oa.order_id = %s
    ''', (order_id,))
    employee = cursor.fetchone()

    # get ordered products with details
    cursor.execute('''
        SELECT ol.product_id, p.pname AS product_name, ol.quantity, ol.price_at_order_time
        FROM Order_Line ol
        JOIN Product p ON ol.product_id = p.product_id
        WHERE ol.order_id = %s
    ''', (order_id,))
    order_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('order_confirmation.html',
                           order=order,
                           branch=branch,
                           address=address,
                           employee=employee,
                           order_items=order_items)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash('You have to log in first to add products to the cart.', 'warning')
        return redirect(url_for('login'))

    try:
        quantity = int(request.form.get('quantity', 1))
    except ValueError:
        flash("Quantity must be a number.", "warning")
        return redirect(url_for('product_detail', product_id=product_id))

    if quantity <= 0:
        flash("Quantity must be greater than zero.", "warning")
   
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # check if the customer has an existing cart
    cursor.execute('SELECT cart_id FROM Shopping_Cart WHERE customer_id = %s', (user_id,))
    cart = cursor.fetchone()

    if cart is None:
        # if no cart exists create a new one
        cursor.execute('INSERT INTO Shopping_Cart (cart_id, customer_id) VALUES (NULL, %s)', (user_id,))
        conn.commit()
        # get last cart_id inserted
        cursor.execute('SELECT LAST_INSERT_ID()')
        cart_id = cursor.fetchone()[0]
    else:
        cart_id = cart[0]

    # check if the product exists in the cart
    cursor.execute('SELECT quantity FROM Cart_Product WHERE cart_id = %s AND product_id = %s', (cart_id, product_id))
    existing_product = cursor.fetchone()

    if existing_product:
       #if exists update quantity
       new_quantity = existing_product[0] + quantity
       cursor.execute('UPDATE Cart_Product SET quantity = %s WHERE cart_id = %s AND product_id = %s', (new_quantity, cart_id, product_id))
    else:
        # if not exists insert new product
        cursor.execute('INSERT INTO Cart_Product (cart_id, product_id, quantity, date_added) VALUES (%s, %s, %s, CURDATE())', (cart_id, product_id, quantity))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Product added to cart successfully.', 'success')
    return redirect(url_for('cart'))

def get_haircare_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    max_price = request.args.get("max_price")
    if max_price:
        try:
            max_price_val = float(max_price)
            if max_price_val < 0:
                flash("Max price cannot be negative.", "warning")
                cursor.close()
                conn.close()
                return redirect(url_for('haircare'))
        except ValueError:
            flash("Max price must be a number.", "warning")
            cursor.close()
            conn.close()
            return redirect(url_for('/products/haircare'))
    show_trending = request.args.get("trending") == "1"
    show_best_selling = request.args.get("best_selling") == "1"
    hair_type = request.args.get("hair_type")
    scalp_type = request.args.get("scalp_type") 
    sulfate_free = request.args.get("sulfate_free") == "1" 

    natural_or_organic = request.args.get("natural_or_organic") == "1"
    fragrance_free = request.args.get("fragrance_free") == "1"
    product_type = request.args.get("type")

    filters = []
    joins = []

    if hair_type:
        joins.append("JOIN Hair_Hair_Type hh ON hh.product_id = hp.product_id")
        filters.append(f"(hh.hair_type = %s OR hh.hair_type = 'All')")

    if scalp_type:
        joins.append("JOIN Hair_Scalp_Type hs ON hs.product_id = hp.product_id")
        filters.append(f"(hs.scalp_type = %s)")

    if max_price:
        filters.append("p.price <= %s")
    if show_trending:
        filters.append("p.is_trending = 1")
    """ if show_best_selling:
        filters.append("p.num_of_purchases >= 100")"""
    if product_type:
        filters.append("hp.type = %s")
    if natural_or_organic:
        filters.append("hp.natural_or_organic = 1")
    if fragrance_free:
        filters.append("hp.fragrance_free = 1")
    if sulfate_free:
        filters.append("hp.sulfate_free = 1")

    base_query = f"""
        SELECT DISTINCT p.*
        FROM Product p
        JOIN Hair_Product hp ON p.product_id = hp.product_id
        {' '.join(joins)}
    """

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    values = []
    if hair_type:
        values.append(hair_type)
    if scalp_type:
        values.append(scalp_type)
    if max_price:
        values.append(max_price)
    if product_type:
        values.append(product_type)

    cursor.execute(base_query, values)
    products = cursor.fetchall()
    cursor.close()

    return render_template("haircare.html",
                           category_name="Haircare",
                           products=products,
                           max_price=max_price,
                           trending=show_trending,
                           best_selling=show_best_selling,
                           hair_type=hair_type,
                           scalp_type=scalp_type,
                           natural_or_organic=natural_or_organic,
                           fragrance_free=fragrance_free,
                           sulfate_free=sulfate_free,
                           product_type=product_type)

def get_fragrance_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


   #get filters from request
    max_price = request.args.get("max_price")
    
    show_trending = request.args.get("trending") == "1"
    show_best_selling = request.args.get("best_selling") == "1"

    season = request.args.get("season")
    recommended_time = request.args.get("recommended_time")
    gender = request.args.get("gender")
    scent_note = request.args.get("scent_note")

    concentration = request.args.get("concentration")
    is_alcohol_free = request.args.get("is_alcohol_free")  
    lasting_hours = request.args.get("lasting_hours")
    if lasting_hours :
        try:
                lasting_hours_val = float(lasting_hours)
                if lasting_hours_val < 0:
                    flash("lasting hours cannot be negative.", "warning")
                    cursor.close()
                    conn.close()
                    return redirect(url_for('fragrance'))
        except ValueError:
                flash("lasting hours must be a number.", "warning")
                cursor.close()
                conn.close()
                return redirect(url_for('fragrance'))
    fragrance_type = request.args.get("fragrance_type")
    size_ml = request.args.get("size_ml")
    if size_ml:
        try:
                size_ml_val = float(size_ml)
                if size_ml_val < 0:
                    flash("size cannot be negative.", "warning")
                    cursor.close()
                    conn.close()
                    return redirect(url_for('fragrance'))
        except ValueError:
                flash("size must be a number.", "warning")
                cursor.close()
                conn.close()
                return redirect(url_for('products_home'))

    filters = []
    joins = []
    values = []

    # add filters and joins based on the request parameters
    if season:
        joins.append("JOIN Fragrance_Season fs ON fs.product_id = f.product_id")
        filters.append("fs.season = %s")
        values.append(season)

    if recommended_time:
        joins.append("JOIN Fragrance_Time ft ON ft.product_id = f.product_id")
        filters.append("ft.recommended_time = %s")
        values.append(recommended_time)

    if gender:
        joins.append("JOIN Fragrance_Gender fg ON fg.product_id = f.product_id")
        filters.append("(fg.gender = %s OR fg.gender = 'Unisex')")
        values.append(gender)

    if scent_note:
        joins.append("JOIN Fragrance_Scent_Note sn ON sn.product_id = f.product_id")
        filters.append("sn.scent_note = %s")
        values.append(scent_note)

    if max_price:
        filters.append("p.price <= %s")
        values.append(max_price)

    if show_trending:
        filters.append("p.is_trending = 1")

    if show_best_selling:
        filters.append("p.num_of_purchases >= 100")

    if concentration:
        filters.append("f.concentration = %s")
        values.append(concentration)

    if is_alcohol_free is not None:
        val = 1 if is_alcohol_free.lower() in ['1', 'true', 'yes', 'on'] else 0
        filters.append("f.is_alcohol_free = %s")
        values.append(val)

    if lasting_hours:
        filters.append("f.lasting_hours >= %s")
        values.append(lasting_hours)

    if fragrance_type:
        filters.append("f.fragrance_type = %s")
        values.append(fragrance_type)

    if size_ml:
        filters.append("f.size_ml <= %s")
        values.append(size_ml)
#the base query
    base_query = f"""
        SELECT DISTINCT p.*
        FROM Product p
        JOIN Fragrance f ON p.product_id = f.product_id
        {' '.join(joins)}
    """

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    cursor.execute(base_query, values)
    products = cursor.fetchall()
    cursor.close()

    return render_template(
        "fragrance.html",
        category_name="Fragrance",
        products=products,
        max_price=max_price,
        trending=show_trending,
        best_selling=show_best_selling,
        season=season,
        recommended_time=recommended_time,
        gender=gender,
        scent_note=scent_note,
        concentration=concentration,
        is_alcohol_free=is_alcohol_free,
        lasting_hours=lasting_hours,
        fragrance_type=fragrance_type,
        size_ml=size_ml
    )




@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        if user_type == 'customer':
            cursor.execute('''
                SELECT c.customer_id, c.cname AS name, ca.password
                FROM Customer_Email ce
                JOIN Customer c ON ce.customer_id = c.customer_id
                JOIN Customer_Auth ca ON c.customer_id = ca.customer_id
                WHERE ce.email = %s AND ce.is_primary = TRUE
            ''', (email,))
        elif user_type == 'manager':
            cursor.execute('''
                SELECT e.employee_id AS manager_id, e.employee_name AS name, ma.password
                FROM Employee_Contact ec
                JOIN Employee e ON ec.employee_id = e.employee_id
                JOIN Manager_Auth ma ON e.employee_id = ma.employee_id
                WHERE ec.contact_value = %s
                  AND ec.contact_type = 'Email'
                  AND e.is_manager = TRUE
            ''', (email,))
        else:
            flash('Invalid user type', 'danger')
            return redirect(url_for('login'))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            if user['password'] != password:
                flash('Incorrect password', 'danger')
                return redirect(url_for('login'))

            session.clear()
            session['user_type'] = user_type
            
            if user_type == 'customer':
                session['user_id'] = user['customer_id']
                session['user_name'] = user['name']
            else:
                session['user_id'] = user['manager_id']
                session['user_name'] = user['name']

            flash('Login successful', 'success')

            if user_type == 'manager':
                return redirect(url_for('manager_home'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid email or not registered', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        cname = request.form['cname']
        gender = request.form['gender']
        date_of_birth_str = request.form['date_of_birth']
        email = request.form['email']
        password = request.form['password']

        if not (cname and gender and date_of_birth_str and email):
            flash("Please fill all fields.")
            return redirect(url_for('signup'))

        if not password:
            flash("Password is required.")
            return redirect(url_for('signup'))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "warning")
            return redirect(url_for('signup'))

        if '@' not in email or '.' not in email:
            flash("Please enter a valid email address.", "warning")
            return redirect(url_for('signup'))

        try:
            date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.")
            return redirect(url_for('signup'))


        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT MAX(customer_id) FROM Customer")
        result = cursor.fetchone()
        new_customer_id = (result[0] or 0) + 1

        try:
            cursor.execute(
                "INSERT INTO Customer (customer_id, cname, gender, date_of_birth) VALUES (%s, %s, %s, %s)",
                (new_customer_id, cname, gender, date_of_birth)
            )

            cursor.execute(
                "INSERT INTO Customer_Email (customer_id, email, is_primary) VALUES (%s, %s, TRUE)",
                (new_customer_id, email)
            )

            cursor.execute(
                "INSERT INTO Customer_Auth (customer_id, password) VALUES (%s, %s)",
                (new_customer_id, password)
            )

            conn.commit()
            flash("Account created successfully! Please log in.")
            return redirect(url_for('login'))

        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Database error: {err}")
            return redirect(url_for('signup'))

        finally:
            cursor.close()
            conn.close()

    return render_template('signup.html')


@app.route('/manager/home')
def manager_home():
    if 'user_type' not in session or session['user_type'] != 'manager':
        flash("Access denied", "danger")
        return redirect(url_for('login'))
    return render_template('manager.html')
  
@app.route('/customers')
def customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    customer_id = request.args.get('customer_id')
    cname = request.args.get('cname')
    gender = request.args.get('gender')
    dob = request.args.get('date_of_birth')
    top_n = request.args.get('top_n', type=int)
    inactive_since = request.args.get('inactive_since')

    if top_n:
        query = """
        SELECT 
            c.customer_id,
            c.cname,
            c.gender,
            c.date_of_birth,
            MAX(so.order_date) AS last_order_date,
            SUM(so.total_price) AS total_spending
        FROM Customer c
        JOIN Shopping_Cart sc ON c.customer_id = sc.customer_id
        JOIN Sales_Order so ON sc.cart_id = so.cart_id
        GROUP BY c.customer_id, c.cname, c.gender, c.date_of_birth
        ORDER BY total_spending DESC
        LIMIT %s
        """
        cursor.execute(query, (top_n,))
        customers = cursor.fetchall()
    else:
        conditions = []
        params = []

        if customer_id:
            conditions.append("c.customer_id = %s")
            params.append(customer_id)
        if cname:
            conditions.append("c.cname LIKE %s")
            params.append(f"%{cname}%")
        if gender:
            conditions.append("c.gender = %s")
            params.append(gender)
        if dob:
            conditions.append("c.date_of_birth = %s")
            params.append(dob)
        if inactive_since:
            conditions.append("""
                NOT EXISTS (
                    SELECT 1 
                    FROM Shopping_Cart sc2 
                    JOIN Sales_Order so2 ON sc2.cart_id = so2.cart_id 
                    WHERE sc2.customer_id = c.customer_id 
                    AND so2.order_date >= %s
                )
            """)
            params.append(inactive_since)

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        query = f"""
        SELECT
            c.customer_id,
            c.cname,
            c.gender,
            c.date_of_birth,
            MAX(so.order_date) AS last_order_date,
            SUM(CASE WHEN so.payment_status IN ('Paid', 'Pending') THEN so.total_price ELSE 0 END) AS total_spending
        FROM Customer c
        LEFT JOIN Shopping_Cart sc ON c.customer_id = sc.customer_id
        LEFT JOIN Sales_Order so ON sc.cart_id = so.cart_id
        {where_clause}
        GROUP BY c.customer_id, c.cname, c.gender, c.date_of_birth
        """
        cursor.execute(query, params)
        customers = cursor.fetchall()

    # Bar Chart: All customers with total spending
    cursor.execute("""
        SELECT 
            c.cname,
            SUM(CASE WHEN so.payment_status IN ('Paid', 'Pending') THEN so.total_price ELSE 0 END) AS total_spending
        FROM Customer c
        JOIN Shopping_Cart sc ON c.customer_id = sc.customer_id
        JOIN Sales_Order so ON sc.cart_id = so.cart_id
        GROUP BY c.cname
        ORDER BY total_spending DESC
        LIMIT 30
    """)
    chart_data = cursor.fetchall()
    labels = [row['cname'] for row in chart_data]
    values = [round(float(row['total_spending']), 2) for row in chart_data]

    # Pie Chart: Spending by gender
    cursor.execute("""
        SELECT c.gender, SUM(so.total_price) AS total_spending
        FROM Customer c
        JOIN Shopping_Cart sc ON c.customer_id = sc.customer_id
        JOIN Sales_Order so ON sc.cart_id = so.cart_id
        WHERE so.payment_status IN ('Paid', 'Pending')
        GROUP BY c.gender
    """)
    gender_spend_data = cursor.fetchall()
    gender_spend_labels = ['Male' if row['gender'] == 'M' else 'Female' for row in gender_spend_data]
    gender_spend_totals = [float(row['total_spending']) for row in gender_spend_data]

    # Pie Chart: Spending by age group
    cursor.execute("""
        SELECT
            CASE
                WHEN TIMESTAMPDIFF(YEAR, c.date_of_birth, CURDATE()) < 18 THEN '< 18'
                WHEN TIMESTAMPDIFF(YEAR, c.date_of_birth, CURDATE()) BETWEEN 18 AND 50 THEN '18 - 50'
                ELSE '> 50'
            END AS age_group,
            SUM(so.total_price) AS total_spending
        FROM Customer c
        JOIN Shopping_Cart sc ON c.customer_id = sc.customer_id
        JOIN Sales_Order so ON sc.cart_id = so.cart_id
        WHERE so.payment_status IN ('Paid', 'Pending')
        GROUP BY age_group
    """)
    age_data = cursor.fetchall()
    age_labels = [row['age_group'] for row in age_data]
    age_totals = [float(row['total_spending']) for row in age_data]

    cursor.close()
    conn.close()

    return render_template(
        'customers.html',
        customers=customers,
        labels=labels,
        values=values,
        gender_spend_labels=gender_spend_labels,
        gender_spend_totals=gender_spend_totals,
        age_labels=age_labels,
        age_totals=age_totals
    )


@app.route('/api/top-customers')
def top_customers():
    if 'user_type' not in session or session['user_type'] != 'manager':
        flash("Access denied", "danger")
        return redirect(url_for('login'))

    n = request.args.get('n', default=1, type=int)
    if n <= 0:
        n = 1

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        c.customer_id, 
        c.cname, 
        SUM(so.total_price) AS total_spending
    FROM Customer c
    JOIN Shopping_Cart sc ON c.customer_id = sc.customer_id
    JOIN Sales_Order so ON sc.cart_id = so.cart_id
    WHERE so.payment_status = 'Completed'
    GROUP BY c.customer_id, c.cname
    ORDER BY total_spending DESC
    LIMIT %s
    """

    cursor.execute(query, (n,))
    top_customers = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(top_customers)

@app.route('/api/top-customers')
def api_top_customers():
    if 'user_type' not in session or session['user_type'] != 'manager':
        return jsonify({"error": "Access denied"}), 403

    n = request.args.get('n', default=5, type=int)
    if n <= 0:
        n = 5

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        c.customer_id, 
        c.cname AS first_name, 
        '' AS last_name, 
        SUM(so.total_price) AS total_spending
    FROM Customer c
    JOIN Shopping_Cart sc ON c.customer_id = sc.customer_id
    JOIN Sales_Order so ON sc.cart_id = so.cart_id
    WHERE so.payment_status = 'Completed'
    GROUP BY c.customer_id, c.cname
    ORDER BY total_spending DESC
    LIMIT %s
    """

    cursor.execute(query, (n,))
    top_customers = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(top_customers)

@app.route('/customer_spending_chart')
def customer_spending_chart():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    #number of customers with total spending
    cursor.execute("""
        SELECT c.cname, SUM(o.total_price) AS total_spending
        FROM Customer c
        LEFT JOIN Shopping_Cart sc ON c.customer_id = sc.customer_id
        LEFT JOIN Sales_Order o ON sc.cart_id = o.cart_id
        GROUP BY c.customer_id, c.cname
        ORDER BY total_spending DESC
        LIMIT 10

    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()
    #convert data to lists for chart rendering
    customer_names = [row['cname'] for row in data]
    spending_amounts = [float(row['total_spending'] or 0) for row in data]

    return render_template('customer_spending_chart.html',
                           customer_names=customer_names,
                           spending_amounts=spending_amounts)
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/employees', methods=['GET', 'POST'])
def employees():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    base_query = """
       SELECT E.employee_id, E.employee_name, E.employee_role, E.working_hours_per_week,
       IFNULL(SUM(SO.total_price), 0) AS total_sales,
       B.b_name AS branch_name
        FROM Employee E
        LEFT JOIN Branch B ON E.branch_id = B.branch_id
        LEFT JOIN Order_Assignment OA ON E.employee_id = OA.employee_id
        LEFT JOIN Sales_Order SO ON OA.order_id = SO.order_id

    """

    where_clauses = []
    having_clauses = []
    params = []

    # Top seller: override full query
    if request.method == 'POST' and request.form.get('top_seller') == '1':
        query = """
           SELECT E.employee_id, E.employee_name, E.employee_role, E.working_hours_per_week,
       SUM(SO.total_price) AS total_sales,
       B.b_name AS branch_name
    FROM Employee E
    JOIN Branch B ON E.branch_id = B.branch_id
    JOIN Order_Assignment OA ON E.employee_id = OA.employee_id
    JOIN Sales_Order SO ON OA.order_id = SO.order_id
    GROUP BY E.employee_id, E.employee_name, E.employee_role, E.working_hours_per_week, B.b_name
    ORDER BY total_sales DESC
    LIMIT 1

        """
        cursor.execute(query)
        employees = cursor.fetchall()
        cursor.close()
        return render_template('manage_employees.html', employees=employees)

    # Filters
    if request.method == 'POST':
        if request.form.get('min_sales'):
            having_clauses.append("SUM(SO.total_price) > %s")
            params.append(float(request.form['min_sales']))
        if request.form.get('min_hours'):
            where_clauses.append("E.working_hours_per_week > %s")
            params.append(int(request.form['min_hours']))
        if request.form.get('max_hours'):
            where_clauses.append("E.working_hours_per_week < %s")
            params.append(int(request.form['max_hours']))

    # Assemble final query
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    base_query += """
        GROUP BY E.employee_id, E.employee_name, E.employee_role, E.working_hours_per_week
    """

    if having_clauses:
        base_query += " HAVING " + " AND ".join(having_clauses)

    cursor.execute(base_query, params)
    employees = cursor.fetchall()
    cursor.close()

    names = [e['employee_name'] for e in employees]
    sales = [float(e['total_sales']) for e in employees]
    hours = [int(e['working_hours_per_week']) for e in employees]
   
    return render_template('manage_employees.html', employees=employees, names=names, sales=sales, hours=hours)


@app.route("/manage_products", methods=["GET", "POST"])
def manage_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    all_products = []
    trending_products = []
    highest_rated = []
    most_reviewed = []
    least_selling = []
    best_categories = []
    worst_categories = []

    message = None 

    if request.method == "POST":
        action = request.form["action"]
        product_id = request.form.get("product_id")

        #check if product_id is provided
        cursor.execute("SELECT * FROM Product WHERE product_id = %s", (product_id,))
        product_exists = cursor.fetchone() is not None

        if action == "Insert":
            if product_exists:
                message = f"Error: Product ID {product_id} already exists."
            else:
                pname = request.form["pname"]
                price = request.form["price"]
                
                try:
                    price = float(request.form["price"])

                except ValueError:
                    message = "Price must be a number."
                    return render_template("manage_products.html", message=message)

                if price < 0:
                    message = "Price cannot be negative."
                    return render_template("manage_products.html", message=message)
                
                purchases = request.form["num_of_purchases"]
                
                    
                
                is_trending = 1 if "is_trending" in request.form else 0
                category_name = request.form["category_name"].lower()

                cursor.execute("""
                    INSERT INTO Product (product_id, pname, price, num_of_purchases, is_trending)
                    VALUES (%s, %s, %s, %s, %s)
                """, (product_id, pname, price, purchases, is_trending))
                conn.commit()

                if category_name == "fragrance":
                    cursor.execute("INSERT INTO Fragrance (product_id) VALUES (%s)", (product_id,))
                elif category_name == "skincare":
                    cursor.execute("INSERT INTO Skincare_Product (product_id) VALUES (%s)", (product_id,))
                elif category_name == "haircare":
                    cursor.execute("INSERT INTO Hair_Product (product_id) VALUES (%s)", (product_id,))
                conn.commit()
                message = f"Product {product_id} inserted successfully."

        elif action == "Update":
            if not product_exists:
                message = f"Error: Product ID {product_id} does not exist."
            else:
                updates = []
                params = []

                if request.form.get("pname"):
                    updates.append("pname = %s")
                    params.append(request.form["pname"])

                if request.form.get("price"):
                    updates.append("price = %s")
                    params.append(request.form["price"])

                if request.form.get("num_of_purchases"):
                    updates.append("num_of_purchases = %s")
                    params.append(request.form["num_of_purchases"])

                if "is_trending" in request.form:
                    updates.append("is_trending = %s")
                    params.append(1)
                else:
                    updates.append("is_trending = %s")
                    params.append(0)

                if updates:
                    params.append(product_id)
                    cursor.execute(f"""
                        UPDATE Product SET {', '.join(updates)} WHERE product_id = %s
                    """, params)
                    conn.commit()
                    message = f"Product {product_id} updated successfully."
                else:
                    message = "No fields to update."

        elif action == "Delete":
            if not product_exists:
                message = f"Error: Product ID {product_id} does not exist."
            else:
                cursor.execute("DELETE FROM Product WHERE product_id = %s", (product_id,))
                cursor.execute("DELETE FROM Fragrance WHERE product_id = %s", (product_id,))
                cursor.execute("DELETE FROM Skincare_Product WHERE product_id = %s", (product_id,))
                cursor.execute("DELETE FROM Hair_Product WHERE product_id = %s", (product_id,))
                conn.commit()
                message = f"Product {product_id} deleted successfully."

    # ---------------------------
    # Fetch all products with category name
    cursor.execute("""
        SELECT P.*, 
               CASE 
                   WHEN FP.product_id IS NOT NULL THEN 'Fragrance'
                   WHEN SP.product_id IS NOT NULL THEN 'Skincare'
                   WHEN HP.product_id IS NOT NULL THEN 'Haircare'
                   ELSE 'Unknown'
               END AS category_name
        FROM Product P
        LEFT JOIN Fragrance FP ON P.product_id = FP.product_id
        LEFT JOIN Skincare_Product SP ON P.product_id = SP.product_id
        LEFT JOIN Hair_Product HP ON P.product_id = HP.product_id
    """)
    all_products = cursor.fetchall()

    # Fetch trending products with category name
    cursor.execute("""
        SELECT P.*, 
               CASE 
                   WHEN FP.product_id IS NOT NULL THEN 'Fragrance'
                   WHEN SP.product_id IS NOT NULL THEN 'Skincare'
                   WHEN HP.product_id IS NOT NULL THEN 'Haircare'
                   ELSE 'Unknown'
               END AS category_name
        FROM Product P
        LEFT JOIN Fragrance FP ON P.product_id = FP.product_id
        LEFT JOIN Skincare_Product SP ON P.product_id = SP.product_id
        LEFT JOIN Hair_Product HP ON P.product_id = HP.product_id
        WHERE P.is_trending = 1
    """)
    trending_products = cursor.fetchall()

    # Highest-rated products
    cursor.execute("""
        SELECT 
            P.product_id, 
            P.pname, 
            P.price,  
            AVG(R.rating) AS avg_rating
        FROM Product P
        JOIN Review R ON P.product_id = R.product_id
        GROUP BY P.product_id
        ORDER BY avg_rating DESC
        LIMIT 10
    """)
    highest_rated = cursor.fetchall()

    # Most reviewed products
    cursor.execute("""
        SELECT 
            P.product_id, 
            P.pname, 
            P.price, 
            COUNT(R.rating) AS review_count
        FROM Product P
        JOIN Review R ON P.product_id = R.product_id
        GROUP BY P.product_id
        ORDER BY review_count DESC
        LIMIT 10
    """)
    most_reviewed = cursor.fetchall()

    # Least-selling products
    cursor.execute("""
        SELECT 
            P.product_id, 
            P.pname, 
            P.price, 
            IFNULL(SUM(CP.quantity), 0) AS total_sold
        FROM Product P
        LEFT JOIN Cart_Product CP ON P.product_id = CP.product_id
        GROUP BY P.product_id
        ORDER BY total_sold ASC
        LIMIT 10
    """)
    least_selling = cursor.fetchall()

    # Best and worst performing categories
    cursor.execute("""
        SELECT 'Fragrance' AS category_name, SUM(P.num_of_purchases) AS total_sales
        FROM Product P JOIN Fragrance F ON P.product_id = F.product_id
        UNION
        SELECT 'Skincare', SUM(P.num_of_purchases)
        FROM Product P JOIN Skincare_Product S ON P.product_id = S.product_id
        UNION
        SELECT 'Haircare', SUM(P.num_of_purchases)
        FROM Product P JOIN Hair_Product H ON P.product_id = H.product_id
        ORDER BY total_sales DESC
    """)
    categories = cursor.fetchall()
    best_category = categories[0] if categories else None
    worst_category = categories[-1] if len(categories) >= 2 else None


    

    return render_template("manage_products.html",
                           all_products=all_products,
                           trending_products=trending_products,
                           highest_rated=highest_rated,
                           most_reviewed=most_reviewed,
                           least_selling=least_selling,
                            best_category= best_category,
                           worst_category=worst_category,
                           message=message)




@app.route('/branches')
def branches():
    filter_type = request.args.get('filter', 'all') 

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    base_query = """
        SELECT b.branch_id, b.b_name AS branch_name, p.product_id, p.pname AS product_name, bp.stock_quantity
        FROM Branch b
        JOIN Branch_Product bp ON b.branch_id = bp.branch_id
        JOIN Product p ON bp.product_id = p.product_id
    """

    if filter_type == 'out_of_stock':
        base_query += " WHERE bp.stock_quantity = 0"
    elif filter_type == 'low_stock':
        base_query += " WHERE bp.stock_quantity > 0 AND bp.stock_quantity < 20"

    base_query += " ORDER BY b.branch_id, p.product_id;"

    cursor.execute(base_query)
    rows = cursor.fetchall()

    employee_rows = []

    if filter_type == 'all':
        cursor.execute("""
            SELECT e.employee_id, e.employee_name, e.employee_role, 
                e.hire_date, e.working_hours_per_week, e.is_manager, e.branch_id
            FROM Employee e
            ORDER BY e.branch_id, e.employee_id;
        """)
        employee_rows = cursor.fetchall()


    conn.close()

    branches = {}
    for row in rows:
        branch_id = row['branch_id']
        if branch_id not in branches:
            branches[branch_id] = {
                'branch_name': row['branch_name'],
                'products': [],
                'employees': []
            }

        quantity = row['stock_quantity']
        if quantity == 0:
            status = 'Out of Stock'
        elif quantity < 20:
            status = 'Low Stock'
        else:
            status = 'In Stock'

        branches[branch_id]['products'].append({
            'product_id': row['product_id'],
            'product_name': row['product_name'],
            'quantity': quantity,
            'status': status
        })

    for emp in employee_rows:
        branch_id = emp['branch_id']
        if branch_id in branches:
            branches[branch_id]['employees'].append({
                'employee_id': emp['employee_id'],
                'employee_name': emp['employee_name'],
                'employee_role': emp['employee_role'],
                'hire_date': emp['hire_date'],
                'working_hours_per_week': emp['working_hours_per_week'],
                'is_manager': emp['is_manager']
            })

    return render_template('branches.html', branches=branches, filter_type=filter_type)
@app.route('/orders')
def orders():
    payment_filter = request.args.get('payment_status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    min_total = request.args.get('min_total', type=float)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            so.order_id,
            so.order_date,
            so.expected_receive_date,
            so.shipment_date,
            so.total_price,
            so.payment_status,
            c.cname AS customer_name,
            e.employee_name AS employee_name,
            b.b_name AS branch_name
        FROM sales_order so
        LEFT JOIN shopping_cart sc ON so.cart_id = sc.cart_id
        LEFT JOIN customer c ON sc.customer_id = c.customer_id
        LEFT JOIN order_assignment oa ON so.order_id = oa.order_id
        LEFT JOIN employee e ON oa.employee_id = e.employee_id
        LEFT JOIN branch b ON e.branch_id = b.branch_id
        WHERE 1=1
    """

    filters = []

    if payment_filter:
        query += " AND so.payment_status = %s"
        filters.append(payment_filter)

    if date_from:
        query += " AND so.order_date >= %s"
        filters.append(date_from)

    if date_to:
        query += " AND so.order_date <= %s"
        filters.append(date_to)

    if min_total is not None:
        query += " AND so.total_price >= %s"
        filters.append(min_total)

    query += " ORDER BY so.order_date DESC"

    cursor.execute(query, filters)
    orders = cursor.fetchall()

    #get order details for each order
    order_ids = [o['order_id'] for o in orders]
    order_details = {}
    if order_ids:
        format_strings = ','.join(['%s'] * len(order_ids))
        cursor.execute(f"""
            SELECT ol.order_id, p.pname, ol.quantity, ol.price_at_order_time
            FROM order_line ol
            JOIN product p ON ol.product_id = p.product_id
            WHERE ol.order_id IN ({format_strings})
        """, order_ids)

        for row in cursor.fetchall():
            order_id = row['order_id']
            if order_id not in order_details:
                order_details[order_id] = []
            order_details[order_id].append({
                'product_name': row['pname'],
                'quantity': row['quantity'],
                'price': row['price_at_order_time']
            })

    conn.close()

    # devide orders into peak periods
    peak_periods = {
        "12–3 AM": 0,
        "3–6 AM": 0,
        "6–9 AM": 0,
        "9–12 PM": 0,
        "12–3 PM": 0,
        "3–6 PM": 0,
        "6–9 PM": 0,
        "9–12 AM": 0
    }

    def get_period(hour):
        if 0 <= hour < 3:
            return "12–3 AM"
        elif 3 <= hour < 6:
            return "3–6 AM"
        elif 6 <= hour < 9:
            return "6–9 AM"
        elif 9 <= hour < 12:
            return "9–12 PM"
        elif 12 <= hour < 15:
            return "12–3 PM"
        elif 15 <= hour < 18:
            return "3–6 PM"
        elif 18 <= hour < 21:
            return "6–9 PM"
        else:  # 21-23
            return "9–12 AM"

    for order in orders:
        hour = order['order_date'].hour
        period = get_period(hour)
        peak_periods[period] += 1
        order['peak_time'] = period

    peak_time = max(peak_periods, key=peak_periods.get)
    peak_count = peak_periods[peak_time]

    return render_template(
        'orders.html',
        orders=orders,
        order_details=order_details,
        payment_filter=payment_filter,
        date_from=date_from,
        date_to=date_to,
        min_total=min_total,
        peak_periods=peak_periods,
        peak_time=peak_time,
        peak_count=peak_count
    )


@app.route('/suppliers')
def suppliers():
    company_filter = request.args.get('company_name')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT supplier_id, email, company_name FROM Supplier WHERE 1=1"
    filters = []

    if company_filter:
        query += " AND company_name LIKE %s"
        filters.append(f"%{company_filter}%")

    query += " ORDER BY company_name"

    cursor.execute(query, filters)
    suppliers = cursor.fetchall()
    conn.close()

    return render_template(
        'suppliers.html',
        suppliers=suppliers,
        company_filter=company_filter
    )


if __name__ == '__main__':
    app.run(debug=True)

