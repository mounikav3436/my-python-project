from pydantic_settings import BaseSettings
import mysql.connector
from enum import Enum
from datetime import datetime


#  Load DB settings from .env
class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_user: str
    db_password: str 
    db_name: str

    class Config:
        env_file = ".env"

settings = Settings()

#  User roles
class Role(str, Enum):
    admin = "Admin"
    customer = "Customer"

#  MySQL connection 
def get_connection(db=None):
    config = {
        "host": settings.db_host,
        "port": settings.db_port,
        "user": settings.db_user,
        "password": settings.db_password,
    }
    if db:
        config["database"] = db
    return mysql.connector.connect(**config)

# Create database if not exists
def create_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.db_name}")
    conn.commit()
    cursor.close()
    conn.close()

# Create users table
def create_users_table():
    conn = get_connection(settings.db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role ENUM('Admin', 'Customer') NOT NULL,
            email VARCHAR(100),
            age INT,
            contact_number VARCHAR(15),
            city VARCHAR(50),
            state VARCHAR(50),
            pincode VARCHAR(10)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

#  Create products table
def create_products_table():
    conn = get_connection(settings.db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            subcategory VARCHAR(50) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            stock INT NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

#  Create orders table
def create_orders_table():
    conn = get_connection(settings.db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL,
            status VARCHAR(20) DEFAULT 'Placed',
            requested_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            shipping_city VARCHAR(100),
            shipping_state VARCHAR(100),
            shipping_pincode VARCHAR(20),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


#  products into DB
def populate_products():
    # Define products grouped by category & subcategory
    product_data = {
        "Personal Care": {
            "Skin Care": [
                ("Aloe Vera Gel", 199.00, 50),
                ("Face Wash", 149.00, 40),
                ("Moisturizer", 299.00, 30),
            ],
            "Hand and Foot care": [
                ("Hand Cream", 250.00, 25),
                ("Foot Scrub", 270.00, 20),
            ],
            "Oral Care": [
                ("Toothpaste", 99.00, 60),
                ("Mouthwash", 199.00, 45),
            ],
            "Hair care": [
                ("Shampoo", 350.00, 35),
                ("Conditioner", 320.00, 30),
            ],
        },
        "Nutrition": {
            "Special Nutrition Needs": [
                ("Gluten-Free Protein Bar", 120.00, 50),
                ("Infant Formula", 450.00, 25),
            ],
            "Sports Nutrition": [
                ("Whey Protein", 1500.00, 40),
                ("Energy Drink", 99.00, 70),
            ],
            "Vitamins and Supplements": [
                ("Vitamin C Tablets", 350.00, 60),
                ("Omega 3 Capsules", 400.00, 55),
            ],
            "Weight Management": [
                ("Fat Burner Capsules", 999.00, 30),
                ("Meal Replacement Shake", 850.00, 20),
            ],
        },
        "Health Care": {
            "Diabetes Management": [
                ("Glucometer", 1200.00, 15),
                ("Insulin Pen", 2000.00, 10),
            ],
            "Health Accessories": [
                ("Digital Thermometer", 800.00, 25),
                ("Blood Pressure Monitor", 2500.00, 10),
            ],
            "Home Testing Kit": [
                ("COVID-19 Rapid Test Kit", 500.00, 35),
                ("Pregnancy Test Kit", 300.00, 50),
            ],
        },
    }

    conn = get_connection(settings.db_name)
    cursor = conn.cursor()

    # Insert products if not already present
    for category, subcats in product_data.items():
        for subcat, items in subcats.items():
            for name, price, stock in items:
                cursor.execute("""
                    SELECT id FROM products WHERE name=%s AND category=%s AND subcategory=%s
                """, (name, category, subcat))
                if cursor.fetchone():
                    continue  # Product exists
                cursor.execute("""
                    INSERT INTO products (name, category, subcategory, price, stock)
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, category, subcat, price, stock))
    conn.commit()
    cursor.close()
    conn.close()
def add_new_product():
    print("\n🆕 Add New Product")
    name = input("Enter product name: ").strip()
    category = input("Enter category (e.g., Personal Care, Nutrition, Health Care): ").strip()
    subcategory = input("Enter subcategory (e.g., Skin Care, Vitamins): ").strip()

    try:
        price = float(input("Enter price (e.g., 199.99): ").strip())
        stock = int(input("Enter initial stock quantity: ").strip())
    except ValueError:
        print("❌ Invalid price or stock input.")
        return

    conn = get_connection(settings.db_name)
    cursor = conn.cursor()

    try:
        # Check if product already exists
        cursor.execute("""
            SELECT id FROM products WHERE name = %s AND category = %s AND subcategory = %s
        """, (name, category, subcategory))
        if cursor.fetchone():
            print("⚠️ Product already exists in this category/subcategory.")
        else:
            cursor.execute("""
                INSERT INTO products (name, category, subcategory, price, stock)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, category, subcategory, price, stock))
            conn.commit()
            print("✅ Product added successfully.")
    except mysql.connector.Error as err:
        print(f"❌ Error adding product: {err}")
    finally:
        cursor.close()
        conn.close()

# Register
def register():
    print("\n📋 Register New User")
    role_input = input("Role (Admin/Customer): ").capitalize()
    if role_input not in [r.value for r in Role]:
        print("❌ Invalid role.")
        return
    user_id = input("User ID: ")
    password = input("Password: ")
    email = input("Email ID: ")
    try:
        age = int(input("Age: "))
    except ValueError:
        print("❌ Invalid age.")
        return
    contact = input("Contact Number: ")
    city = input("City: ")
    state = input("State: ")
    pincode = input("Pincode: ")
    conn = get_connection(settings.db_name)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (user_id, password, role, email, age, contact_number, city, state, pincode)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, password, role_input, email, age, contact, city, state, pincode))
        conn.commit()
        print("✅ Registered successfully.")
    except mysql.connector.Error as err:
        print(f"❌ Registration error: {err}")
    finally:
        cursor.close()
        conn.close()

