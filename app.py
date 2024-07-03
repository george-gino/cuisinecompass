from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost/restaurants_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Replace with your Google API key
GOOGLE_PLACES_API_KEY = 'AIzaSyCVBJPRfiZgGAYihMVgdKwiXyX1RAeaD2I'

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    place_id = db.Column(db.String(100), nullable=False, unique=True)
    address = db.Column(db.String(200), nullable=False)
    cuisine = db.Column(db.String(50), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_restaurant', methods=['POST'])
def add_restaurant():
    data = request.json
    if Restaurant.query.filter_by(place_id=data['place_id']).first():
        return jsonify({"status": "error", "message": "Restaurant already exists."}), 409

    new_restaurant = Restaurant(
        name=data['name'],
        place_id=data['place_id'],
        address=data['address'],
        cuisine=data['cuisine']
    )
    db.session.add(new_restaurant)
    db.session.commit()
    return jsonify({"status": "success", "message": "Restaurant added successfully!"})

@app.route('/get_restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    results = [
        {
            "name": restaurant.name,
            "place_id": restaurant.place_id,
            "address": restaurant.address,
            "cuisine": restaurant.cuisine
        } for restaurant in restaurants]

    return jsonify(results)

@app.route('/view_restaurants')
def view_restaurants():
    return render_template('view_restaurants.html')

@app.route('/clear_restaurants', methods=['DELETE'])
def clear_restaurants():
    try:
        num_rows_deleted = db.session.query(Restaurant).delete()
        db.session.commit()
        return jsonify({"status": "success", "message": f"Deleted {num_rows_deleted} restaurants."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/search_place', methods=['GET'])
def search_place():
    query = request.args.get('query')
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={GOOGLE_PLACES_API_KEY}"
    response = requests.get(url)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)



















