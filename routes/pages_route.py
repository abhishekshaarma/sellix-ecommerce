from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import Page, Seller

page_bp = Blueprint('page', __name__, url_prefix='/pages')

@page_bp.route('/<slug>')
def view(slug):
    """Public view for a page by slug"""
    
    page = Page.get_by_slug_any_seller(slug)
    
    if not page or not page['is_active']:
        abort(404)  # Page not found or not published
    
    # Get seller info
    seller = Seller.get_by_id(page['seller_id'])
    
    if not seller:
        abort(404)  # Seller not found
    
    # Get seller pages for navigation
    pages = Page.get_seller_pages(seller['id'])
    
    return render_template('page_view.html', 
                          page=page, 
                          seller=seller,
                          pages=pages,
                          title=page['title'])

@staticmethod
def get_by_slug_any_seller(slug):
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
"""
"""
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
"""
