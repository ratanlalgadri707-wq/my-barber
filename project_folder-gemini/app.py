from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import json
import os

app = Flask(__name__)
app.secret_key = "super_secret_key" # Needed for sessions and flash messages
DATA_FILE = 'data.json'

# --- HELPER FUNCTIONS ---
def load_data():
    """Read data from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return {"shops": []}
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

def save_data(data):
    """Write data to the JSON file."""
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# --- ROUTES ---

@app.route('/manifest.json')
def serve_manifest():
    """Serve the PWA manifest file."""
    return send_from_directory('.', 'manifest.json', mimetype='application/manifest+json')

@app.route('/')
def index():
    """Public home page showing all shops."""
    data = load_data()
    return render_template('index.html', shops=data['shops'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Shopkeeper registration page."""
    if request.method == 'POST':
        data = load_data()
        
        # Generate new ID
        new_id = 1 if len(data['shops']) == 0 else max(shop['id'] for shop in data['shops']) + 1
        
        new_shop = {
            "id": new_id,
            "shop_name": request.form['shop_name'],
            "barber_name": request.form['barber_name'],
            "mobile": request.form['mobile'],
            "address": request.form['address'],
            "password": request.form['password'],
            "queue_count": 0,
            "shop_status": "closed"
        }
        
        data['shops'].append(new_shop)
        save_data(data)
        
        # Automatically log in the user after registration
        session['shop_id'] = new_id
        return redirect(url_for('dashboard'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Shopkeeper login page."""
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']
        
        data = load_data()
        for shop in data['shops']:
            if shop['mobile'] == mobile and shop['password'] == password:
                session['shop_id'] = shop['id']
                return redirect(url_for('dashboard'))
                
        flash("Invalid mobile number or password!")
        return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Log out the shopkeeper."""
    session.pop('shop_id', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard for the logged-in shopkeeper."""
    if 'shop_id' not in session:
        return redirect(url_for('login'))
        
    data = load_data()
    # Find the logged-in shop's data
    shop = next((s for s in data['shops'] if s['id'] == session['shop_id']), None)
    
    if not shop:
        return redirect(url_for('logout'))
        
    return render_template('dashboard.html', shop=shop)

@app.route('/add')
def add_queue():
    """Increase the queue count."""
    if 'shop_id' in session:
        data = load_data()
        for shop in data['shops']:
            if shop['id'] == session['shop_id']:
                shop['queue_count'] += 1
                break
        save_data(data)
    return redirect(url_for('dashboard'))

@app.route('/remove')
def remove_queue():
    """Decrease the queue count (minimum 0)."""
    if 'shop_id' in session:
        data = load_data()
        for shop in data['shops']:
            if shop['id'] == session['shop_id']:
                if shop['queue_count'] > 0:
                    shop['queue_count'] -= 1
                break
        save_data(data)
    return redirect(url_for('dashboard'))

@app.route('/open_shop')
def open_shop():
    """Set shop status to open."""
    if 'shop_id' in session:
        data = load_data()
        for shop in data['shops']:
            if shop['id'] == session['shop_id']:
                shop['shop_status'] = "open"
                break
        save_data(data)
    return redirect(url_for('dashboard'))

@app.route('/close_shop')
def close_shop():
    """Set shop status to closed."""
    if 'shop_id' in session:
        data = load_data()
        for shop in data['shops']:
            if shop['id'] == session['shop_id']:
                shop['shop_status'] = "closed"
                break
        save_data(data)
    return redirect(url_for('dashboard'))

@app.route('/shop/<int:id>')
def shop_detail(id):
    """Public page to view details of a specific shop."""
    data = load_data()
    shop = next((s for s in data['shops'] if s['id'] == id), None)
    
    if not shop:
        return "Shop not found", 404
        
    return render_template('shop.html', shop=shop)

if __name__ == '__main__':
    app.run(debug=True)