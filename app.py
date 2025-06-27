from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=True)
    surname = db.Column(db.String(150), nullable=True)
    number = db.Column(db.String(150), nullable=True)

# Модель заказа
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start = db.Column(db.String(150), nullable=False)
    end = db.Column(db.String(150), nullable=False)
    driver_name = db.Column(db.String(100), nullable=False)
    car_number = db.Column(db.String(20), nullable=False)
    driver_rating = db.Column(db.Float)  # Для рейтинга водителя
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def generate_driver_info():
        # Генерация случайного имени водителя
        names = ['Ivan', 'Petr', 'Svetlana', 'Olga', 'Alexey']
        driver_name = random.choice(names)

        # Генерация случайного номера машины
        car_number = ''.join(random.choices(string.ascii_uppercase, k=1)) + ''.join(random.choices(string.digits, k=3)) + \
            ''.join(random.choices(string.ascii_uppercase, k=2)) + ''.join(random.choices(string.digits, k=2))

        # Генерация случайного рейтинга от 1 до 5
        driver_rating = round(random.uniform(1, 5), 1)

        return driver_name, car_number, driver_rating

# Инициализация базы данных
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!')
            return redirect(url_for('profile'))
        else:
            flash('Incorrect email or password.')
    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.email = request.form['email']
        user.password = request.form['password'] 
        user.name = request.form['name'] 
        user.surname = request.form['surname'] 
        user.number = request.form['number']   # Обновление имени пользователя
        db.session.commit()
        flash('Profile updated!')

    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/order', methods=['GET', 'POST'])
def order():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        start = request.form['start']
        end = request.form['end']

        driver_name, car_number, driver_rating = Order.generate_driver_info()  # Ваша функция генерации
        new_order = Order(user_id=session['user_id'],
                      start=start,
                      end=end,
                      driver_name=driver_name,
                      car_number=car_number,
                      driver_rating=driver_rating)

        db.session.add(new_order)
        db.session.commit()
        flash('Order created!')
        
    return render_template('order.html')

@app.route('/orders_history')
def orders_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_orders = Order.query.filter_by(user_id=session['user_id']).all()
    return render_template('orders_history.html', orders=user_orders)

if __name__ == '__main__':
    app.run(debug=True)