#  Login and redirect
def login():
    print("\n🔐 User Login")
    role_input = input("Role (Admin/Customer): ").capitalize()
    user_id = input("User ID: ")
    password = input("Password: ")
    conn = get_connection(settings.db_name)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users WHERE user_id = %s AND password = %s AND role = %s
    """, (user_id, password, role_input))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        print(f"✅ Login successful! Welcome {role_input} {user_id}.")
        if role_input == Role.customer.value:
            customer_menu(user_id)
        else:
            admin_menu()
    else:
        print("❌ Invalid credentials.")

#  View products by category/subcategory
def view_products():
    conn = get_connection(settings.db_name)
    cursor = conn.cursor()

    # Get all unique categories
    cursor.execute("SELECT DISTINCT LOWER(TRIM(category)) FROM products")
    categories = [row[0] for row in cursor.fetchall()]

    if not categories:
        print("⚠️ No categories available.")
        return []

    print("\n🛒 Categories:")
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat}")
    try:
        cat_index = int(input("Select category number: ")) - 1
        selected_cat = categories[cat_index]
    except (ValueError, IndexError):
        print("❌ Invalid category choice.")
        return []

    # Get subcategories for selected category
    cursor.execute("SELECT DISTINCT subcategory FROM products WHERE category = %s", (selected_cat,))
    subcategories = [row[0] for row in cursor.fetchall()]
    if not subcategories:
        print("⚠️ No subcategories found.")
        return []

    print(f"\nSubcategories under {selected_cat}:")
    for i, subcat in enumerate(subcategories, 1):
        print(f"{i}. {subcat}")
    try:
        subcat_index = int(input("Select subcategory number: ")) - 1
        selected_subcat = subcategories[subcat_index]
    except (ValueError, IndexError):
        print("❌ Invalid subcategory choice.")
        return []

    # Show products in that category & subcategory
    cursor.execute("""
        SELECT id, name, price, stock FROM products
        WHERE category = %s AND subcategory = %s AND stock > 0
    """, (selected_cat, selected_subcat))
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    if not products:
        print("⚠️ No products found in this category/subcategory.")
        return []

    print("\nAvailable Products:")
    print(f"{'ID':<5} {'Name':<30} {'Price':<10} {'Stock':<5}")
    for prod in products:
        print(f"{prod[0]:<5} {prod[1]:<30} {prod[2]:<10} {prod[3]:<5}")

    return products

# Place order
def place_order(user_id=None):
    products = view_products()
    if not products:
        return
    product_id = input("\nEnter the Product ID to order: ").strip()
    quantity = input("Enter quantity: ").strip()
    try:
        product_id = int(product_id)
        quantity = int(quantity)
        if quantity <= 0:
            print("⚠️ Quantity must be positive.")
            return
    except ValueError:
        print("⚠️ Invalid input.")
        return

    conn = get_connection(settings.db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT stock FROM products WHERE id = %s", (product_id,))
    result = cursor.fetchone()
    if not result:
        print("❌ Product not found.")
        cursor.close()
        conn.close()
        return
    stock = result[0]
    if stock < quantity:
        print(f"❌ Only {stock} items in stock.")
        cursor.close()
        conn.close()
        return

    # If admin placing order, ask for customer user_id and shipping address
    if user_id is None:
        user_id = input("Enter Customer User ID for placing order: ").strip()
        # Fetch customer shipping info
        cursor.execute("SELECT city, state, pincode FROM users WHERE user_id = %s", (user_id,))
        cust_info = cursor.fetchone()
        if not cust_info:
            print("❌ Customer not found.")
            cursor.close()
            conn.close()
            return
        shipping_city, shipping_state, shipping_pincode = cust_info
    else:
        # For customer placing order, use their own address
        cursor.execute("SELECT city, state, pincode FROM users WHERE user_id = %s", (user_id,))
        shipping_city, shipping_state, shipping_pincode = cursor.fetchone()

    try:
        cursor.execute("""
            INSERT INTO orders (user_id, product_id, quantity, status, shipping_city, shipping_state, shipping_pincode)
            VALUES (%s, %s, %s, 'Placed', %s, %s, %s)
        """, (user_id, product_id, quantity, shipping_city, shipping_state, shipping_pincode))
        cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (quantity, product_id))
        conn.commit()
        print("✅ Order placed successfully.")
    except mysql.connector.Error as err:
        print(f"❌ Error placing order: {err}")
    finally:
        cursor.close()
        conn.close()
def delete_product():
    conn = get_connection(settings.db_name)
    cursor = conn.cursor()

    # Step 1: Fetch and show categories
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = [row[0] for row in cursor.fetchall()]
    if not categories:
        print("⚠️ No categories found.")
        return
        
    print("\n🗃️ Categories:")
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat}")
    try:
        cat_choice = int(input("Select category number: ")) - 1
        selected_cat = categories[cat_choice]
    except (ValueError, IndexError):
        print("❌ Invalid choice.")
        return

    # Step 2: Fetch and show subcategories
    cursor.execute("SELECT DISTINCT subcategory FROM products WHERE category = %s", (selected_cat,))
    subcategories = [row[0] for row in cursor.fetchall()]
    if not subcategories:
        print("⚠️ No subcategories found.")
        return

    print(f"\nSubcategories under {selected_cat}:")
    for i, subcat in enumerate(subcategories, 1):
        print(f"{i}. {subcat}")
    try:
        subcat_choice = int(input("Select subcategory number: ")) - 1
        selected_subcat = subcategories[subcat_choice]
    except (ValueError, IndexError):
        print("❌ Invalid choice.")
        return

    # Step 3: Fetch and show products
    cursor.execute("""
        SELECT id, name, price, stock FROM products
        WHERE category = %s AND subcategory = %s
    """, (selected_cat, selected_subcat))
    products = cursor.fetchall()
    if not products:
        print("⚠️ No products found.")
        return

    print(f"\nProducts in {selected_cat} > {selected_subcat}:")
    print(f"{'ID':<5} {'Name':<30} {'Price':<10} {'Stock':<5}")
    for prod in products:
        print(f"{prod[0]:<5} {prod[1]:<30} {prod[2]:<10} {prod[3]:<5}")

    try:
        prod_id = int(input("Enter the Product ID to delete: "))
    except ValueError:
        print("❌ Invalid product ID.")
        return

    # Confirm deletion
    cursor.execute("SELECT name FROM products WHERE id = %s", (prod_id,))
    product = cursor.fetchone()
    if not product:
        print("❌ Product not found.")
        return

    confirm = input(f"Are you sure you want to delete '{product[0]}'? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❎ Deletion cancelled.")
        return

    # Delete product
    try:
        cursor.execute("DELETE FROM products WHERE id = %s", (prod_id,))
        conn.commit()
        print("✅ Product deleted successfully.")
    except mysql.connector.Error as err:
        print(f"❌ Error deleting product: {err}")
    finally:
        cursor.close()
        conn.close()

# Update order (customer only)
def update_order(user_id):
    conn = get_connection(settings.db_name)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.id, p.name, o.quantity, o.status
        FROM orders o JOIN products p ON o.product_id = p.id
        WHERE o.user_id = %s AND o.status != 'Cancelled'
    """, (user_id,))
    orders = cursor.fetchall()

    if not orders:
        print("You have no active orders to update.")
        cursor.close()
        conn.close()
        return

    print("\nYour Active Orders:")
    print(f"{'Order ID':<10} {'Product':<30} {'Quantity':<10} {'Status':<10}")
    for order in orders:
        print(f"{order[0]:<10} {order[1]:<30} {order[2]:<10} {order[3]:<10}")

    try:
        order_id = int(input("Enter Order ID to update: "))
    except ValueError:
        print("⚠️ Invalid Order ID.")
        cursor.close()
        conn.close()
        return

    # Check order belongs to user and is not cancelled
    cursor.execute("SELECT product_id, quantity, status FROM orders WHERE id = %s AND user_id = %s AND status != 'Cancelled'", (order_id, user_id))
    order = cursor.fetchone()
    if not order:
        print("❌ Order not found or cannot be updated.")
        cursor.close()
        conn.close()
        return

    product_id, old_quantity, status = order
    print(f"Current quantity: {old_quantity}")
    try:
        new_quantity = int(input("Enter new quantity: "))
        if new_quantity <= 0:
            print("⚠️ Quantity must be positive.")
            cursor.close()
            conn.close()
            return
    except ValueError:
        print("⚠️ Invalid quantity.")
        cursor.close()
        conn.close()
        return

    # Check stock availability difference
    diff = new_quantity - old_quantity
    if diff > 0:
        cursor.execute("SELECT stock FROM products WHERE id = %s", (product_id,))
        stock = cursor.fetchone()[0]
        if stock < diff:
            print(f"❌ Only {stock} items left in stock.")
            cursor.close()
            conn.close()
            return

    try:
        # Update order quantity
        cursor.execute("UPDATE orders SET quantity = %s, status = 'Updated' WHERE id = %s", (new_quantity, order_id))
        # Update stock accordingly
        cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (diff, product_id))
        conn.commit()
        print("✅ Order updated successfully.")
    except mysql.connector.Error as err:
        print(f"❌ Error updating order: {err}")
    finally:
        cursor.close()
        conn.close()

