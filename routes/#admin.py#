from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import User, Seller, Product, Category, Order
from routes.auth import login_required, admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@admin_required
def dashboard():
    # Get counts
    from models import get_db_connection
    
    connection = get_db_connection()
    stats = {}
    
    try:
        with connection.cursor() as cursor:
            # Get user count
            cursor.execute("SELECT COUNT(*) as count FROM users")
            stats['user_count'] = cursor.fetchone()['count']
            
            # Get seller count
            cursor.execute("SELECT COUNT(*) as count FROM sellers")
            stats['seller_count'] = cursor.fetchone()['count']
            
            # Get product count
            cursor.execute("SELECT COUNT(*) as count FROM products")
            stats['product_count'] = cursor.fetchone()['count']
            
            # Get order count
            cursor.execute("SELECT COUNT(*) as count FROM orders")
            stats['order_count'] = cursor.fetchone()['count']
            
            # Get total sales
            cursor.execute("SELECT SUM(total_amount) as total FROM orders")
            result = cursor.fetchone()
            stats['total_sales'] = result['total'] if result['total'] else 0
            
            # Get recent orders
            cursor.execute("""
                SELECT o.*, u.username 
                FROM orders o
                JOIN users u ON o.user_id = u.id
                ORDER BY o.created_at DESC
                LIMIT 5
            """)
            stats['recent_orders'] = cursor.fetchall()
    finally:
        connection.close()
    
    return render_template('admin/dashboard.html', 
                       stats=stats,
                       title="Admin Dashboard")

@admin_bp.route('/admin/users')
@admin_required
def users():
    # Get all users
    from models import get_db_connection
    
    connection = get_db_connection()
    users = []
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, 
                       (SELECT COUNT(*) FROM orders WHERE user_id = u.id) as order_count,
                       (SELECT s.id FROM sellers s WHERE s.user_id = u.id) as seller_id
                FROM users u
                ORDER BY u.created_at DESC
            """)
            users = cursor.fetchall()
    finally:
        connection.close()
    
    return render_template('admin/users.html', 
                       users=users,
                       title="Manage Users")

@admin_bp.route('/admin/user/<int:user_id>')
@admin_required
def user_detail(user_id):
    # Get user data
    user = User.get_by_id(user_id)
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('admin.users'))
    
    # Check if user is a seller
    seller = Seller.get_by_user_id(user_id)
    
    # Get user orders
    orders = Order.get_user_orders(user_id)
    
    return render_template('admin/user_detail.html', 
                       user=user,
                       seller=seller,
                       orders=orders,
                       title="User Detail")

@admin_bp.route('/admin/user/toggle-admin/<int:user_id>', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    # Get user data
    user = User.get_by_id(user_id)
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('admin.users'))
    
    # Toggle admin status
    current_status = user['is_admin']
    
    # Update user
    if User.update(user_id, {'is_admin': not current_status}):
        flash(f"User {'removed from' if current_status else 'added to'} administrators", 'success')
    else:
        flash('Error updating user', 'danger')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/admin/sellers')
@admin_required
def sellers():
    # Get all sellers
    from models import get_db_connection
    
    connection = get_db_connection()
    sellers = []
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.*, u.username, u.email,
                       (SELECT COUNT(*) FROM products WHERE seller_id = s.id) as product_count
                FROM sellers s
                JOIN users u ON s.user_id = u.id
                ORDER BY s.created_at DESC
            """)
            sellers = cursor.fetchall()
    finally:
        connection.close()
    
    return render_template('admin/sellers.html', 
                       sellers=sellers,
                       title="Manage Sellers")

@admin_bp.route('/admin/seller/<int:seller_id>')
@admin_required
def seller_detail(seller_id):
    # Get seller data
    seller = Seller.get_by_id(seller_id)
    
    if not seller:
        flash('Seller not found', 'danger')
        return redirect(url_for('admin.sellers'))
    
    # Get seller user data
    user = User.get_by_id(seller['user_id'])
    
    # Get seller products
    products = Product.get_all(seller_id=seller_id)
    
    # Get seller orders
    orders = Order.get_seller_orders(seller_id)
    
    return render_template('admin/seller_detail.html', 
                       seller=seller,
                       user=user,
                       products=products,
                       orders=orders,
                       title="Seller Detail")

@admin_bp.route('/admin/seller/toggle-verified/<int:seller_id>', methods=['POST'])
@admin_required
def toggle_verified(seller_id):
    # Get seller data
    seller = Seller.get_by_id(seller_id)
    
    if not seller:
        flash('Seller not found', 'danger')
        return redirect(url_for('admin.sellers'))
    
    # Toggle verified status
    current_status = seller['is_verified']
    
    # Update seller
    from models import get_db_connection
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE sellers SET is_verified = %s WHERE id = %s",
                (not current_status, seller_id)
            )
            connection.commit()
            flash(f"Seller {'unverified' if current_status else 'verified'} successfully", 'success')
    except:
        flash('Error updating seller', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('admin.seller_detail', seller_id=seller_id))

@admin_bp.route('/admin/categories')
@admin_required
def categories():
    # Get all categories
    categories = Category.get_all()
    
    return render_template('admin/categories.html', 
                       categories=categories,
                       title="Manage Categories")

@admin_bp.route('/admin/category/add', methods=['GET', 'POST'])
@admin_required
def add_category():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        parent_id = request.form.get('parent_id', type=int)
        
        if parent_id == 0:
            parent_id = None
        
        # Validation
        if not name:
            flash('Category name is required', 'danger')
            return redirect(url_for('admin.categories'))
        
        # Create category
        from models import get_db_connection
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO categories (name, description, parent_id) VALUES (%s, %s, %s)",
                    (name, description, parent_id)
                )
                connection.commit()
                flash('Category added successfully', 'success')
        except:
            flash('Error adding category', 'danger')
        finally:
            connection.close()
        
        return redirect(url_for('admin.categories'))
    
    # Get all categories for parent selection
    categories = Category.get_all()
    
    return render_template('admin/category_form.html', 
                       categories=categories,
                       title="Add Category")

