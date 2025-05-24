
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import Product, Category, Cart, Review, Order
from routes.auth import login_required

market_bp = Blueprint('market', __name__)

@market_bp.route('/market')
def market():
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', None, type=int)
    search = request.args.get('search', None)
    
    # Get products per page from config
    from flask import current_app
    items_per_page = current_app.config['ITEMS_PER_PAGE']
    offset = (page - 1) * items_per_page
    
    # Get products
    products = Product.get_all(
        limit=items_per_page,
        offset=offset,
        category_id=category_id,
        search=search
    )
    
    # Get categories for sidebar
    categories = Category.get_all()
    
    # Get category name if filtered
    category_name = None
    if category_id:
        category = Category.get_by_id(category_id)
        if category:
            category_name = category['name']
    
    return render_template('market.html', 
                        products=products, 
                        categories=categories,
                        category_id=category_id,
                        category_name=category_name,
                        search=search,
                        page=page,
                        title="Market")

@market_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    # Get product details
    product = Product.get_by_id(product_id)
    
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('market.market'))
    
    # Get related products (same category)
    related_products = []
    if product['category_id']:
        related_products = Product.get_all(
            limit=4,
            category_id=product['category_id']
        )
        # Remove current product from related products
        related_products = [p for p in related_products if p['id'] != product_id]
    
    return render_template('product_detail.html', 
                        product=product, 
                        related_products=related_products,
                        title=product['name'])

@market_bp.route('/cart')
def cart():
    # If user is not logged in, show empty cart
    if 'user_id' not in session:
        return render_template('cart.html', 
                            cart={'items': [], 'total': 0, 'item_count': 0},
                            title="Shopping Cart")
    
    # Get cart data
    cart_data = Cart.get_user_cart(session['user_id'])
    
    return render_template('cart.html', 
                        cart=cart_data,
                        title="Shopping Cart")

@market_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    if not product_id or quantity <= 0:
        flash('Invalid product or quantity', 'danger')
        return redirect(url_for('market.market'))
    
    # Add to cart
    if Cart.add_item(session['user_id'], product_id, quantity):
        flash('Product added to cart', 'success')
    else:
        flash('Error adding product to cart', 'danger')
    
    # Determine redirect URL
    referer = request.referrer
    if referer and 'product' in referer:
        return redirect(referer)
    else:
        return redirect(url_for('market.market'))

@market_bp.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    cart_id = request.form.get('cart_id', type=int)
    quantity = request.form.get('quantity', type=int)
    
    if not cart_id or not quantity:
        return jsonify({'success': False, 'message': 'Invalid cart item or quantity'})
    
    # Update cart
    if Cart.update_quantity(cart_id, quantity):
        # Get updated cart data
        cart_data = Cart.get_user_cart(session['user_id'])
        
        return jsonify({
            'success': True, 
            'message': 'Cart updated',
            'cart': {
                'total': cart_data['total'],
                'item_count': cart_data['item_count']
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Error updating cart'})

@market_bp.route('/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    cart_id = request.form.get('cart_id', type=int)
    
    if not cart_id:
        return jsonify({'success': False, 'message': 'Invalid cart item'})
    
    # Remove from cart
    if Cart.remove_item(cart_id):
        # Get updated cart data
        cart_data = Cart.get_user_cart(session['user_id'])
        
        return jsonify({
            'success': True, 
            'message': 'Item removed from cart',
            'cart': {
                'total': cart_data['total'],
                'item_count': cart_data['item_count']
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Error removing item from cart'})

@market_bp.route('/checkout')
@login_required
def checkout():
    # Get cart data
    cart_data = Cart.get_user_cart(session['user_id'])
    
    if not cart_data['items']:
        flash('Your cart is empty', 'info')
        return redirect(url_for('market.cart'))
    
    # Get user data
    from models import User
    user = User.get_by_id(session['user_id'])    # ← fixed!

    # Now you can render checkout with both cart_data and user
    return render_template(
        'checkout.html',
        user=user,
        cart=cart_data
    )


@market_bp.route('/place-order', methods=['POST'])
@login_required
def place_order():
    # 1) Gather user & cart
    user_id   = session['user_id']
    cart_data = Cart.get_user_cart(user_id)
    items     = cart_data.get('items', [])
    total     = cart_data.get('total_amount', 0)

    if not items:
        flash('Your cart is empty', 'info')
        return redirect(url_for('market.cart'))

    shipping_address = request.form.get('shipping_address', '').strip()
    first_name       = request.form.get('first_name', '').strip()
    last_name        = request.form.get('last_name', '').strip()
    email            = request.form.get('email', '').strip()
    phone            = request.form.get('phone', '').strip()

    if not shipping_address or not first_name or not last_name or not email:
        flash('Thank you for the order', 'warning')
        return redirect(url_for('market.checkout'))

    # 3) Create the Order
    order_id = Order.create(
        user_id=user_id,
        total_amount=total,
        shipping_address=shipping_address,
        order_status='pending',
        payment_status='pending'
    )

    if not order_id:
        flash('Could not place your order. Please try again.', 'danger')
        return redirect(url_for('market.checkout'))

    # 4) Create OrderItems
    for it in items:
        OrderItem.create(
            order_id=order_id,
            product_id=it['id'],
            seller_id=it.get('seller_id'),
            quantity=it['quantity'],
            price=it['price'],
            subtotal=it['subtotal']
        )

    # 5) Clear the cart
    Cart.clear_user_cart(user_id)

    flash('Your order has been placed successfully!', 'success')
    return redirect(url_for('market.order_confirmation', order_id=order_id))