# Cancel order (customer only)
def cancel_order(user_id):
    conn = get_connection(settings.db_name)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.id, p.name, o.quantity, o.status
        FROM orders o JOIN products p ON o.product_id = p.id
        WHERE o.user_id = %s AND o.status != 'Cancelled'
    """, (user_id,))
    orders = cursor.fetchall()

    if not orders:
        print("You have no active orders to cancel.")
        cursor.close()
        conn.close()
        return

    print("\nYour Active Orders:")
    print(f"{'Order ID':<10} {'Product':<30} {'Quantity':<10} {'Status':<10}")
    for order in orders:
        print(f"{order[0]:<10} {order[1]:<30} {order[2]:<10} {order[3]:<10}")

    try:
        order_id = int(input("Enter Order ID to cancel: "))
    except ValueError:
        print("⚠️ Invalid Order ID.")
        cursor.close()
        conn.close()
        return

    cursor.execute("SELECT product_id, quantity, status FROM orders WHERE id = %s AND user_id = %s AND status != 'Cancelled'", (order_id, user_id))
    order = cursor.fetchone()
    if not order:
        print("❌ Order not found or already cancelled.")
        cursor.close()
        conn.close()
        return

    product_id, quantity, status = order
    try:
        cursor.execute("UPDATE orders SET status = 'Cancelled' WHERE id = %s", (order_id,))
        cursor.execute("UPDATE products SET stock = stock + %s WHERE id = %s", (quantity, product_id))
        conn.commit()
        print("✅ Order cancelled successfully.")
    except mysql.connector.Error as err:
        print(f"❌ Error cancelling order: {err}")
    finally:
        cursor.close()
        conn.close()

# View orders (both customer & admin)
def view_orders(user_id=None, admin=False):
    conn = get_connection(settings.db_name)
    cursor = conn.cursor()

    if admin:
        cursor.execute("""
            SELECT o.id, o.user_id, p.name, o.quantity, o.status, o.requested_date, o.shipping_city, o.shipping_state, o.shipping_pincode
            FROM orders o JOIN products p ON o.product_id = p.id
            ORDER BY o.requested_date DESC
        """)
        orders = cursor.fetchall()
        print("\nAll Orders:")
        print(f"{'Order ID':<10} {'User ID':<15} {'Product':<30} {'Qty':<5} {'Status':<10} {'Date':<20} {'Shipping Address':<30}")
        for order in orders:
            shipping = f"{order[6]}, {order[7]}, {order[8]}"
            print(f"{order[0]:<10} {order[1]:<15} {order[2]:<30} {order[3]:<5} {order[4]:<10} {order[5].strftime('%Y-%m-%d %H:%M'):<20} {shipping:<30}")
    else:
        cursor.execute("""
            SELECT o.id, p.name, o.quantity, o.status, o.requested_date, o.shipping_city, o.shipping_state, o.shipping_pincode
            FROM orders o JOIN products p ON o.product_id = p.id
            WHERE o.user_id = %s
            ORDER BY o.requested_date DESC
        """, (user_id,))
        orders = cursor.fetchall()
        print("\nYour Orders:")
        print(f"{'Order ID':<10} {'Product':<30} {'Qty':<5} {'Status':<10} {'Date':<20} {'Shipping Address':<30}")
        for order in orders:
            shipping = f"{order[5]}, {order[6]}, {order[7]}"
            print(f"{order[0]:<10} {order[1]:<30} {order[2]:<5} {order[3]:<10} {order[4].strftime('%Y-%m-%d %H:%M'):<20} {shipping:<30}")

    cursor.close()
    conn.close()

# Customer menu
def customer_menu(user_id):
    while True:
        print("""
