#test

import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_factory_website'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
DATABASE = 'database.db'
GOOGLE_MAP_EMBED_URL = 'https://www.google.com/maps/embed?pb=!1m10!1m8!1m3!1d2262.9326149033272!2d116.72771976465418!3d38.12647611442997!3m2!1i1024!2i768!4f13.1!5e1!3m2!1szh-CN!2sjp!4v1773801946878!5m2!1szh-CN!2sjp'
GOOGLE_MAP_SHARE_URL = 'https://maps.app.goo.gl/CfdrBDpE5sW9126r9'
ADMIN_PASSWORD_HASH = os.getenv(
    'ADMIN_PASSWORD_HASH',
    'scrypt:32768:8:1$8u59Ael7UIuF3xPg$81fbf4d206bbd09fc44636ece26243329fde4ebee666007a172924fc51c3ff7ffed4f154487a0c7cf800507f7b71705b44eef54b5b90fe0af560ab6d50af8d8c'
)

# --- Database Setup ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        # Create Products Table
        db.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_zh TEXT NOT NULL,
                name_en TEXT NOT NULL,
                desc_zh TEXT,
                desc_en TEXT,
                specs_zh TEXT,
                specs_en TEXT,
                image_path TEXT,
                category_id INTEGER DEFAULT 1,
                pdf_path TEXT
            )
        ''')
        # Create Config Table (for general site text)
        db.execute('''
            CREATE TABLE IF NOT EXISTS site_config (
                key TEXT PRIMARY KEY,
                value_zh TEXT,
                value_en TEXT
            )
        ''')
        # Create Categories Table
        db.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_zh TEXT NOT NULL,
                name_en TEXT NOT NULL,
                image_path TEXT,
                sort_order INTEGER DEFAULT 0
            )
        ''')
        # Create Product Images Table
        db.execute('''
            CREATE TABLE IF NOT EXISTS product_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                image_path TEXT
            )
        ''')
        # Create Operation Logs Table
        db.execute('''
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operator TEXT,
                action TEXT,
                target TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if config exists, if not seed it
        cursor = db.execute('SELECT * FROM site_config LIMIT 1')
        if not cursor.fetchone():
            seed_data(db)
        ensure_contact_config(db)
        
        # Ensure categories exist
        cursor = db.execute('SELECT count(*) FROM categories')
        if cursor.fetchone()[0] == 0:
            db.execute('INSERT INTO categories (name_zh, name_en, image_path, sort_order) VALUES (?, ?, ?, ?)', ('连接件', 'Connectors', 'images/factory.jpg', 1))
            db.execute('INSERT INTO categories (name_zh, name_en, image_path, sort_order) VALUES (?, ?, ?, ?)', ('定制件', 'Custom Parts', 'images/factory.jpg', 2))
            
        db.commit()

def seed_data(db):
    configs = [
        ('site_title', '南皮县国瑞五金制造有限公司', 'Nanpi County Guorui Hardware Manufacturing Co., Ltd.'),
        ('company_name', '国瑞五金', 'Guorui Hardware'),
        ('hero_title', '专注精密五金冲压加工二十年', '20 Years Focus on Precision Metal Stamping'),
        ('hero_subtitle', '提供高质量、高精度的五金冲压件定制服务', 'High-quality, high-precision custom metal stamping services'),
        ('address', 'XX省XX市XX工业区XX路88号', 'No. 88, XX Road, XX Industrial Zone, XX City'),
        ('phone', '138-xxxx-xxxx', '138-xxxx-xxxx'),
        ('email', 'contact@example.com', 'contact@example.com')
    ]
    db.executemany('INSERT OR IGNORE INTO site_config (key, value_zh, value_en) VALUES (?, ?, ?)', configs)
    
    # Seed Products
    products = [
        ('电子五金配件', 'Electronic Hardware', '高精度电子元件外壳', 'High precision electronic component housing', '材质: 不锈钢; 厚度: 0.5mm', 'Material: Stainless Steel; Thickness: 0.5mm', 'uploads/product1.jpg'),
        ('汽车零部件', 'Automotive Parts', '汽车发动机支架冲压件', 'Automotive engine bracket stamping parts', '材质: 碳钢; 表面处理: 电泳', 'Material: Carbon Steel; Finish: Electrophoresis', 'uploads/product2.jpg'),
        ('家具五金配件', 'Furniture Hardware', '耐用家具连接件', 'Durable furniture connectors', '材质: 铁; 表面处理: 镀锌', 'Material: Iron; Finish: Galvanized', 'uploads/product3.jpg'),
        ('机箱外壳', 'Chassis & Cabinets', '定制工业控制机箱', 'Custom industrial control chassis', '尺寸: 定制; 防护等级: IP54', 'Size: Custom; IP Rating: IP54', 'uploads/product4.jpg')
    ]
    db.executemany('''
        INSERT INTO products (name_zh, name_en, desc_zh, desc_en, specs_zh, specs_en, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', products)

def ensure_contact_config(db):
    configs = [
        ('address', '河北省沧州市南皮县后上桥开发区开发大街2号', 'No. 2 Kaifa Avenue, Houshangqiao Development Zone, Nanpi County, Cangzhou, Hebei, China'),
        ('phone', '13930722650', '13930722650'),
        ('whatsapp', '+86 15968060478', '+86 15968060478'),
        ('email', 'grmetalstamping@outlook.com', 'grmetalstamping@outlook.com')
    ]
    db.executemany(
        'INSERT OR IGNORE INTO site_config (key, value_zh, value_en) VALUES (?, ?, ?)',
        configs
    )

# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_lang():
    return session.get('lang', 'zh')

def get_trans(key):
    lang = get_lang()
    db = get_db()
    row = db.execute('SELECT value_zh, value_en FROM site_config WHERE key = ?', (key,)).fetchone()
    if row:
        return row[f'value_{lang}']
    return key

def config_val(key):
    return get_trans(key)

def get_map_embed_url():
    return GOOGLE_MAP_EMBED_URL

def get_map_link_url():
    return GOOGLE_MAP_SHARE_URL

def product_image_path(product):
    image_path = product['image_path'] if product and product['image_path'] else ''
    static_root = os.path.join(app.root_path, 'static')
    if image_path:
        full_path = os.path.join(static_root, image_path.replace('/', os.sep))
        if os.path.exists(full_path):
            return image_path
    return 'images/factory.jpg'

app.jinja_env.globals.update(
    get_lang=get_lang,
    get_trans=get_trans,
    config_val=config_val,
    product_image_path=product_image_path
)

def log_operation(action, target, details=''):
    if not session.get('logged_in'): return
    db = get_db()
    db.execute('INSERT INTO operation_logs (operator, action, target, details) VALUES (?, ?, ?, ?)',
               ('admin', action, target, details))
    db.commit()

# --- Routes ---

@app.route('/')
def index():
    db = get_db()
    categories = db.execute('SELECT * FROM categories ORDER BY sort_order').fetchall()
    map_embed_url = get_map_embed_url()
    map_link_url = get_map_link_url()
    return render_template('index.html', categories=categories, map_embed_url=map_embed_url, map_link_url=map_link_url)

@app.route('/category/<int:category_id>')
def category(category_id):
    db = get_db()
    category = db.execute('SELECT * FROM categories WHERE id = ?', (category_id,)).fetchone()
    if not category:
        return "Category not found", 404
    products = db.execute('SELECT * FROM products WHERE category_id = ?', (category_id,)).fetchall()
    return render_template('category.html', category=category, products=products)

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['zh', 'en']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    if not product:
        return "Product not found", 404
    images = db.execute('SELECT * FROM product_images WHERE product_id = ?', (product_id,)).fetchall()
    return render_template('product_detail.html', product=product, images=images)

@app.route('/contact')
def contact():
    map_embed_url = get_map_embed_url()
    map_link_url = get_map_link_url()
    return render_template('contact.html', map_embed_url=map_embed_url, map_link_url=map_link_url)

# --- Admin Routes ---

@app.route('/admin')
def admin_login():
    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_do_login():
    if check_password_hash(ADMIN_PASSWORD_HASH, request.form['password']):
        session['logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    flash('密码错误')
    return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    db = get_db()
    categories = db.execute('SELECT * FROM categories ORDER BY sort_order').fetchall()
    products = db.execute('''
        SELECT p.*, c.name_zh as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
    ''').fetchall()
    configs = db.execute('SELECT * FROM site_config').fetchall()
    logs = db.execute('SELECT * FROM operation_logs ORDER BY created_at DESC LIMIT 50').fetchall()
    return render_template('admin_dashboard.html', categories=categories, products=products, configs=configs, logs=logs)

@app.route('/admin/product/add', methods=['GET', 'POST'])
def add_product():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    db = get_db()
    
    if request.method == 'POST':
        name_zh = request.form['name_zh']
        name_en = request.form['name_en']
        desc_zh = request.form['desc_zh']
        desc_en = request.form['desc_en']
        specs_zh = request.form['specs_zh']
        specs_en = request.form['specs_en']
        category_id = request.form.get('category_id', 1)
        
        image_path = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = f"uploads/{filename}"

        pdf_path = ''
        if 'pdf_file' in request.files:
            pdf_file = request.files['pdf_file']
            if pdf_file and pdf_file.filename.lower().endswith('.pdf'):
                pdf_filename = secure_filename(pdf_file.filename)
                pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename))
                pdf_path = f"uploads/{pdf_filename}"

        cursor = db.execute('''
            INSERT INTO products (name_zh, name_en, desc_zh, desc_en, specs_zh, specs_en, image_path, category_id, pdf_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name_zh, name_en, desc_zh, desc_en, specs_zh, specs_en, image_path, category_id, pdf_path))
        
        product_id = cursor.lastrowid
        
        # Multiple images
        if 'gallery' in request.files:
            files = request.files.getlist('gallery')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    db.execute('INSERT INTO product_images (product_id, image_path) VALUES (?, ?)', (product_id, f"uploads/{filename}"))
        
        db.commit()
        log_operation('Add Product', name_zh, f'Added product ID {product_id}')
        return redirect(url_for('admin_dashboard'))
        
    categories = db.execute('SELECT * FROM categories').fetchall()
    return render_template('product_form.html', action='add', categories=categories)

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    db = get_db()
    if request.method == 'POST':
        name_zh = request.form['name_zh']
        name_en = request.form['name_en']
        desc_zh = request.form['desc_zh']
        desc_en = request.form['desc_en']
        specs_zh = request.form['specs_zh']
        specs_en = request.form['specs_en']
        category_id = request.form.get('category_id', 1)
        
        # Handle Image
        update_sql = "name_zh=?, name_en=?, desc_zh=?, desc_en=?, specs_zh=?, specs_en=?, category_id=?"
        params = [name_zh, name_en, desc_zh, desc_en, specs_zh, specs_en, category_id]
        
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                update_sql += ", image_path=?"
                params.append(f"uploads/{filename}")

        if 'pdf_file' in request.files:
            pdf_file = request.files['pdf_file']
            if pdf_file and pdf_file.filename.lower().endswith('.pdf'):
                pdf_filename = secure_filename(pdf_file.filename)
                pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename))
                update_sql += ", pdf_path=?"
                params.append(f"uploads/{pdf_filename}")
                
        # Multiple images (append)
        if 'gallery' in request.files:
            files = request.files.getlist('gallery')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    db.execute('INSERT INTO product_images (product_id, image_path) VALUES (?, ?)', (product_id, f"uploads/{filename}"))
        
        params.append(product_id)
        
        db.execute(f'UPDATE products SET {update_sql} WHERE id=?', params)
        db.commit()
        log_operation('Edit Product', name_zh, f'Updated product ID {product_id}')
        return redirect(url_for('admin_dashboard'))

    product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    categories = db.execute('SELECT * FROM categories').fetchall()
    return render_template('product_form.html', product=product, action='edit', categories=categories)

@app.route('/admin/product/delete/<int:product_id>')
def delete_product(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    if product:
        db.execute('DELETE FROM products WHERE id = ?', (product_id,))
        db.execute('DELETE FROM product_images WHERE product_id = ?', (product_id,))
        db.commit()
        log_operation('Delete Product', product['name_zh'], f'Deleted product ID {product_id}')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/category/add', methods=['POST'])
def add_category():
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    name_zh = request.form['name_zh']
    name_en = request.form['name_en']
    sort_order = request.form.get('sort_order', 0)
    image_path = ''
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = f"uploads/{filename}"
    db = get_db()
    db.execute('INSERT INTO categories (name_zh, name_en, image_path, sort_order) VALUES (?, ?, ?, ?)',
               (name_zh, name_en, image_path, sort_order))
    db.commit()
    log_operation('Add Category', name_zh)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/category/delete/<int:category_id>')
def delete_category(category_id):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    db = get_db()
    category = db.execute('SELECT * FROM categories WHERE id = ?', (category_id,)).fetchone()
    if category:
        db.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        db.execute('UPDATE products SET category_id = NULL WHERE category_id = ?', (category_id,))
        db.commit()
        log_operation('Delete Category', category['name_zh'])
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/config/update', methods=['POST'])
def update_config():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    db = get_db()
    for key in request.form:
        if key.startswith('zh_'):
            real_key = key[3:]
            val = request.form[key]
            db.execute('UPDATE site_config SET value_zh = ? WHERE key = ?', (val, real_key))
        elif key.startswith('en_'):
            real_key = key[3:]
            val = request.form[key]
            db.execute('UPDATE site_config SET value_en = ? WHERE key = ?', (val, real_key))
    db.commit()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
