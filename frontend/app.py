"""
Agam Organics - Flask Frontend Application
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Backend API URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')


# Helper Functions
def get_headers():
    """Get authorization headers if user is logged in"""
    token = session.get('access_token')
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            flash('Please login to continue', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def api_call(method, endpoint, **kwargs):
    """Make API call to backend"""
    url = f"{BACKEND_URL}{endpoint}"
    try:
        response = requests.request(method, url, **kwargs)
        return response
    except Exception as e:
        print(f"API Error: {e}")
        return None


# Routes
@app.route('/')
def home():
    """Home page with product listing"""
    # Get query parameters for filtering and sorting
    category = request.args.get('category', '')
    sort_by = request.args.get('sort_by', 'created_at')
    search = request.args.get('search', '')
    
    # Build API query parameters
    params = {
        'page': 1,
        'page_size': 20
    }
    
    if category:
        params['category'] = category
    if sort_by:
        params['sort_by'] = sort_by
    if search:
        params['search'] = search
    
    # Build query string
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    response = api_call('GET', f'/api/products?{query_string}')
    
    products = []
    categories = []
    banners = []
    
    if response and response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
    
    # Fetch categories
    cat_response = api_call('GET', '/api/products/categories')
    if cat_response and cat_response.status_code == 200:
        categories = cat_response.json().get('categories', [])
    
    # Fetch banners
    banner_response = api_call('GET', '/api/banners')
    if banner_response and banner_response.status_code == 200:
        banners = banner_response.json()
    
    return render_template(
        'home.html', 
        products=products, 
        categories=categories,
        banners=banners,
        selected_category=category,
        selected_sort=sort_by
    )


@app.route('/product/<product_id>')
def product_detail(product_id):
    """Product detail page"""
    # Get product details
    product_response = api_call('GET', f'/api/products/{product_id}')
    
    if not product_response or product_response.status_code != 200:
        flash('Product not found', 'error')
        return redirect(url_for('home'))
    
    product = product_response.json()
    
    # Get similar products
    similar_response = api_call('GET', f'/api/products/similar/{product_id}')
    similar_products = []
    if similar_response and similar_response.status_code == 200:
        similar_products = similar_response.json().get('products', [])
    
    # Get reviews
    reviews_response = api_call('GET', f'/api/reviews/{product_id}')
    reviews_data = {'reviews': [], 'total': 0, 'average_rating': 0.0}
    if reviews_response and reviews_response.status_code == 200:
        reviews_data = reviews_response.json()
    
    return render_template(
        'product_detail.html',
        product=product,
        similar_products=similar_products,
        reviews=reviews_data
    )


@app.route('/cart')
@login_required
def cart():
    """Shopping cart page"""
    response = api_call('GET', '/api/cart', headers=get_headers())
    
    cart_data = {'items': [], 'total_items': 0, 'total_price': 0}
    
    if response and response.status_code == 200:
        cart_data = response.json()
    
    return render_template('cart.html', cart=cart_data)


@app.route('/checkout')
@login_required
def checkout():
    """Checkout page"""
    # Get cart
    cart_response = api_call('GET', '/api/cart', headers=get_headers())
    
    if not cart_response or cart_response.status_code != 200:
        flash('Error loading cart', 'error')
        return redirect(url_for('cart'))
    
    cart_data = cart_response.json()
    
    if not cart_data.get('items'):
        flash('Your cart is empty', 'error')
        return redirect(url_for('home'))
    
    # Get addresses
    addresses_response = api_call('GET', '/api/profile/addresses', headers=get_headers())
    addresses = []
    if addresses_response and addresses_response.status_code == 200:
        addresses = addresses_response.json()
    
    return render_template('checkout.html', cart=cart_data, addresses=addresses)


@app.route('/orders/<order_id>')
@login_required
def order_details(order_id):
    """Order details page"""
    print(f"[DEBUG] Fetching order details for order_id: {order_id}")
    print(f"[DEBUG] Headers: {get_headers()}")
    
    response = api_call('GET', f'/api/orders/{order_id}', headers=get_headers())
    
    print(f"[DEBUG] Response status: {response.status_code if response else 'None'}")
    if response and response.status_code != 200:
        try:
            error_data = response.json()
            print(f"[DEBUG] Error response: {error_data}")
            flash(f"Order error: {error_data.get('detail', 'Order not found')}", 'error')
        except:
            print(f"[DEBUG] Response text: {response.text if response else 'None'}")
            flash('Order not found', 'error')
        return redirect(url_for('profile'))
    
    if not response:
        print("[DEBUG] No response from backend")
        flash('Unable to connect to server', 'error')
        return redirect(url_for('profile'))
    
    order = response.json()
    print(f"[DEBUG] Order data received: {order.get('order_number', 'N/A')}")
    return render_template('order_details.html', order=order)


@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    # Get user profile
    profile_response = api_call('GET', '/api/profile', headers=get_headers())
    
    if not profile_response or profile_response.status_code != 200:
        flash('Error loading profile', 'error')
        return redirect(url_for('home'))
    
    user_profile = profile_response.json()
    
    # Get addresses
    addresses_response = api_call('GET', '/api/profile/addresses', headers=get_headers())
    addresses = []
    if addresses_response and addresses_response.status_code == 200:
        addresses = addresses_response.json()
    
    # Get orders
    orders_response = api_call('GET', '/api/orders', headers=get_headers())
    orders = []
    if orders_response and orders_response.status_code == 200:
        orders = orders_response.json()
    
    return render_template('profile.html', user=user_profile, addresses=addresses, orders=orders)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        response = api_call('POST', '/api/auth/login', json={
            'email': email,
            'password': password
        })
        
        if response and response.status_code == 200:
            data = response.json()
            session['access_token'] = data['access_token']
            session['refresh_token'] = data['refresh_token']
            
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        response = api_call('POST', '/api/auth/signup', json={
            'email': email,
            'password': password,
            'full_name': full_name,
            'phone': phone
        })
        
        if response and response.status_code == 201:
            data = response.json()
            session['access_token'] = data['access_token']
            session['refresh_token'] = data['refresh_token']
            
            flash('Account created successfully!', 'success')
            return redirect(url_for('home'))
        else:
            error = response.json().get('detail', 'Registration failed') if response else 'Registration failed'
            flash(error, 'error')
    
    return render_template('signup.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))


# Debug endpoint
@app.route('/debug/session')
def debug_session():
    """Debug endpoint to check session"""
    return jsonify({
        'has_access_token': 'access_token' in session,
        'access_token_preview': session.get('access_token', 'None')[:50] + '...' if 'access_token' in session else 'None',
        'session_keys': list(session.keys())
    })


# API endpoints for AJAX calls
@app.route('/api/products')
def api_products():
    """Get products for AJAX requests"""
    # Get query parameters
    category = request.args.get('category', '')
    sort_by = request.args.get('sort_by', 'created_at')
    search = request.args.get('search', '')
    page = request.args.get('page', '1')
    page_size = request.args.get('page_size', '20')
    
    # Build API query parameters
    params = {
        'page': page,
        'page_size': page_size
    }
    
    if category:
        params['category'] = category
    if sort_by:
        params['sort_by'] = sort_by
    if search:
        params['search'] = search
    
    # Build query string
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    response = api_call('GET', f'/api/products?{query_string}')
    
    if response and response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'products': [], 'total': 0}), 500


@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """Add item to cart via AJAX"""
    data = request.get_json()
    headers = get_headers()
    print(f"DEBUG: Headers being sent: {headers}")
    print(f"DEBUG: Data being sent: {data}")
    response = api_call('POST', '/api/cart/add', headers=headers, json=data)
    
    if response:
        print(f"DEBUG: Response status: {response.status_code}")
        print(f"DEBUG: Response body: {response.text}")
    else:
        print("DEBUG: No response from backend")
    
    if response and response.status_code == 201:
        return jsonify({'success': True, 'message': 'Added to cart'})
    else:
        error = response.json().get('detail', 'Failed to add to cart') if response else 'Failed to add to cart'
        return jsonify({'success': False, 'message': error}), 400


@app.route('/api/cart/update/<cart_item_id>', methods=['PUT'])
@login_required
def update_cart_item(cart_item_id):
    """Update cart item quantity via AJAX"""
    data = request.get_json()
    response = api_call('PUT', f'/api/cart/update/{cart_item_id}', headers=get_headers(), json=data)
    
    if response and response.status_code == 200:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False}), 400


@app.route('/api/cart/remove/<cart_item_id>', methods=['DELETE'])
@login_required
def remove_cart_item(cart_item_id):
    """Remove cart item via AJAX"""
    response = api_call('DELETE', f'/api/cart/remove/{cart_item_id}', headers=get_headers())
    
    if response and response.status_code == 200:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False}), 400


@app.route('/api/cart', methods=['GET'])
@login_required
def get_cart_api():
    """Get cart data via AJAX"""
    response = api_call('GET', '/api/cart', headers=get_headers())
    
    if response and response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to fetch cart'}), 400


@app.route('/api/checkout/razorpay-order', methods=['POST'])
@login_required
def create_razorpay_order():
    """Create Razorpay order via AJAX"""
    response = api_call('POST', '/api/checkout/razorpay-order', 
                       headers=get_headers(), 
                       json=request.json)
    
    if response and response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to create order'}), 400


@app.route('/api/checkout/create-order', methods=['POST'])
@login_required
def create_order_api():
    """Create order via AJAX"""
    response = api_call('POST', '/api/checkout/create-order', 
                       headers=get_headers(), 
                       json=request.json)
    
    if response and response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to create order'}), 400


@app.route('/api/profile/addresses', methods=['POST'])
@login_required
def add_address_api():
    """Add address via AJAX"""
    response = api_call('POST', '/api/profile/addresses', 
                       headers=get_headers(), 
                       json=request.json)
    
    if response and response.status_code == 201:
        return jsonify(response.json()), 201
    else:
        return jsonify({'error': 'Failed to add address'}), 400


@app.route('/api/orders/<order_id>/cancel', methods=['PUT'])
@login_required
def cancel_order_api(order_id):
    """Cancel order via AJAX"""
    response = api_call('PUT', f'/api/orders/{order_id}/cancel', 
                       headers=get_headers())
    
    if response and response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        error_detail = response.json().get('detail', 'Failed to cancel order') if response else 'Failed to cancel order'
        return jsonify({'detail': error_detail}), response.status_code if response else 400


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)