Customer Menu:
1. 🔎👀 View Products
2. 🛍🛒 Place Order
3. ⏩ Update Order
4. ❎ Cancel Order
5. 👁‍🗨 View My Orders
6. 🔒👋 Logout
        """)
        choice = input("Enter choice: ").strip()
        if choice == "1":
            view_products()
        elif choice == "2":
            place_order(user_id)
        elif choice == "3":
            update_order(user_id)
        elif choice == "4":
            cancel_order(user_id)
        elif choice == "5":
            view_orders(user_id)
        elif choice == "6":
            print("Logging out...")
            break
        else:
            print("Invalid choice, try again.")
def admin_view_order_by_id():
    order_id = input("Enter the Order ID to view: ").strip()
    
    conn = get_connection(settings.db_name)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT o.id, o.user_id, p.name, o.quantity, o.status, o.requested_date, o.shipping_city, o.shipping_state, o.shipping_pincode
            FROM orders o JOIN products p ON o.product_id = p.id
            WHERE o.id = %s
        """, (order_id,))
        
        order = cursor.fetchone()
        
        if order:
            (order_id, user_id, product_name, quantity, status, 
             requested_date, shipping_city, shipping_state, shipping_pincode) = order
             
            print("\nOrder Details:")
            print(f"Order ID        : {order_id}")
            print(f"User ID         : {user_id}")
            print(f"Product Name    : {product_name}")
            print(f"Quantity        : {quantity}")
            print(f"Status          : {status}")
            print(f"Requested Date  : {requested_date.strftime('%Y-%m-%d %H:%M:%S') if requested_date else 'N/A'}")
            print(f"Shipping City   : {shipping_city if shipping_city else 'N/A'}")
            print(f"Shipping State  : {shipping_state if shipping_state else 'N/A'}")
            print(f"Shipping Pincode: {shipping_pincode if shipping_pincode else 'N/A'}")
        else:
            print("❌ No order found with that Order ID.")
    except mysql.connector.Error as err:
        print(f"❌ Error fetching order details: {err}")
    finally:
        cursor.close()
        conn.close()

