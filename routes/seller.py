from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import Product, Category, Seller, Order, ProductImage, Page
from routes.auth import login_required, seller_required
import os
from werkzeug.utils import secure_filename
import uuid
import json

seller_bp = Blueprint('seller', __name__)

@seller_bp.route('/seller/dashboard')
@seller_required
def dashboard():
    # Get seller data
    seller = Seller.get_by_user_id(session['user_id'])
    
    # Get recent orders
    recent_orders = Order.get_seller_orders(seller['id'])[:5]
    
    # Get product count
    products = Product.get_all(seller_id=seller['id'])
    product_count = len(products)
    
    # Calculate total sales
    total_sales = 0
    order_count = 0
    for order in recent_orders:
        for item in order['items']:
            total_sales += item['subtotal']
        order_count += 1
    
    return render_template('dashboard/seller.html', 
                       seller=seller,
                       recent_orders=recent_orders,
                       product_count=product_count,
                       total_sales=total_sales,
                       order_count=order_count,
                       title="Seller Dashboard")

@seller_bp.route('/seller/products')
@seller_required
def products():
    # Get seller data
    seller = Seller.get_by_user_id(session['user_id'])
    
    # Get seller products
    products = Product.get_all(seller_id=seller['id'])
    
    # Get categories for form
    categories = Category.get_all()
    
    return render_template('dashboard/seller_products.html', 
                       seller=seller,
                       products=products,
                       categories=categories,
                       title="Manage Products")

@seller_bp.route('/seller/product/add', methods=['GET', 'POST'])
@seller_required
def add_product():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price', type=float)
        discount_price = request.form.get('discount_price', type=float)
        category_id = request.form.get('category_id', type=int)
        stock_quantity = request.form.get('stock_quantity', 0, type=int)
        barcode = request.form.get('barcode')
        sku = request.form.get('sku')
        is_active = request.form.get('is_active') == 'on'
        
        # Get seller data
        seller = Seller.get_by_user_id(session['user_id'])
        
        # Validation
        if not name or not price or price <= 0:
            flash('Product name and valid price are required', 'danger')
            categories = Category.get_all()
            return render_template('dashboard/seller_product_form.html', 
                               categories=categories,
                               title="Add Product")
        
        # Create product
        product_id = Product.create(
            seller_id=seller['id'],
            name=name,
            description=description,
            price=price,
            discount_price=discount_price,
            category_id=category_id,
            stock_quantity=stock_quantity,
            barcode=barcode,
            sku=sku,
            is_active=is_active
        )
        
        if product_id:
            # Handle image uploads
            images = request.form.get('images')
            if images:
                images = json.loads(images)
                for i, image_url in enumerate(images):
                    ProductImage.add(product_id, image_url, i == 0)  # First image is primary
            
            flash('Product added successfully', 'success')
            return redirect(url_for('seller.products'))
        else:
            flash('Error adding product', 'danger')
    
    # Get categories for form
    categories = Category.get_all()
    
    return render_template('dashboard/seller_product_form.html', 
                       categories=categories,
                       title="Add Product")

