# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

def setup_db(app):
    """Binds a flask application and a SQLAlchemy service"""
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost:5432/castingagency"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

class Movie(db.Model):
    """Movie Model representing movies in the casting agency"""
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    release_date = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        """Inserts a new movie into the database"""
        try:
            db.session.add(self)
            db.session.commit()
            return self.id
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()

    def update(self):
        """Updates an existing movie in the database"""
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()

    def delete(self):
        """Deletes a movie from the database"""
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()

    def format(self):
        """Returns a dictionary representation of the Movie model"""
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date.isoformat()
        }

class Actor(db.Model):
    """Actor Model representing actors in the casting agency"""
    __tablename__ = 'actors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    def insert(self):
        """Inserts a new actor into the database"""
        try:
            db.session.add(self)
            db.session.commit()
            return self.id
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()

    def update(self):
        """Updates an existing actor in the database"""
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()

    def delete(self):
        """Deletes an actor from the database"""
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()

    def format(self):
        """Returns a dictionary representation of the Actor model"""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender
        }