# Admin menu
def admin_menu():
    while True:
        print("""
Admin Menu:
1. 🕵🏼🔎 View Products
2. ➡️ Place Order for Customer
3. 🛍 View All Orders
4. 👩🏻‍💻 Register New User
5. 📩 Add New Product
6. 🗑 Delete Product
7. 🔒 Logout
        """)
        choice = input("Enter choice: ").strip()
        if choice == "1":
            view_products()
        elif choice == "2":
            place_order(None)
        elif choice == "3":
            view_orders(admin=True)
        elif choice == "4":
            register()
        elif choice == "5":
            add_new_product()
        elif choice == "6":
            delete_product()
        elif choice == "7":
            print("Logging out...")
            break
        else:
            print("Invalid choice 👎, try again.")

# Initial setup and main loop
def main():
    print("***WELCOME TO 💊 PHARMACY 🧬 STORE ***")
    create_database()
    create_users_table()
    create_products_table()
    create_orders_table()
    populate_products()

    while True:
        print("""
Main Menu:
1. 📝Register
2. 🔐 Login
3. ❌ Exit
        """)
        choice = input("Enter choice: ").strip()
        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            print(" 🙏 THANKYOU BYE!")
            break
        else:
            print("👎Invalid choice, try again.")

if __name__ == "__main__":
    main()
   
       