@seller_bp.route('/seller/product/edit/<int:product_id>', methods=['GET', 'POST'])
@seller_required
def edit_product(product_id):
    # Get seller data
    seller = Seller.get_by_user_id(session['user_id'])
    
    # Get product data
    product = Product.get_by_id(product_id)
    
    # Verify ownership
    if not product or product['seller_id'] != seller['id']:
        flash('Product not found', 'danger')
        return redirect(url_for('seller.products'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price', type=float)
        discount_price = request.form.get('discount_price', type=float)
        category_id = request.form.get('category_id', type=int)
        stock_quantity = request.form.get('stock_quantity', 0, type=int)
        barcode = request.form.get('barcode')
        sku = request.form.get('sku')
        is_active = request.form.get('is_active') == 'on'
        
        # Validation
        if not name or not price or price <= 0:
            flash('Product name and valid price are required', 'danger')
            categories = Category.get_all()
            return render_template('dashboard/seller_product_form.html', 
                               product=product,
                               categories=categories,
                               title="Edit Product")
        
        # Update product
        product_data = {
            'name': name,
            'description': description,
            'price': price,
            'discount_price': discount_price,
            'category_id': category_id,
            'stock_quantity': stock_quantity,
            'barcode': barcode,
            'sku': sku,
            'is_active': is_active
        }
        
        if Product.update(product_id, product_data):
            # Handle image uploads
            images = request.form.get('images')
            if images:
                images = json.loads(images)
                
                # Delete existing images if new ones are uploaded
                if images:
                    for image in product['images']:
                        ProductImage.delete(image['id'])
                    
                    # Add new images
                    for i, image_url in enumerate(images):
                        ProductImage.add(product_id, image_url, i == 0)  # First image is primary
            
            flash('Product updated successfully', 'success')
            return redirect(url_for('seller.products'))
        else:
            flash('Error updating product', 'danger')
    
    # Get categories for form
    categories = Category.get_all()
    
    return render_template('dashboard/seller_product_form.html', 
                       product=product,
                       categories=categories,
                       title="Edit Product")

@seller_bp.route('/seller/product/delete/<int:product_id>', methods=['POST'])
@seller_required
def delete_product(product_id):
    # Get seller data
    seller = Seller.get_by_user_id(session['user_id'])
    
    # Get product data
    product = Product.get_by_id(product_id)
    
    # Verify ownership
    if not product or product['seller_id'] != seller['id']:
        flash('Product not found', 'danger')
        return redirect(url_for('seller.products'))
    
    # Delete product
    if Product.delete(product_id):
        flash('Product deleted successfully', 'success')
    else:
        flash('Error deleting product', 'danger')
    
    return redirect(url_for('seller.products'))

@seller_bp.route('/seller/orders')
@seller_required
def orders():
    # Get seller data
    seller = Seller.get_by_user_id(session['user_id'])
    
    # Get seller orders
    seller_orders = Order.get_seller_orders(seller['id'])
    
    return render_template('dashboard/seller_orders.html', 
                       seller=seller,
                       orders=seller_orders,
                       title="Manage Orders")

@seller_bp.route('/seller/order/<int:order_id>')
@seller_required
def order_detail(order_id):
    # Get seller data
    seller = Seller.get_by_user_id(session['user_id'])
    
    # Get order details
    order = Order.get_by_id(order_id)
    
    # Check if seller has items in this order
    has_items = False
    if order and 'items' in order:
        for item in order['items']:
            if item['seller_id'] == seller['id']:
                has_items = True
                break
    
    if not order or not has_items:
        flash('Order not found', 'danger')
        return redirect(url_for('seller.orders'))
    
    return render_template('dashboard/seller_order_detail.html', 
                       seller=seller,
                       order=order,
                       title="Order Detail")

@seller_bp.route('/seller/update-order-status', methods=['POST'])
@seller_required
def update_order_status():
    order_id = request.form.get('order_id', type=int)
    status = request.form.get('status')
    
    if not order_id or not status:
        flash('Invalid order or status', 'danger')
        return redirect(url_for('seller.orders'))
    
    # Update order status
    if Order.update_status(order_id, status):
        flash('Order status updated successfully', 'success')
    else:
        flash('Error updating order status', 'danger')
    
    return redirect(url_for('seller.order_detail', order_id=order_id))

@seller_bp.route('/seller/settings')
@seller_required
def settings():
    # Get seller data
    seller = Seller.get_by_user_id(session['user_id'])
    
    return render_template('dashboard/seller_settings.html', 
                       seller=seller,
                       title="Seller Settings")

@seller_bp.route('/seller/settings/update', methods=['POST'])
@seller_required
def update_settings():
    # Get form data
    shop_name = request.form.get('shop_name')
    shop_description = request.form.get('shop_description')
    logo_url = request.form.get('logo_url')
    banner_url = request.form.get('banner_url')
    theme_color = request.form.get('theme_color')
    
    # Get seller data
    seller = Seller.get_by_user_id(session['user_id'])
    
    # Validation
    if not shop_name:
        flash('Shop name is required', 'danger')
        return redirect(url_for('seller.settings'))
    
    # Update seller data
    seller_data = {
        'shop_name': shop_name,
        'shop_description': shop_description,
        'logo_url': logo_url,
        'banner_url': banner_url,
        'theme_color': theme_color
    }
    
    if Seller.update(seller['id'], seller_data):
        flash('Settings updated successfully', 'success')
    else:
        flash('Error updating settings', 'danger')
    
    return redirect(url_for('seller.settings'))

@seller_bp.route('/seller/pages')
@seller_required
def pages():
    # Get seller data
    seller = Seller.get_by_user_id(session['user_id'])
    
    # Get seller pages
    pages = Page.get_seller_pages(seller['id'])
    
    return render_template('dashboard/seller_pages.html', 
                       seller=seller,
                       pages=pages,
                       title="Manage Pages")

@seller_bp.route('/seller/page/add', methods=['GET', 'POST'])
@seller_required
def add_page():
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        content = request.form.get('content')
        slug = request.form.get('slug')
        is_active = request.form.get('is_active') == 'on'
        
        # Get seller data
        seller = Seller.get_by_user_id(session['user_id'])
        
        # Validation
        if not title or not content or not slug:
            flash('Title, content, and slug are required', 'danger')
            return render_template('dashboard/seller_page_form.html', 
                               title="Add Page")
        
        # Create page
        page_id = Page.create(
            seller_id=seller['id'],
            title=title,
            content=content,
            slug=slug,
            is_active=is_active
        )
        
        if page_id:
            flash('Page added successfully', 'success')
            return redirect(url_for('seller.pages'))
        else:
            flash('Error adding page', 'danger')
    
    return render_template('dashboard/seller_page_form.html', 
                       title="Add Page")

@seller_bp.route('/seller/page/edit/<int:page_id>', methods=['GET', 'POST'])
@seller_required
def edit_page(page_id):
    # Get seller data
    seller = Seller.get_by_user_id(session['user_id'])
    
    # Get page data
    page = Page.get_by_id(page_id)
    
    # Verify ownership
    if not page or page['seller_id'] != seller['id']:
        flash('Page not found', 'danger')
        return redirect(url_for('seller.pages'))
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        content = request.form.get('content')
        slug = request.form.get('slug')
        is_active = request.form.get('is_active') == 'on'
        
        # Validation
        if not title or not content or not slug:
            flash('Title, content, and slug are required', 'danger')
            return render_template('dashboard/seller_page_form.html', 
                               page=page,
                               title="Edit Page")
        
        # Update page
        page_data = {
            'title': title,
            'content': content,
            'slug': slug,
            'is_active': is_active
        }
        
        if Page.update(page_id, page_data):
            flash('Page updated successfully', 'success')
            return redirect(url_for('seller.pages'))
        else:
            flash('Error updating page', 'danger')
    
    return render_template('dashboard/seller_page_form.html', 
                       page=page,
                       title="Edit Page")

@seller_bp.route('/seller/page/delete/<int:page_id>', methods=['POST'])
@seller_required
def delete_page(page_id):
    # Get seller data
    seller = Seller.get_by_user_id(session['user_id'])
    
    # Get page data
    page = Page.get_by_id(page_id)
    
    # Verify ownership
    if not page or page['seller_id'] != seller['id']:
        flash('Page not found', 'danger')
        return redirect(url_for('seller.pages'))
    
    # Delete page
    if Page.delete(page_id):
        flash('Page deleted successfully', 'success')
    else:
        flash('Error deleting page', 'danger')
    
    return redirect(url_for('seller.pages'))

# Shop frontend routes
@seller_bp.route('/shop/<int:seller_id>')
def shop_home(seller_id):
    # Get seller data
    seller = Seller.get_by_id(seller_id)
    
    if not seller:
        flash('Shop not found', 'danger')
        return redirect(url_for('market.market'))
    
    # Get seller products
    products = Product.get_all(seller_id=seller_id)
    
    # Get seller pages
    pages = Page.get_seller_pages(seller_id)
    
    return render_template('shop/home.html', 
                       seller=seller,
                       products=products,
                       pages=pages,
                       title=seller['shop_name'])

@seller_bp.route('/shop/<int:seller_id>/page/<slug>')
def shop_page(seller_id, slug):
    # Get seller data
    seller = Seller.get_by_id(seller_id)
    
    if not seller:
        flash('Shop not found', 'danger')
        return redirect(url_for('market.market'))
    
    # Get page data
    page = Page.get_by_slug(seller_id, slug)
    
    if not page or not page['is_active']:
        flash('Page not found', 'danger')
        return redirect(url_for('seller.shop_home', seller_id=seller_id))
    
    # Get seller pages for navigation
    pages = Page.get_seller_pages(seller_id)
    
    return render_template('shop/page.html', 
                       seller=seller,
                       page=page,
                       pages=pages,
                       title=page['title'])

@seller_bp.route('/seller/page/toggle-publish/<int:page_id>', methods=['POST'])
@seller_required
def toggle_publish(page_id):
    # Get seller data
    seller = Seller.get_by_user_id(session['user_id'])
    
    # Get page data
    page = Page.get_by_id(page_id)
    
    # Verify ownership
    if not page or page['seller_id'] != seller['id']:
        flash('Page not found', 'danger')
        return redirect(url_for('seller.pages'))
    
    # Toggle is_active status
    new_status = not page['is_active']
    
    page_data = {
        'is_active': new_status
    }
    
    if Page.update(page_id, page_data):
        status_text = 'published' if new_status else 'unpublished'
        flash(f'Page {status_text} successfully', 'success')
    else:
        flash('Error updating page status', 'danger')
    
    return redirect(url_for('seller.pages'))
