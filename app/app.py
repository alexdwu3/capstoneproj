from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
from app.models import setup_db, Actor, Movie, db
from app.auth import AuthError, requires_auth
from datetime import datetime

# Ensure a single instance of SQLAlchemy is created and used
migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__)
    
    app.config.from_object('config.Config')

    setup_db(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate with the app and db

    CORS(app)

    @app.before_request
    def log_request():
        print(f"🔍 Received request: {request.method} {request.path}")
        print(f"🔍 Headers: {request.headers}")

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS')
        return response

    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def get_actors(payload):
        try:
            actors = Actor.query.all()
            return jsonify({
                'success': True,
                'actors': [actor.format() for actor in actors]
            }), 200
        except Exception as e:
            abort(500)

    @app.route('/movies', methods=['GET'])
    @requires_auth('get:movies')
    def get_movies(payload):
        print("✅ Entered get_movies() route")  # Debugging

        try:
            movies = Movie.query.all()
            print(f"🔍 Retrieved {len(movies)} movies from database")

            return jsonify({
                'success': True,
                'movies': [movie.format() for movie in movies]
            }), 200

        except Exception as e:
            abort(500)

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def create_actor(payload):
        body = request.get_json()
        
        if not ('name' in body and 'age' in body and 'gender' in body):
            abort(400)
            
        try:
            actor = Actor(
                name=body['name'],
                age=body['age'],
                gender=body['gender']
            )
            actor.insert()
            
            return jsonify({
                'success': True,
                'created': actor.id
            }), 201
        except Exception as e:
            abort(422)

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def create_movie(payload):
        body = request.get_json()
        
        if not ('title' in body and 'release_date' in body):
            abort(400)
            
        try:
            movie = Movie(
                title=body['title'],
                release_date=datetime.fromisoformat(body['release_date'])
            )
            movie.insert()
            
            return jsonify({
                'success': True,
                'created': movie.id
            }), 201
        except Exception as e:
            print(f"Database error: {e}")  # Debugging print
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def update_actor(payload, actor_id):
        actor = Actor.query.get(actor_id)
        if not actor:
            abort(404)
            
        body = request.get_json()
        
        try:
            if 'name' in body:
                actor.name = body['name']
            if 'age' in body:
                actor.age = body['age']
            if 'gender' in body:
                actor.gender = body['gender']
            
            print(f"Updating actor: {actor}")  # Debugging
            db.session.add(actor)  # Ensure the actor object is attached to the session
            db.session.commit()  # Explicitly commit changes
            print(f"Actor updated: {actor}")  # Debugging
            
            formatted_actor = actor.format()
            print(f"Formatted actor: {formatted_actor}")  # Debugging
            
            return jsonify({
                'success': True,
                'actor': formatted_actor
            }), 200
        except Exception as e:
            print(f"🚨 Error updating actor: {str(e)}")  # Debugging
            db.session.rollback()  # Ensure rollback on failure
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def update_movie(payload, movie_id):
        movie = Movie.query.get(movie_id)
        if not movie:
            abort(404)

        body = request.get_json()
        
        try:
            # Ensure the movie object is attached to the session
            movie = db.session.merge(movie)  
            
            if 'title' in body:
                movie.title = body['title']
            if 'release_date' in body:
                movie.release_date = datetime.fromisoformat(body['release_date'])

            db.session.commit()  # Explicitly commit changes
            
            return jsonify({
                'success': True,
                'movie': movie.format()
            }), 200
        except Exception as e:
            print(f"🚨 Error updating movie: {str(e)}")  # Debugging
            db.session.rollback()  # Ensure rollback on failure
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(payload, actor_id):
        actor = Actor.query.get(actor_id)
        if not actor:
            abort(404)
            
        try:
            actor.delete()
            return jsonify({
                'success': True,
                'deleted': actor_id
            }), 200
        except Exception as e:
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(payload, movie_id):
        movie = Movie.query.get(movie_id)
        if not movie:
            abort(404)
            
        try:
            movie.delete()
            return jsonify({
                'success': True,
                'deleted': movie_id
            }), 200
        except Exception as e:
            abort(422)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable entity"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error['description']
        }), error.status_code

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)