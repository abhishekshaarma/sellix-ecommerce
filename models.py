from flask import current_app
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import uuid
import os

def get_db_connection():
    """Establish a database connection using the configuration settings"""
    connection = pymysql.connect(
        host=current_app.config['DB_HOST'],  # Changed from 'localhost' to 'DB_HOST'
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PASSWORD'],
        database=current_app.config['DB_NAME'],
        charset=current_app.config['DB_CHARSET'],
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

class User:
    """User model for handling user operations"""
    @staticmethod
    def update_user_verified(user_id, verified_status):
        """
        Directly update the user's verified status in the database
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Direct SQL update to ensure it's committed to the database
                cursor.execute(
                    "UPDATE users SET is_verified = %s WHERE id = %s",
                    (verified_status, user_id)
                )
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()


    
    @staticmethod
    def create(username, email, password, first_name=None, last_name=None, address=None, phone=None, is_admin=False):
        """Create a new user"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Hash the password
                password_hash = generate_password_hash(password)
                
                # SQL query to insert new user
                sql = """
                INSERT INTO users 
                (username, email, password_hash, first_name, last_name, address, phone, is_admin) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Execute the query
                cursor.execute(sql, (
                    username, email, password_hash, first_name, 
                    last_name, address, phone, is_admin
                ))
                
                # Commit the changes
                connection.commit()
                
                # Return the ID of the new user
                return cursor.lastrowid
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(user_id):
        """Get a user by ID"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE id = %s"
                cursor.execute(sql, (user_id,))
                user = cursor.fetchone()
                return user
        finally:
            connection.close()
    
    @staticmethod
    def get_by_username(username):
        """Get a user by username"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE username = %s"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
                return user
        finally:
            connection.close()
    
    @staticmethod
    def get_by_email(email):
        """Get a user by email"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE email = %s"
                cursor.execute(sql, (email,))
                user = cursor.fetchone()
                return user
        finally:
            connection.close()
    
    @staticmethod
    def check_password(user, password):
        """Check if the provided password matches the stored hash"""
        if not user or 'password_hash' not in user:
            return False
        return check_password_hash(user['password_hash'], password)
    
    @staticmethod
    def update(user_id, data):
        """Update user information"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Build update SQL based on provided data
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key == 'password':
                        update_fields.append("password_hash = %s")
                        values.append(generate_password_hash(value))
                    elif key in ['username', 'email', 'first_name', 'last_name', 'address', 'phone']:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                if not update_fields:
                    return False
                
                sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
                values.append(user_id)
                
                cursor.execute(sql, values)
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()


class Seller:
    """Seller model for handling seller operations"""
    
    @staticmethod
    def create(user_id, shop_name, shop_description=None, logo_url=None, banner_url=None, theme_color=None):
        """Create a new seller profile"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO sellers 
                (user_id, shop_name, shop_description, logo_url, banner_url, theme_color) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    user_id, shop_name, shop_description, logo_url, banner_url, theme_color
                ))
                connection.commit()
                return cursor.lastrowid
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(seller_id):
        """Get a seller by ID"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM sellers WHERE id = %s"
                cursor.execute(sql, (seller_id,))
                seller = cursor.fetchone()
                return seller
        finally:
            connection.close()
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get a seller by user ID"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM sellers WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                seller = cursor.fetchone()
                return seller
        finally:
            connection.close()
    
    @staticmethod
    def update(seller_id, data):
        """Update seller information"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key in ['shop_name', 'shop_description', 'logo_url', 'banner_url', 'theme_color']:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                if not update_fields:
                    return False
                
                sql = f"UPDATE sellers SET {', '.join(update_fields)} WHERE id = %s"
                values.append(seller_id)
                
                cursor.execute(sql, values)
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()


