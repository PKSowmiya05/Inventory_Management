# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from models import db, Product, Location, ProductMovement
from sqlalchemy import text
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'inventory_secret_123')

# --------- Database config (SQLite for local/testing) ----------
# If you want to switch to MySQL later, change this URI.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables and run a tiny migration to add new columns if the DB is old
with app.app_context():
    db.create_all()
    # Run a one-time migration using a proper connection (compatible with SQLAlchemy 1.4+)
    try:
        with db.engine.connect() as conn:
            res = conn.execute(text("PRAGMA table_info(product)"))
            existing = [row[1] for row in res.fetchall()]
            if 'quantity' not in existing:
                conn.execute(text("ALTER TABLE product ADD COLUMN quantity INTEGER NOT NULL DEFAULT 0"))
            if 'location_id' not in existing:
                conn.execute(text("ALTER TABLE product ADD COLUMN location_id INTEGER"))
    except Exception as e:
        # Migration isn't critical for a fresh DB; log and continue
        print('Migration check error:', e)


# we ran the migration once above inside app.app_context(); that's sufficient for dev usage

# -------------------- Helper functions -------------------- #
def get_product_name(pid):
    p = Product.query.get(pid)
    return p.name if p else "Unknown Product"

def get_location_name(lid):
    if lid is None:
        return '---'
    loc = Location.query.get(lid)
    return loc.name if loc else 'Unknown Location'

# -------------------- Routes -------------------- #
@app.route('/')
def home():
    return render_template('home.html')

# ---------- PRODUCTS ----------
@app.route('/products')
def products():
    products = Product.query.order_by(Product.id).all()
    return render_template('products.html', products=products)

@app.route('/product/add', methods=['GET', 'POST'])
def add_product():
    # fetch locations for the dropdown
    locations = Location.query.order_by(Location.name).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        qty_raw = request.form.get('quantity', '0')
        loc_in = request.form.get('location') or ''
        try:
            quantity = int(qty_raw)
        except ValueError:
            flash("Quantity must be a number.")
            return redirect(url_for('add_product'))

        if not name:
            flash("Product name is required.")
            return redirect(url_for('add_product'))

        # resolve location id or None
        location_id = int(loc_in) if loc_in else None

        new_p = Product(name=name, description=description, quantity=quantity, location_id=location_id)
        db.session.add(new_p)
        db.session.commit()
        flash("✅ Product added.")
        return redirect(url_for('products'))

    return render_template('include_product.html', locations=locations)

