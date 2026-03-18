from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# МОДЕЛИ БАЗЫ ДАННЫХ
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    places = db.relationship('TripPlace', backref='trip', lazy=True, cascade='all, delete-orphan')

class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    region = db.Column(db.String(100))
    budget_level = db.Column(db.String(50))
    image_url = db.Column(db.String(500))
    rating = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TripPlace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)
    day_number = db.Column(db.Integer)
    order_index = db.Column(db.Integer)
    notes = db.Column(db.Text)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_days = db.Column(db.Integer)
    price = db.Column(db.Integer)
    places = db.Column(db.Text)  # JSON строка с ID мест
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ФУНКЦИЯ СОЗДАНИЯ ТЕСТОВЫХ ДАННЫХ
def init_database():
    with app.app_context():
        db.create_all()
        
        # Проверяем, есть ли уже места
        if Place.query.count() == 0:
            print("Создаю тестовые данные...")
            places = [
                Place(
                    name="Красная площадь",
                    description="Главная площадь Москвы с собором Василия Блаженного, мавзолеем и историческим музеем. Символ России, известный во всем мире.",
                    region="msk",
                    budget_level="medium",
                    image_url="https://images.unsplash.com/photo-1554995207-c18c203602cb?w=500",
                    rating=4.9
                ),
                Place(
                    name="Государственный Эрмитаж",
                    description="Один из величайших художественных музеев мира с коллекцией более 3 миллионов произведений искусства.",
                    region="spb",
                    budget_level="premium",
                    image_url="https://images.unsplash.com/photo-1559650656-5d1d361ad10e?w=500",
                    rating=4.8
                ),
                Place(
                    name="Остров Кижи",
                    description="Музей деревянного зодчества под открытым небом с знаменитой 22-главой Преображенской церковью.",
                    region="karelia",
                    budget_level="medium",
                    image_url="https://images.unsplash.com/photo-1580155405015-5d1793518f7a?w=500",
                    rating=4.7
                ),
                Place(
                    name="Озеро Байкал",
                    description="Самое глубокое озеро на планете, содержащее 20% всей пресной воды мира. Уникальная природа и эндемичные виды.",
                    region="baikal",
                    budget_level="premium",
                    image_url="https://images.unsplash.com/photo-1597265822404-7dbb5f0eae1e?w=500",
                    rating=5.0
                ),
                Place(
                    name="Суздаль",
                    description="Город-музей, часть Золотого кольца России с многочисленными монастырями, церквями и деревянными постройками.",
                    region="golden",
                    budget_level="economy",
                    image_url="https://images.unsplash.com/photo-1580155405015-5d1793518f7a?w=500",
                    rating=4.6
                ),
                Place(
                    name="Ласточкино гнездо",
                    description="Замок на отвесной скале мыса Ай-Тодор, один из символов Крыма и популярнейшая достопримечательность.",
                    region="crimea",
                    budget_level="medium",
                    image_url="https://images.unsplash.com/photo-1596728325487-5c4c6f8b5c3c?w=500",
                    rating=4.5
                )
            ]
            
            for place in places:
                db.session.add(place)
            
            # Добавляем готовые туры
            tours = [
                Tour(
                    name="Золотое кольцо",
                    description="7 дней: Москва, Сергиев Посад, Переславль-Залесский, Ростов Великий, Ярославль, Кострома, Иваново, Суздаль, Владимир",
                    duration_days=7,
                    price=35000,
                    places=json.dumps([1, 5])
                ),
                Tour(
                    name="Карельские каникулы",
                    description="5 дней: Петрозаводск, Кижи, Валаам, водопад Кивач, горный парк Рускеала",
                    duration_days=5,
                    price=28000,
                    places=json.dumps([3])
                ),
                Tour(
                    name="Байкальская сказка",
                    description="8 дней: Иркутск, Листвянка, Ольхон, КБЖД, бухты Малого моря",
                    duration_days=8,
                    price=55000,
                    places=json.dumps([4])
                )
            ]
            
            for tour in tours:
                db.session.add(tour)
            
            # Добавляем отзывы
            reviews = [
                Review(
                    author_name="Анна Смирнова",
                    rating=5,
                    text="Потрясающее путешествие по Золотому кольцу! Все организовано на высшем уровне. Особенно понравилось в Суздале и Ростове.",
                    place_id=5,
                    created_at=datetime.strptime("2024-07-15", "%Y-%m-%d")
                ),
                Review(
                    author_name="Дмитрий Волков",
                    rating=4,
                    text="Карелия впечатлила своей суровой красотой. Кижи и Рускеала - must see!",
                    place_id=3,
                    created_at=datetime.strptime("2024-06-03", "%Y-%m-%d")
                ),
                Review(
                    author_name="Елена Кузнецова",
                    rating=5,
                    text="Байкал превзошел все ожидания! Очень удобный планировщик, все даты и места под рукой.",
                    place_id=4,
                    created_at=datetime.strptime("2024-05-22", "%Y-%m-%d")
                )
            ]
            
            for review in reviews:
                db.session.add(review)
            
            db.session.commit()
            print("Тестовые данные созданы успешно!")

