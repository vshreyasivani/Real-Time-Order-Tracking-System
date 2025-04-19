from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.static_folder = 'static'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'SivaniCSE5002$',
    'database': 'Order_Tracking'
}

# Database connection
def create_db_connection():
    return mysql.connector.connect(**db_config)

# Decorators for access control
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin', False):
            flash('Admin access required!')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Basic routes
@app.route('/')
def home():
    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        middle_name = request.form.get('middle_name', '')
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        contact_info = request.form['contact_info']
        house_no = request.form['house_no']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        
        connection = create_db_connection()
        cursor = connection.cursor()
        
        try:
            # Check for existing email
            cursor.execute("SELECT Customer_ID FROM customer WHERE Email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered!')
                return redirect(url_for('signup'))
            
            # Get new customer ID
            cursor.execute("SELECT MAX(Customer_ID) FROM customer")
            max_id = cursor.fetchone()[0]
            new_id = 1 if max_id is None else max_id + 1
            
            # Insert new customer
            cursor.execute("""
                INSERT INTO customer (Customer_ID, First_Name, Middle_Name, Last_Name, 
                Contact_Info, House_No_Room_No, Street, City, State, Email, Password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (new_id, first_name, middle_name, last_name, contact_info, 
                  house_no, street, city, state, email, password))
            # Insert contact info into contact_info table
            cursor.execute("""
                INSERT INTO contact_info (Customer_ID, Contact_No)
                VALUES (%s, %s)
            """, (new_id, contact_info))
            connection.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('home'))
        except Exception as e:
            connection.rollback()
            flash(f'Registration failed: {str(e)}')
        finally:
            cursor.close()
            connection.close()
            
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    connection = create_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT Customer_ID, First_Name, Email FROM customer WHERE Email = %s AND Password = %s", 
        (username, password)
    )
    user = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if user:
        customer_id, first_name, email = user
        session['username'] = first_name
        session['email'] = email
        session['customer_id'] = customer_id
        
        if email == 'admin@rtots.com':
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            session['is_admin'] = False
            return redirect(url_for('user_dashboard'))
    else:
        flash('Invalid username or password!')
        return redirect(url_for('home'))

@app.route('/admin_dashboard', methods=['GET', 'POST'])
@admin_required
def admin_dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    connection = create_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Handle POST request for updating location
    if request.method == 'POST':
        for tracking in tracking_data:
            tracking_id = tracking['Tracking_ID']
            new_location = request.form.get(f'current_location_{tracking_id}')
            
            if new_location:
                # Update the location in the database
                cursor.execute("""
                    UPDATE tracking_info 
                    SET Current_Location = %s 
                    WHERE Tracking_ID = %s
                """, (new_location, tracking_id))
                connection.commit()
                
                # Show a flash message
                flash(f"Location for Tracking ID #{tracking_id} updated to {new_location}!", 'success')
    
    # Fetch active orders count
    cursor.execute("""
        SELECT COUNT(*) as count FROM orders 
        WHERE Order_Status IN ('Processing', 'Shipped')
    """)
    active_orders = cursor.fetchone()['count']
    
    # Fetch delivered today count
    cursor.execute("""
        SELECT COUNT(*) as count FROM orders 
        WHERE Order_Status = 'Delivered' 
        AND Expected_Delivery = CURDATE()
    """)
    delivered_today = cursor.fetchone()['count']
    
    # Fetch in transit count
    cursor.execute("""
        SELECT COUNT(*) as count FROM orders 
        WHERE Order_Status = 'Shipped'
    """)
    in_transit = cursor.fetchone()['count']
    
    # Fetch total orders
    cursor.execute("SELECT COUNT(*) as count FROM orders")
    total_orders = cursor.fetchone()['count']
    
    # Fetch recent orders
    cursor.execute("""
    SELECT o.Order_ID, p.Product_Name, 
           CONCAT(c.First_Name, ' ', c.Last_Name) as Customer_Name,
           oh.Customer_ID, o.Order_Status, o.Expected_Delivery
    FROM orders o
    JOIN customer c ON o.Customer_ID = c.Customer_ID
    JOIN order_product op ON o.Order_ID = op.Order_ID
    JOIN product p ON op.Product_ID = p.Product_ID
    JOIN order_history oh ON o.Order_ID = oh.Order_ID
    ORDER BY o.Order_ID DESC
    LIMIT 5
""")
    recent_orders = cursor.fetchall()
    
    # Fetch recent updates/notifications
    cursor.execute("""
        SELECT o.Order_ID, o.Order_Status, 
               ABS(TIMESTAMPDIFF(MINUTE, o.Expected_Delivery, NOW())) as time_ago
        FROM orders o
        ORDER BY o.Expected_Delivery DESC
        LIMIT 5
    """)
    notifications = cursor.fetchall()
    
    # Fetch weekly order statistics
    cursor.execute("""
        SELECT 
            DATE_FORMAT(Expected_Delivery, '%a') as day, 
            COUNT(*) as order_count
        FROM orders
        WHERE Expected_Delivery >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE_FORMAT(Expected_Delivery, '%a'), DATE(Expected_Delivery)
        ORDER BY DATE(Expected_Delivery)
    """)
    weekly_stats = cursor.fetchall()
    
    cursor.execute("""
        SELECT Tracking_ID, Order_ID, Current_Location, Timestamp, Vehicle_ID
        FROM tracking_info
        ORDER BY Timestamp DESC
        LIMIT 3
    """)
    tracking_data = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('admin_welcome.html',
                         username=session['username'],
                         active_orders=active_orders,
                         delivered_today=delivered_today,
                         in_transit=in_transit,
                         total_orders=total_orders,
                         recent_orders=recent_orders,
                         notifications=notifications,
                         weekly_stats=weekly_stats,
                         tracking_data=tracking_data
                         )


@app.route('/update_order_status/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    if 'username' not in session:
        return redirect(url_for('home'))

    new_status = request.form['status']
    connection = create_db_connection()
    cursor = connection.cursor()

    # Update the status in the database
    cursor.execute("""
        UPDATE orders
        SET Order_Status = %s
        WHERE Order_ID = %s
    """, (new_status, order_id))
    connection.commit()

    cursor.close()
    connection.close()

    # Optionally, flash a message to the admin
    flash('Order status updated successfully!', 'success')

    # Redirect back to the admin dashboard
    return redirect(url_for('admin_dashboard'))

@app.route('/update_location/<int:tracking_id>', methods=['POST'])
@admin_required
def update_location(tracking_id):
    new_location = request.form['current_location']
    connection = create_db_connection()
    cursor = connection.cursor()

    # Update the location in the database
    cursor.execute("""
        UPDATE tracking_info
        SET Current_Location = %
        WHERE Tracking_ID = %s
    """, (new_location, tracking_id))
    connection.commit()

    cursor.close()
    connection.close()

    # Optionally, flash a message to indicate success
    flash('Location updated successfully!', 'success')

    # Redirect back to the page showing tracking info
    return redirect(url_for('admin_dashboard'))




@app.route('/order_tracking', methods=['GET'])
@login_required
def order_tracking():
    try:
        # Open DB connection with context manager
        connection = create_db_connection()
        with connection.cursor() as cursor:
            # Fetch tracking data for the current user (You can adjust this query to fetch tracking data for specific orders)
            cursor.execute("""
                SELECT Tracking_ID, Order_ID, Current_Location, Timestamp, Vehicle_ID
                FROM tracking_info
                WHERE Order_ID IN (SELECT Order_ID FROM orders WHERE Customer_ID = %s)
                ORDER BY Timestamp DESC
            """, (session['customer_id'],))

            # Fetch all tracking data
            tracking_data = cursor.fetchall()

        return render_template('admin_welcome.html', tracking_data=tracking_data)

    except mysql.connector.Error as e:
        flash(f'Error fetching tracking data: {str(e)}', 'error')
        return redirect(url_for('user_dashboard'))

    finally:
        cursor.close()
        connection.close()

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    # Check if user is an admin, and redirect to admin dashboard if true
    if session.get('is_admin', False):
        return redirect(url_for('admin_dashboard'))
    
    # Retrieve user information from session variables
    username = session['username']
    email = session['email']
    customer_id = session['customer_id']
    
    # Connect to the database
    connection = create_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Fetch user's orders and statistics with a nested query
    cursor.execute("""
        SELECT 
            COUNT(*) as total_orders,
            (SELECT COUNT(*) FROM orders WHERE Customer_ID = %s AND Order_Status = 'Processing') as processing_orders,
            (SELECT COUNT(*) FROM orders WHERE Customer_ID = %s AND Order_Status = 'Shipped') as shipped_orders,
            (SELECT COUNT(*) FROM orders WHERE Customer_ID = %s AND Order_Status = 'Delivered') as delivered_orders
        FROM orders 
        WHERE Customer_ID = %s
    """, (customer_id, customer_id, customer_id, customer_id))
    order_stats = cursor.fetchone()
    
    # Fetch available products
    cursor.execute("""
        SELECT Product_ID, Product_Name, Category, Price, Stock
        FROM product
        WHERE Stock > 0
        ORDER BY Product_Name
    """)
    available_products = cursor.fetchall()
    
    # Fetch referral count for the user
    cursor.execute("""
        SELECT COUNT(*) as referral_count
        FROM refers
        WHERE Referrer_Customer_ID = %s
    """, (customer_id,))
    referral_count = cursor.fetchone()['referral_count']
    
    # Call the stored procedure to get recent orders
    cursor.callproc('get_recent_orders', (customer_id,))

    # Fetch the result from the stored procedure
    recent_orders = None
    for result in cursor.stored_results():
        recent_orders = result.fetchall()
    
    # Close the database connection
    cursor.close()
    connection.close()
    
    # Return the rendered template with all the fetched data
    return render_template('user_welcome.html',
                           username=username,
                           order_stats=order_stats,
                           available_products=available_products,
                           recent_orders=recent_orders,
                           referral_count=referral_count)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    customer_id = session['customer_id']
    connection = create_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    if request.method == 'POST':
        # Capture updated details from the form
        first_name = request.form['first_name']
        middle_name = request.form.get('middle_name', '')
        last_name = request.form['last_name']
        contact_numbers = request.form.getlist('contact_info')  # Capture multiple contact numbers
        house_no = request.form['house_no']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']

        try:
            # Update the customer's personal information
            cursor.execute("""
                UPDATE customer
                SET First_Name = %s, Middle_Name = %s, Last_Name = %s, 
                    House_No_Room_No = %s, Street = %s, City = %s, State = %s
                WHERE Customer_ID = %s
            """, (first_name, middle_name, last_name, house_no, street, city, state, customer_id))
            
            # Remove old contact numbers from the contact_info table
            cursor.execute("DELETE FROM contact_info WHERE Customer_ID = %s", (customer_id,))
            
            # Insert new contact numbers
            for contact_number in contact_numbers:
                cursor.execute("""
                    INSERT INTO contact_info (Customer_ID, Contact_No)
                    VALUES (%s, %s)
                """, (customer_id, contact_number))
            
            connection.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user_dashboard'))
        
        except Exception as e:
            connection.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')
    
    else:
        # Fetch existing customer data to pre-fill the form
        cursor.execute("SELECT * FROM customer WHERE Customer_ID = %s", (customer_id,))
        customer = cursor.fetchone()

        # Fetch the contact numbers for the customer
        cursor.execute("SELECT Contact_No FROM contact_info WHERE Customer_ID = %s", (customer_id,))
        contact_numbers = [row['Contact_No'] for row in cursor.fetchall()]
        
    cursor.close()
    connection.close()
    return render_template('edit_profile.html', customer=customer, contact_numbers=contact_numbers, contact_numbers_length=len(contact_numbers))


@app.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    connection = create_db_connection()
    cursor = connection.cursor()
    
    try:
        # Check if the order exists and is not already cancelled
        cursor.execute("""
            SELECT Order_Status FROM orders WHERE Order_ID = %s AND Customer_ID = %s
        """, (order_id, session['customer_id']))
        order = cursor.fetchone()
        
        if order:
            order_status = order[0]
            if order_status != 'Cancelled':
                cursor.execute("UPDATE orders SET Order_Status = 'Cancelled' WHERE Order_ID = %s", (order_id,))
                connection.commit()
                flash('Order successfully cancelled!', 'success')
            else:
                flash('Order is already cancelled.', 'error')
        else:
            flash('Order not found or you do not have permission to cancel it.', 'error')
    
    except Exception as e:
        connection.rollback()
        flash(f'Error cancelling order: {str(e)}', 'error')
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('user_dashboard'))

@app.route('/refer', methods=['POST'])
def refer():
    referrer_id = session.get('customer_id')  # Ensure customer_id is in session
    referee_contact_no = request.form.get('referee_contact_no')  # Get the contact number from the form
    
    # Check if referrer ID and referee contact number are provided
    if not referrer_id:
        flash("Referrer ID is missing.", "error")
        return redirect(url_for('user_dashboard'))
    
    if not referee_contact_no:
        flash("Please provide a contact number for the referee.", "error")
        return redirect(url_for('user_dashboard'))
    
    # Create database connection
    connection = create_db_connection()
    cursor = connection.cursor()
    
    # Query to find the Customer_ID of the referee based on the contact number
    cursor.execute("""
        SELECT ci.Customer_ID
        FROM contact_info ci
        WHERE ci.Contact_No = %s
    """, (referee_contact_no,))
    
    result = cursor.fetchone()
    
    # Check if referee's contact number exists
    if result is None:
        flash("Referee contact number not found!", "error")
        connection.close()
        return redirect(url_for('user_dashboard'))
    
    referee_id = result[0]

    
    # Insert the referral into the refers table
    try:
        cursor.execute("""
            INSERT INTO refers (Referrer_Customer_ID, Referee_Customer_ID)
            VALUES (%s, %s)
        """, (referrer_id, referee_id))
        
        connection.commit()
        flash("Referral recorded successfully!", "success")
    except Exception as e:
        flash("An error occurred while recording the referral: " + str(e), "error")
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('user_dashboard'))




@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])  # Get quantity selected by user
    special_instructions = request.form.get('special_instructions', '')
    payment_option = request.form.get('payment_option', 'Pay Later')  # Default to 'Pay Later'

    # Validate inputs
    if not product_id or quantity <= 0:
        flash('Invalid product or quantity. Cannot place order.', 'error')
        return redirect(url_for('user_dashboard'))
    
    try:
        # Open DB connection with context manager
        connection = create_db_connection()
        with connection.cursor() as cursor:
            # Retrieve product price (no need to check stock, as the trigger will handle it)
            cursor.execute("SELECT Price FROM product WHERE Product_ID = %s", (product_id,))
            product = cursor.fetchone()

            if not product or product[0] is None:
                flash('Product is unavailable. Cannot place order.', 'error')
                return redirect(url_for('user_dashboard'))

            price = product[0]

            # Proceed with order placement, relying on the trigger for stock validation
            cursor.execute("""INSERT INTO orders (Customer_ID, Order_Status, Expected_Delivery, Special_Instructions)
                            VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL 7 DAY), %s)""",
                            (session['customer_id'], 'Processing', special_instructions))
            order_id = cursor.lastrowid

            # Attempt to insert into order_product, letting the trigger validate stock
            cursor.execute("INSERT INTO order_product (Order_ID, Product_ID, Quantity) VALUES (%s, %s, %s)", (order_id, product_id, quantity))
            
            # Call the calculate_total_price function to get the total price
            cursor.execute("SELECT calculate_total_price(%s)", (order_id,))
            total_price = cursor.fetchone()[0]
            
            # Insert into payment table with calculated total price and the correct payment status
            payment_status = 'Completed' if payment_option == 'Pay Now' else 'Pending'
            cursor.execute("INSERT INTO payment (Order_ID, Amount, Status, Date) VALUES (%s, %s, %s, NOW())", (order_id, total_price, payment_status))

            # Dynamically fetch an available vehicle (can implement custom logic here)
            cursor.execute("""SELECT Vehicle_ID, Driver_Name, Capacity 
                              FROM delivery_vehicle 
                              WHERE Status = 'Available' 
                              ORDER BY Capacity DESC LIMIT 1""")
            vehicle = cursor.fetchone()

            if vehicle:
                vehicle_id, driver_name, capacity = vehicle
                # Insert into tracking_info table
                cursor.execute("""INSERT INTO tracking_info (Order_ID, Current_Location, Timestamp, Vehicle_ID)
                                  VALUES (%s, %s, NOW(), %s)""", 
                                  (order_id, 'Warehouse', vehicle_id))  # Using dynamic Vehicle_ID

                # Optionally, update vehicle status to 'In Use'
                cursor.execute("""UPDATE delivery_vehicle 
                                  SET Status = 'In Use' 
                                  WHERE Vehicle_ID = %s""", (vehicle_id,))

            else:
                flash('No available vehicle found for the delivery.', 'error')
                return redirect(url_for('user_dashboard'))

            connection.commit()
            flash('Order placed successfully!', 'success')
    except mysql.connector.Error as e:
        connection.rollback()
        # Check if the error is due to insufficient stock from the trigger
        if e.errno == 45000:  # SQLSTATE for custom signal
            flash('Order failed: Insufficient stock.', 'error')
        else:
            flash(f'Error placing order: {str(e)}', 'error')
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('user_dashboard'))




@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)