class Product:
    """Product model for handling product operations"""
    
    @staticmethod
    def create(seller_id, name, price, description=None, category_id=None, discount_price=None, 
               stock_quantity=0, barcode=None, sku=None, is_active=True):
        """Create a new product"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO products 
                (seller_id, name, price, description, category_id, discount_price, 
                 stock_quantity, barcode, sku, is_active) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    seller_id, name, price, description, category_id, discount_price,
                    stock_quantity, barcode, sku, is_active
                ))
                connection.commit()
                return cursor.lastrowid
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(product_id):
        """Get a product by ID"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT p.*, c.name as category_name, s.shop_name, 
                       (SELECT image_url FROM product_images WHERE product_id = p.id AND is_primary = TRUE LIMIT 1) as primary_image 
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN sellers s ON p.seller_id = s.id
                WHERE p.id = %s
                """
                cursor.execute(sql, (product_id,))
                product = cursor.fetchone()
                
                if product:
                    # Get all product images
                    sql = "SELECT * FROM product_images WHERE product_id = %s"
                    cursor.execute(sql, (product_id,))
                    product['images'] = cursor.fetchall()
                    
                    # Get product reviews
                    sql = """
                    SELECT r.*, u.username 
                    FROM reviews r
                    JOIN users u ON r.user_id = u.id
                    WHERE r.product_id = %s
                    ORDER BY r.created_at DESC
                    """
                    cursor.execute(sql, (product_id,))
                    product['reviews'] = cursor.fetchall()
                    
                    # Calculate average rating
                    if product['reviews']:
                        total_rating = sum(review['rating'] for review in product['reviews'])
                        product['avg_rating'] = total_rating / len(product['reviews'])
                    else:
                        product['avg_rating'] = 0
                
                return product
        finally:
            connection.close()
    
    @staticmethod
    def get_all(limit=None, offset=0, category_id=None, seller_id=None, search=None):
        """Get all products with optional filtering"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                conditions = []
                params = []
                
                if category_id:
                    conditions.append("p.category_id = %s")
                    params.append(category_id)
                
                if seller_id:
                    conditions.append("p.seller_id = %s")
                    params.append(seller_id)
                
                if search:
                    conditions.append("(p.name LIKE %s OR p.description LIKE %s)")
                    params.append(f"%{search}%")
                    params.append(f"%{search}%")
                
                # Add active filter
                conditions.append("p.is_active = TRUE")
                
                where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
                
                limit_clause = ""
                if limit:
                    limit_clause = "LIMIT %s OFFSET %s"
                    params.append(int(limit))
                    params.append(int(offset))
                
                sql = f"""
                SELECT p.*, c.name as category_name, s.shop_name, 
                       (SELECT image_url FROM product_images WHERE product_id = p.id AND is_primary = TRUE LIMIT 1) as primary_image 
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN sellers s ON p.seller_id = s.id
                {where_clause}
                ORDER BY p.created_at DESC
                {limit_clause}
                """
                
                cursor.execute(sql, params)
                products = cursor.fetchall()
                return products
        finally:
            connection.close()
    
    @staticmethod
    def update(product_id, data):
        """Update product information"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                update_fields = []
                values = []
                
                allowed_fields = [
                    'name', 'description', 'price', 'discount_price', 'category_id',
                    'stock_quantity', 'barcode', 'sku', 'is_active'
                ]
                
                for key, value in data.items():
                    if key in allowed_fields:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                if not update_fields:
                    return False
                
                sql = f"UPDATE products SET {', '.join(update_fields)} WHERE id = %s"
                values.append(product_id)
                
                cursor.execute(sql, values)
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()
    
    @staticmethod
    def delete(product_id):
        """Delete a product"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # First delete all product images
                sql = "DELETE FROM product_images WHERE product_id = %s"
                cursor.execute(sql, (product_id,))
                
                # Delete the product
                sql = "DELETE FROM products WHERE id = %s"
                cursor.execute(sql, (product_id,))
                
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()


class Category:
    """Category model for handling category operations"""
    
    @staticmethod
    def get_all():
        """Get all categories"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM categories ORDER BY name"
                cursor.execute(sql)
                categories = cursor.fetchall()
                return categories
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(category_id):
        """Get a category by ID"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM categories WHERE id = %s"
                cursor.execute(sql, (category_id,))
                category = cursor.fetchone()
                return category
        finally:
            connection.close()