# API МАРШРУТЫ (бэкенд)

@app.route('/api/places', methods=['GET'])
def get_places():
    region = request.args.get('region', 'all')
    budget = request.args.get('budget', 'all')
    
    query = Place.query
    
    if region != 'all':
        query = query.filter_by(region=region)
    if budget != 'all':
        query = query.filter_by(budget_level=budget)
    
    places = query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'region': p.region,
        'budget_level': p.budget_level,
        'image_url': p.image_url,
        'rating': p.rating
    } for p in places])

@app.route('/api/places/<int:place_id>', methods=['GET'])
def get_place(place_id):
    place = Place.query.get_or_404(place_id)
    return jsonify({
        'id': place.id,
        'name': place.name,
        'description': place.description,
        'region': place.region,
        'budget_level': place.budget_level,
        'image_url': place.image_url,
        'rating': place.rating
    })

@app.route('/api/trips', methods=['POST'])
def create_trip():
    data = request.json
    trip = Trip(
        name=data['name'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        user_id=1  # Временный user_id
    )
    db.session.add(trip)
    db.session.commit()
    return jsonify({'id': trip.id, 'message': 'Trip created'})

@app.route('/api/trips/<int:trip_id>/places', methods=['POST'])
def add_place_to_trip(trip_id):
    data = request.json
    trip_place = TripPlace(
        trip_id=trip_id,
        place_id=data['place_id'],
        day_number=data['day_number'],
        notes=data.get('notes', '')
    )
    db.session.add(trip_place)
    db.session.commit()
    return jsonify({'message': 'Place added to trip'})

@app.route('/api/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    trip_places = TripPlace.query.filter_by(trip_id=trip_id).all()
    
    places_data = []
    for tp in trip_places:
        place = Place.query.get(tp.place_id)
        places_data.append({
            'id': place.id,
            'name': place.name,
            'day': tp.day_number,
            'notes': tp.notes
        })
    
    return jsonify({
        'id': trip.id,
        'name': trip.name,
        'start_date': trip.start_date,
        'end_date': trip.end_date,
        'places': places_data
    })

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).limit(10).all()
    return jsonify([{
        'id': r.id,
        'author_name': r.author_name,
        'rating': r.rating,
        'text': r.text,
        'created_at': r.created_at.strftime('%d.%m.%Y')
    } for r in reviews])

@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.json
    review = Review(
        author_name=data['author_name'],
        rating=data['rating'],
        text=data['text']
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({'message': 'Review added'})

@app.route('/api/tours', methods=['GET'])
def get_tours():
    tours = Tour.query.all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'description': t.description,
        'duration_days': t.duration_days,
        'price': t.price
    } for t in tours])

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Запуск инициализации базы данных
init_database()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
