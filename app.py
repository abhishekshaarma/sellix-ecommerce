from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
#from page import Page
from config import Config
import pymysql
from flask_mail import Mail
from routes.auth import mail

def init_db(app):
    """Initialize the database if it doesn't exist"""
    connection = pymysql.connect(
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD']
    )
    
    try:
        with connection.cursor() as cursor:
            # Check if database exists, if not create it
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['DB_NAME']}")
            cursor.execute(f"USE {app.config['DB_NAME']}")
            
            # Check if tables exist
            cursor.execute("SHOW TABLES LIKE 'products'")
            if cursor.fetchone():
                print("Database tables already exist. Skipping initialization.")
                return
            
            print("Creating database tables...")
            
            # Read the schema file and execute it
            schema_path = os.path.join(os.path.dirname(__file__), 'db.sql')
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                
            # Split by semicolon to execute each statement separately
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            for statement in statements:
                try:
                    cursor.execute(statement)
                    connection.commit()
                except Exception as e:
                    print(f"Error executing statement: {e}")
                    print(f"Statement: {statement}")
            
            print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization error: {e}")
    finally:
        connection.close()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db(app)
    mail.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.market import market_bp
    from routes.seller import seller_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(admin_bp)
    
    # Helper function for file uploads
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            # Create a unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Save the file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Return the file URL
            file_url = url_for('uploaded_file', filename=unique_filename, _external=True)
            return jsonify({'url': file_url}), 200
        
        return jsonify({'error': 'File type not allowed'}), 400
    
    @app.context_processor
    def inject_user():
        """Add user data to all templates"""
        user_data = None
        cart_data = {'item_count': 0, 'total': 0}
        
        if 'user_id' in session:
            from models import User, Cart, Seller
            
            user_data = User.get_by_id(session['user_id'])
            cart_data = Cart.get_user_cart(session['user_id'])
            
            # Check if user is a seller
            if user_data:
                seller_data = Seller.get_by_user_id(user_data['id'])
                user_data['is_seller'] = seller_data is not None
                if seller_data:
                    user_data['seller_id'] = seller_data['id']
                    user_data['shop_name'] = seller_data['shop_name']
        
        return {
            'user': user_data,
            'cart': cart_data,
            'current_year': datetime.now().year
        }
    @staticmethod
    def get_by_slug_any_seller(slug):
        """
        Retrieve a published page by slug from any seller
    """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                SELECT * FROM pages
                WHERE slug = %s AND is_active = 1
                LIMIT 1
                """, (slug,))
                return cursor.fetchone()
        finally:
            connection.close()
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
    
    @app.route('/')
    @app.route('/home')
    def home():
        from models import Product, Category
        
        # Get featured products
        featured_products = Product.get_all(limit=8)
        categories = Category.get_all()
        
        return render_template('home.html', 
                            products=featured_products, 
                            categories=categories,
                            title="Home")
    
    return app


# Create the Flask application
app = create_app()

if __name__ == '__main__':
    app.run()