class Order:
    """Order model for handling order operations"""
    
    @staticmethod
    def create(user_id, total_amount, shipping_address):
        """Create a new order"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Create the order
                sql = """
                INSERT INTO orders 
                (user_id, total_amount, shipping_address, order_status, payment_status) 
                VALUES (%s, %s, %s, 'pending', 'pending')
                """
                cursor.execute(sql, (user_id, total_amount, shipping_address))
                order_id = cursor.lastrowid
                
                # Get cart items for the user
                sql = """
                SELECT c.*, p.price, p.seller_id 
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = %s
                """
                cursor.execute(sql, (user_id,))
                cart_items = cursor.fetchall()
                
                # Insert order items
                for item in cart_items:
                    subtotal = item['price'] * item['quantity']
                    sql = """
                    INSERT INTO order_items 
                    (order_id, product_id, seller_id, quantity, price, subtotal) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        order_id, item['product_id'], item['seller_id'],
                        item['quantity'], item['price'], subtotal
                    ))
                    
                    # Update product stock
                    sql = "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id = %s"
                    cursor.execute(sql, (item['quantity'], item['product_id']))
                
                # Clear cart
                sql = "DELETE FROM cart WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                
                connection.commit()
                return order_id
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(order_id):
        """Get an order by ID with all its items"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Get order details
                sql = """
                SELECT o.*, u.username, u.email 
                FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE o.id = %s
                """
                cursor.execute(sql, (order_id,))
                order = cursor.fetchone()
                
                if order:
                    # Get order items
                    sql = """
                    SELECT oi.*, p.name as product_name, s.shop_name 
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.id
                    JOIN sellers s ON oi.seller_id = s.id
                    WHERE oi.order_id = %s
                    """
                    cursor.execute(sql, (order_id,))
                    order['items'] = cursor.fetchall()
                
                return order
        finally:
            connection.close()
    
    @staticmethod
    def get_user_orders(user_id):
        """Get all orders for a user"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC"
                cursor.execute(sql, (user_id,))
                orders = cursor.fetchall()
                return orders
        finally:
            connection.close()
    
    @staticmethod
    def get_seller_orders(seller_id):
        """Get all orders containing items from a seller"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT DISTINCT o.* 
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                WHERE oi.seller_id = %s
                ORDER BY o.created_at DESC
                """
                cursor.execute(sql, (seller_id,))
                orders = cursor.fetchall()
                
                # Get order items for this seller
                for order in orders:
                    sql = """
                    SELECT oi.*, p.name as product_name 
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.id
                    WHERE oi.order_id = %s AND oi.seller_id = %s
                    """
                    cursor.execute(sql, (order['id'], seller_id))
                    order['items'] = cursor.fetchall()
                
                return orders
        finally:
            connection.close()
    
    @staticmethod
    def update_status(order_id, order_status, payment_status=None):
        """Update order status"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                update_fields = ["order_status = %s"]
                values = [order_status]
                
                if payment_status:
                    update_fields.append("payment_status = %s")
                    values.append(payment_status)
                
                sql = f"UPDATE orders SET {', '.join(update_fields)} WHERE id = %s"
                values.append(order_id)
                
                cursor.execute(sql, values)
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()


class Cart:
    """Cart model for handling shopping cart operations"""
    
    @staticmethod
    def add_item(user_id, product_id, quantity=1):
        """Add an item to the cart"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Check if the item is already in the cart
                sql = "SELECT * FROM cart WHERE user_id = %s AND product_id = %s"
                cursor.execute(sql, (user_id, product_id))
                existing_item = cursor.fetchone()
                
                if existing_item:
                    # Update quantity
                    sql = "UPDATE cart SET quantity = quantity + %s WHERE id = %s"
                    cursor.execute(sql, (quantity, existing_item['id']))
                else:
                    # Add new item
                    sql = "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (user_id, product_id, quantity))
                
                connection.commit()
                return True
        finally:
            connection.close()
    
    @staticmethod
    def update_quantity(cart_id, quantity):
        """Update cart item quantity"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                if quantity <= 0:
                    # Remove item if quantity is 0 or negative
                    sql = "DELETE FROM cart WHERE id = %s"
                    cursor.execute(sql, (cart_id,))
                else:
                    # Update quantity
                    sql = "UPDATE cart SET quantity = %s WHERE id = %s"
                    cursor.execute(sql, (quantity, cart_id))
                
                connection.commit()
                return True
        finally:
            connection.close()
    
    @staticmethod
    def remove_item(cart_id):
        """Remove an item from the cart"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM cart WHERE id = %s"
                cursor.execute(sql, (cart_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()
    
    @staticmethod
    def get_user_cart(user_id):
        """Get all items in a user's cart"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT c.*, p.name, p.price, p.discount_price, 
                       (SELECT image_url FROM product_images WHERE product_id = p.id AND is_primary = TRUE LIMIT 1) as image_url,
                       s.shop_name
                FROM cart c
                JOIN products p ON c.product_id = p.id
                JOIN sellers s ON p.seller_id = s.id
                WHERE c.user_id = %s
                """
                cursor.execute(sql, (user_id,))
                cart_items = cursor.fetchall()
                
                # Calculate totals
                total = 0
                for item in cart_items:
                    # Use discount price if available
                    price = item['discount_price'] if item['discount_price'] else item['price']
                    item['subtotal'] = price * item['quantity']
                    total += item['subtotal']
                
                return {
                    'items': cart_items,
                    'total': total,
                    'item_count': len(cart_items)
                }
        finally:
            connection.close()
    
    @staticmethod
    def clear_user_cart(user_id):
        """Remove all items from a user's cart"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM cart WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                connection.commit()
                return True
        finally:
            connection.close()


class Review:
    """Review model for handling product reviews"""
    
    @staticmethod
    def create(product_id, user_id, rating, comment=None):
        """Create a new review"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Check if user already reviewed this product
                sql = "SELECT * FROM reviews WHERE product_id = %s AND user_id = %s"
                cursor.execute(sql, (product_id, user_id))
                existing_review = cursor.fetchone()
                
                if existing_review:
                    # Update existing review
                    sql = "UPDATE reviews SET rating = %s, comment = %s WHERE id = %s"
                    cursor.execute(sql, (rating, comment, existing_review['id']))
                    connection.commit()
                    return existing_review['id']
                else:
                    # Create new review
                    sql = "INSERT INTO reviews (product_id, user_id, rating, comment) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (product_id, user_id, rating, comment))
                    connection.commit()
                    return cursor.lastrowid
        finally:
            connection.close()
    
    @staticmethod
    def get_product_reviews(product_id):
        """Get all reviews for a product"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT r.*, u.username 
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                WHERE r.product_id = %s
                ORDER BY r.created_at DESC
                """
                cursor.execute(sql, (product_id,))
                reviews = cursor.fetchall()
                
                # Calculate average rating
                avg_rating = 0
                if reviews:
                    total_rating = sum(review['rating'] for review in reviews)
                    avg_rating = total_rating / len(reviews)
                
                return {
                    'reviews': reviews,
                    'avg_rating': avg_rating,
                    'count': len(reviews)
                }
        finally:
            connection.close()


class Page:
    """Page model for handling seller custom pages"""
    
    @staticmethod
    def create(seller_id, title, content, slug, is_active=True):
        """Create a new page"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO pages 
                (seller_id, title, content, slug, is_active) 
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (seller_id, title, content, slug, is_active))
                connection.commit()
                return cursor.lastrowid
        finally:
            connection.close()
    
    @staticmethod
    def get_by_slug(seller_id, slug):
        """Get a page by seller ID and slug"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM pages WHERE seller_id = %s AND slug = %s"
                cursor.execute(sql, (seller_id, slug))
                page = cursor.fetchone()
                return page
        finally:
            connection.close()
    
    @staticmethod
    def get_seller_pages(seller_id):
        """Get all pages for a seller"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM pages WHERE seller_id = %s ORDER BY title"
                cursor.execute(sql, (seller_id,))
                pages = cursor.fetchall()
                return pages
        finally:
            connection.close()
    
    @staticmethod
    def update(page_id, data):
        """Update page information"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key in ['title', 'content', 'slug', 'is_active']:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                if not update_fields:
                    return False
                
                sql = f"UPDATE pages SET {', '.join(update_fields)} WHERE id = %s"
                values.append(page_id)
                
                cursor.execute(sql, values)
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()
    
    @staticmethod
    def delete(page_id):
        """Delete a page"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM pages WHERE id = %s"
                cursor.execute(sql, (page_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()


class ProductImage:
    """ProductImage model for handling product images"""
    
    @staticmethod
    def add(product_id, image_url, is_primary=False):
        """Add an image to a product"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # If this is the primary image, reset other images to non-primary
                if is_primary:
                    sql = "UPDATE product_images SET is_primary = FALSE WHERE product_id = %s"
                    cursor.execute(sql, (product_id,))
                
                # Add the new image
                sql = "INSERT INTO product_images (product_id, image_url, is_primary) VALUES (%s, %s, %s)"
                cursor.execute(sql, (product_id, image_url, is_primary))
                connection.commit()
                return cursor.lastrowid
        finally:
            connection.close()
    
    @staticmethod
    def set_primary(image_id):
        """Set an image as the primary image for a product"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Get the product ID for this image
                sql = "SELECT product_id FROM product_images WHERE id = %s"
                cursor.execute(sql, (image_id,))
                result = cursor.fetchone()
                
                if not result:
                    return False
                
                product_id = result['product_id']
                
                # Reset all images for this product to non-primary
                sql = "UPDATE product_images SET is_primary = FALSE WHERE product_id = %s"
                cursor.execute(sql, (product_id,))
                
                # Set this image as primary
                sql = "UPDATE product_images SET is_primary = TRUE WHERE id = %s"
                cursor.execute(sql, (image_id,))
                
                connection.commit()
                return True
        finally:
            connection.close()
    
    @staticmethod
    def delete(image_id):
        """Delete an image"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM product_images WHERE id = %s"
                cursor.execute(sql, (image_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()
                    
            
