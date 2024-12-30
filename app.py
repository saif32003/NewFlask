from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import paypalrestsdk
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')
app.secret_key = 'admin123'

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking to save memory

# Configure file uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder where images will be stored
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image file extensions

# Initialize the database
db = SQLAlchemy(app)

paypalrestsdk.configure({
    "mode": "sandbox",  # Use "sandbox" for testing or "live" for production
    "client_id": "AXBqB7m1gKEjAIE8x0ek4SYy7gJk2hcYVxgMCsO9pWvNqIaZPsE5SaGU5EWvd-penHPf103-77eOgqC_",
    "client_secret": "EPmMmJq8srfwnv9nCl22BuZtQLc0KmkvKUh7Sck0hsN8T5l9qShFKY_KU8C9vjYGOP-Sir5ARt5CSvuY"
})

# Product model to store products in the database
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), default='https://via.placeholder.com/250x150')

# Create the database tables
with app.app_context():
    db.create_all()  # Creates the tables in the database

@app.route('/')
def home():
    return render_template('index.html')

# Services route
@app.route('/services')
def services():
    return render_template('services.html')

# Who Are We route
@app.route('/who-are-we')
def who_are_we():
    return render_template('who are we.html')

# Contact Us route
@app.route('/contact-us')
def contact_us():
    return render_template('contact us.html')

@app.route('/more-works')
def more_works():
    return render_template('more works.html')

# Store route - fetch products from the database
@app.route('/store')
def store():
    products = Product.query.all()  # Get all products from the database
    return render_template('store.html', products=products)

# Dummy user credentials for the sake of example
users = {"noha": "Noha@123#"}

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in users and users[username] == password:
        return redirect(url_for('dashboard'))
    return redirect(url_for('admin'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        try:
            if 'delete_product_id' in request.form:
                # Delete product
                product_id = request.form['delete_product_id']
                product = Product.query.get_or_404(product_id)
                db.session.delete(product)
                db.session.commit()

            elif 'product_id' in request.form:
                # Edit product
                product_id = request.form['product_id']
                product = Product.query.get_or_404(product_id)
                product.name = request.form['product_name']
                product.price = float(request.form['product_price'])

                # Handle image update (if new image is uploaded)
                if 'product_image' in request.files:
                    file = request.files['product_image']
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath)
                        product.image = f'uploads/{filename}'
                
                db.session.commit()

            else:
                # Add new product
                product_name = request.form['product_name']
                product_price = request.form['product_price']
                product_image = None

                # Handle file upload if exists
                if 'product_image' in request.files:
                    file = request.files['product_image']
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath)
                        product_image = f'uploads/{filename}'
                
                try:
                    product_price = float(product_price)
                except ValueError:
                    product_price = 0.0  # Set to 0 if the price is invalid

                new_product = Product(name=product_name, price=product_price, image=product_image)
                db.session.add(new_product)
                db.session.commit()

            return redirect(url_for('dashboard'))
        
        except Exception as e:
            # Handle any error that might occur during the request handling
            db.session.rollback()  # Rollback any changes if an error occurs
            print(f"Error: {e}")
            return render_template('dashboard.html', error_message="An error occurred. Please try again.")

    # Fetch all products from the database
    products = Product.query.all()
    return render_template('dashboard.html', products=products)
@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

def verify_payment():
    payment_id = request.json.get("paymentID")
    payer_id = request.json.get("payerID")
    
    # Fetch the payment details using the payment ID
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Payment was successful, fetch the product associated with the payment
        product_id = request.json.get("product_id")
        product = Product.query.get(product_id)  # Assuming product_id is sent with the payment
        
        if product and product.download_url:
            # Payment successful, provide download link
            return jsonify({
                "status": "Payment successful!",
                "download_url": url_for('download_file', filename=product.download_url, _external=True)
            }), 200
        else:
            return jsonify({"status": "Product not available for download."}), 404
    else:
        # Payment failed
        return jsonify({"status": "Payment failed."}), 400

# Route to serve downloadable content
@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.static_folder, 'downloads', filename)
    
    if os.path.exists(file_path):
        return send_from_directory(os.path.join(app.static_folder, 'downloads'), filename)
    else:
        return "File not found", 404

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == "__main__":
    app.run(debug=True)
