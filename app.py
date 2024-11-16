import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'user', 'admin', or 'owner'

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    author_bio = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    book = db.relationship('Book')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Seed Owner Account
@app.before_first_request
def create_owner():
    if not User.query.filter_by(role="owner").first():
        owner_password = generate_password_hash("12345", method='sha256')
        owner = User(username="Owner", password=owner_password, role="owner")
        db.session.add(owner)
        db.session.commit()


# Routes
@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = 'user'  # Все зарегистрированные пользователи становятся 'user'

        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if current_user.role not in ['admin', 'owner']:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        price = request.form.get('price')
        image_url = request.form.get('image_url') or 'images/default_book.jpg'
        description = request.form.get('description')
        author_bio = request.form.get('author_bio')
        category = request.form.get('category')

        new_book = Book(
            title=title,
            author=author,
            price=price,
            image_url=image_url,
            description=description,
            author_bio=author_bio,
            category=category
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!')
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/add_admin', methods=['GET', 'POST'])
@login_required
def add_admin():
    if current_user.role != 'owner':
        flash('Only the owner can add admins.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('add_admin'))

        hashed_password = generate_password_hash(password, method='sha256')
        new_admin = User(username=username, password=hashed_password, role='admin')
        db.session.add(new_admin)
        db.session.commit()
        flash('Admin added successfully!')
        return redirect(url_for('index'))
    return render_template('add_admin.html')

@app.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if current_user.role not in ['admin', 'owner']:
        flash('You do not have permission to delete books.')
        return redirect(url_for('index'))

    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash(f'Book "{book.title}" has been deleted successfully.')
    return redirect(url_for('index'))

@app.route('/category/<category>')
def category(category):
    filtered_books = Book.query.filter_by(category=category).all()
    return render_template('category.html', books=filtered_books, category_name=category.capitalize())

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.book.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/add_to_cart/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=current_user.id, book_id=book_id)
        db.session.add(cart_item)
    db.session.commit()
    flash('Book added to cart!')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        flash('You do not have permission to delete this item.')
        return redirect(url_for('cart'))
    db.session.delete(cart_item)
    db.session.commit()
    flash('Book removed from cart.')
    return redirect(url_for('cart'))

@app.route('/search_suggestions')
def search_suggestions():
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify([])

    suggestions = Book.query.filter(Book.title.ilike(f'%{query}%')).limit(5).all()
    return jsonify([{'id': book.id, 'title': book.title} for book in suggestions])

# API для загрузки и скачивания файлов
@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if current_user.role not in ['admin', 'owner']:
        return jsonify({"error": "Permission denied"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    return jsonify({"message": "File uploaded successfully", "filename": file.filename}), 201

@app.route('/download/<string:filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "price": book.price,
        "category": book.category
    } for book in books])

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book_details(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify({
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "price": book.price,
        "description": book.description,
        "category": book.category
    })

@app.route('/books/add', methods=['POST'])
@login_required
def add_book_api():
    if current_user.role not in ['admin', 'owner']:
        return jsonify({"error": "Permission denied"}), 403

    data = request.get_json()
    new_book = Book(
        title=data['title'],
        author=data['author'],
        price=data['price'],
        description=data.get('description'),
        category=data.get('category', 'Uncategorized')
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book added successfully!"}), 201

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)