@admin_bp.route('/admin/category/edit/<int:category_id>', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    # Get category data
    category = Category.get_by_id(category_id)
    
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('admin.categories'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        parent_id = request.form.get('parent_id', type=int)
        
        if parent_id == 0:
            parent_id = None
        
        # Validation
        if not name:
            flash('Category name is required', 'danger')
            return redirect(url_for('admin.edit_category', category_id=category_id))
        
        # Update category
        from models import get_db_connection
        
        connection = get_db_connection()
        try:
            with connection:
                cursor.execute(
                    "UPDATE categories SET name = %s, description = %s, parent_id = %s WHERE id = %s",
                    (name, description, parent_id, category_id)
                )
                connection.commit()
                flash('Category updated successfully', 'success')
        except:
            flash('Error updating category', 'danger')
        finally:
            connection.close()
        
        return redirect(url_for('admin.categories'))
    
    # Get all categories for parent selection
    categories = Category.get_all()
    
    return render_template('admin/category_form.html', 
                           category=category,
                           categories=categories,
                           title="Edit Category")

@admin_bp.route('/admin/category/delete/<int:category_id>', methods=['POST'])
@admin_required
def delete_category(category_id):
    # Get category data
    category = Category.get_by_id(category_id)
    
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('admin.categories'))
    
    # Check if category has any products
    products = Product.get_all(category_id=category_id)
    if products:
        flash('Cannot delete category with associated products', 'warning')
        return redirect(url_for('admin.categories'))
    
    # Delete category
    from models import get_db_connection
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
            connection.commit()
            flash('Category deleted successfully', 'success')
    except:
        flash('Error deleting category', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('admin.categories'))

@admin_bp.route('/admin/products')
@admin_required
def products():
    # Get all products with category and seller info
    products = Product.get_all()
    
    return render_template('admin/products.html', 
                           products=products,
                           title="Manage Products")

@admin_bp.route('/admin/product/<int:product_id>')
@admin_required
def product_detail(product_id):
    # Get product data
    product = Product.get_by_id(product_id)
    
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('admin.products'))
    
    # Get seller data
    seller = Seller.get_by_id(product['seller_id'])
    
    # Get category data
    category = Category.get_by_id(product['category_id'])
    
    return render_template('admin/product_detail.html', 
                           product=product,
                           seller=seller,
                           category=category,
                           title="Product Detail")

@admin_bp.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    # Get product data
    product = Product.get_by_id(product_id)
    
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('admin.products'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price', type=float)
        discount_price = request.form.get('discount_price', type=float)
        category_id = request.form.get('category_id', type=int)
        stock_quantity = request.form.get('stock_quantity', type=int)
        barcode = request.form.get('barcode')
        sku = request.form.get('sku')
        is_active = True if request.form.get('is_active') else False
        
        # Validation
        if not name or price is None or stock_quantity is None:
            flash('Name, price, and stock quantity are required', 'danger')
            return redirect(url_for('admin.edit_product', product_id=product_id))
        
        # Update product
        update_data = {
            'name': name,
            'description': description,
            'price': price,
            'discount_price': discount_price,
            'category_id': category_id if category_id > 0 else None,
            'stock_quantity': stock_quantity,
            'barcode': barcode,
            'sku': sku,
            'is_active': is_active
        }
        
        if Product.update(product_id, update_data):
            flash('Product updated successfully', 'success')
            return redirect(url_for('admin.product_detail', product_id=product_id))
        else:
            flash('Error updating product', 'danger')
    
    # Get all categories for selection
    categories = Category.get_all()
    
    return render_template('admin/product_form.html', 
                           product=product,
                           categories=categories,
                           title="Edit Product")

@admin_bp.route('/admin/product/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    # Get product data
    product = Product.get_by_id(product_id)
    
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('admin.products'))
    
    # Delete product
    if Product.delete(product_id):
        flash('Product deleted successfully', 'success')
    else:
        flash('Error deleting product', 'danger')
    
    return redirect(url_for('admin.products'))

@admin_bp.route('/admin/orders')
@admin_required
def orders():
    # Get all orders with user info
    from models import get_db_connection
    
    connection = get_db_connection()
    orders = []
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT o.*, u.username,
                       (SELECT SUM(oi.quantity) FROM order_items oi WHERE oi.order_id = o.id) as total_items
                FROM orders o
                JOIN users u ON o.user_id = u.id
                ORDER BY o.created_at DESC
            """)
            orders = cursor.fetchall()
    finally:
        connection.close()
        
    return render_template('admin/orders.html', 
                           orders=orders,
                           title="Manage Orders")

@admin_bp.route('/admin/order/<int:order_id>')
@admin_required
def order_detail(order_id):
    # Get order data with items and user info
    order = Order.get_by_id(order_id)
    
    if not order:
        flash('Order not found', 'danger')
        return redirect(url_for('admin.orders'))
    
    return render_template('admin/order_detail.html', 
                           order=order,
                           title=f"Order #{order_id} Detail")

@admin_bp.route('/admin/order/update-status/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    # Get form data
    order_status = request.form.get('order_status')
    payment_status = request.form.get('payment_status')
    
    # Update order status
    if Order.update_status(order_id, order_status, payment_status):
        flash('Order status updated successfully', 'success')
    else:
        flash('Error updating order status', 'danger')
        
    return redirect(url_for('admin.order_detail', order_id=order_id))