@app.route('/product/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    # fetch locations for the dropdown
    locations = Location.query.order_by(Location.name).all()
    if request.method == 'POST':
        product.name = request.form.get('name', product.name).strip()
        qty_raw = request.form.get('quantity', product.quantity)
        loc_in = request.form.get('location') or ''
        try:
            product.quantity = int(qty_raw)
        except ValueError:
            flash('Quantity must be a number.')
            return redirect(url_for('edit_product', id=id))

        product.location_id = int(loc_in) if loc_in else None
        db.session.commit()
        flash("✏️ Product updated.")
        return redirect(url_for('products'))

    # render edit form with locations list
    return render_template('alter_product.html', product=product, locations=locations)

@app.route('/product/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash("🗑️ Product deleted.")
    return redirect(url_for('products'))

# ---------- LOCATIONS ----------
@app.route('/locations')
def location():
    # template file is 'location.html' (singular) and templates expect endpoint name 'location'
    locations = Location.query.order_by(Location.id).all()
    return render_template('location.html', locations=locations)

@app.route('/location/add', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash("Location name is required.")
            return redirect(url_for('add_location'))
        new_l = Location(name=name)
        db.session.add(new_l)
        db.session.commit()
        flash("✅ Location added.")
        return redirect(url_for('location'))
    # template file is 'include_location.html' for GET
    return render_template('include_location.html')

@app.route('/location/edit/<int:id>', methods=['GET', 'POST'])
def edit_location(id):
    location = Location.query.get_or_404(id)
    if request.method == 'POST':
        location.name = request.form.get('name', location.name).strip()
        db.session.commit()
        flash("✏️ Location updated.")
        return redirect(url_for('location'))
    # template file is 'alter_location.html' for GET
    return render_template('alter_location.html', location=location)

@app.route('/location/delete/<int:id>', methods=['POST'])
def delete_location(id):
    location = Location.query.get_or_404(id)
    db.session.delete(location)
    db.session.commit()
    flash("🗑️ Location deleted.")
    return redirect(url_for('location'))

# ---------- MOVEMENTS ----------
@app.route('/movements')
def move_product():
    # endpoint name expected by templates is 'move_product' and template file is 'move_product.html'
    moves = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    # Build a friendly list with names (so templates show names not raw ids)
    movement_list = []
    for m in moves:
        movement_list.append({
            'id': m.id,
            'product_name': get_product_name(m.product_id),
            'from_location': get_location_name(m.from_location),
            'to_location': get_location_name(m.to_location),
            'qty': m.qty,
            'timestamp': m.timestamp
        })
    return render_template('move_product.html', movements=movement_list)

@app.route('/movement/add', methods=['GET', 'POST'])
def add_movement():
    # For GET we no longer need lists since user types names/ids
    if request.method == 'POST':
        product_input = request.form.get('product', '').strip()
        from_input = (request.form.get('from_location') or '').strip()
        to_input = (request.form.get('to_location') or '').strip()
        qty_raw = request.form.get('qty', '0')
        try:
            qty = int(qty_raw)
        except ValueError:
            flash("Quantity must be a number.")
            return redirect(url_for('add_movement'))

        # validations
        if not product_input:
            flash("Please enter a product name or id.")
            return redirect(url_for('add_movement'))
        if not from_input and not to_input:
            flash("Choose at least one of From or To location (enter name or id).")
            return redirect(url_for('add_movement'))
        if qty <= 0:
            flash("Quantity must be at least 1.")
            return redirect(url_for('add_movement'))

        # helper to resolve product (id or name) -> product_id
        def resolve_product(inp):
            if inp.isdigit():
                return int(inp)
            # look up by name (case-sensitive). If not found, create it.
            p = Product.query.filter_by(name=inp).first()
            if p:
                return p.id
            newp = Product(name=inp)
            db.session.add(newp)
            db.session.commit()
            return newp.id

        # helper to resolve location (id or name) -> location id or None
        def resolve_location(inp):
            if not inp:
                return None
            if inp.isdigit():
                return int(inp)
            loc = Location.query.filter_by(name=inp).first()
            if loc:
                return loc.id
            newl = Location(name=inp)
            db.session.add(newl)
            db.session.commit()
            return newl.id

        product_id = resolve_product(product_input)
        from_loc = resolve_location(from_input)
        to_loc = resolve_location(to_input)

        # create movement
        move = ProductMovement(product_id=product_id, from_location=from_loc, to_location=to_loc, qty=qty)
        db.session.add(move)
        db.session.commit()
        flash("✅ Movement recorded.")
        return redirect(url_for('move_product'))

    # template file is 'include_move.html' for GET
    return render_template('include_move.html')

@app.route('/movement/delete/<int:id>', methods=['POST'])
def delete_movement(id):
    move = ProductMovement.query.get_or_404(id)
    db.session.delete(move)
    db.session.commit()
    flash("🗑️ Movement deleted.")
    return redirect(url_for('move_product'))


@app.route('/movement/edit/<int:id>', methods=['GET', 'POST'])
def edit_movement(id):
    movement = ProductMovement.query.get_or_404(id)
    products = Product.query.order_by(Product.name).all()
    locations = Location.query.order_by(Location.name).all()

    if request.method == 'POST':
        # Read and validate form data
        prod = request.form.get('product')
        from_loc = request.form.get('from_location') or None
        to_loc = request.form.get('to_location') or None
        qty_raw = request.form.get('qty', '0')
        try:
            qty = int(qty_raw)
        except ValueError:
            flash('Quantity must be a number.')
            return redirect(url_for('edit_movement', id=id))

        if not prod:
            flash('Please select a product.')
            return redirect(url_for('edit_movement', id=id))

        movement.product_id = int(prod)
        movement.from_location = int(from_loc) if from_loc else None
        movement.to_location = int(to_loc) if to_loc else None
        movement.qty = qty
        db.session.commit()
        flash('✏️ Movement updated.')
        return redirect(url_for('move_product'))

    return render_template('edit_movement.html', movement=movement, products=products, locations=locations)



# ---------- REPORT ----------
@app.route('/report')
def report():
    # Build balances starting from current products, then apply movements.
    # This way a newly added product with an initial location/quantity shows up automatically.
    balances = {}  # key: (product_id, location_id) -> qty

    # Start with product initial quantities (simple loop, no ORM magic)
    products = Product.query.order_by(Product.id).all()
    for p in products:
        if p.location_id:
            key = (p.id, p.location_id)
            balances[key] = balances.get(key, 0) + (p.quantity or 0)

    # Apply movements: subtract from from_location, add to to_location
    moves = ProductMovement.query.order_by(ProductMovement.timestamp).all()
    for m in moves:
        if m.from_location:
            key = (m.product_id, m.from_location)
            balances[key] = balances.get(key, 0) - m.qty
        if m.to_location:
            key = (m.product_id, m.to_location)
            balances[key] = balances.get(key, 0) + m.qty

    # Build list for template: each row is a product-location pair with its computed qty
    report_rows = []
    for (pid, lid), qty in balances.items():
        if qty == 0:
            continue
        report_rows.append({
            'product_name': get_product_name(pid),
            'location_name': get_location_name(lid),
            'qty': qty
        })

    # sort by product then location for stable output
    report_rows.sort(key=lambda r: (r['product_name'], r['location_name']))
    return render_template('finalreport.html', report=report_rows)


# add alias so templates using endpoint 'finalreport' also work (some templates refer to 'finalreport')
app.add_url_rule('/report', endpoint='finalreport', view_func=report)

# ---------------- Main ---------------- #
if __name__ == '__main__':
    # run debug locally
    app.run(debug=True)
