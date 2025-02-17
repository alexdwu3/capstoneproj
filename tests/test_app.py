import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from app.models import setup_db, Actor, Movie
from datetime import datetime

class CastingAgencyTestCase(unittest.TestCase):
    """This class represents the casting agency test case"""

    def setUp(self):
        """Define test variables and initialize app"""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = os.environ.get('DATABASE_URL')
        setup_db(self.app)

        # Test data
        self.new_movie = {
            'title': 'Test Movie',
            'release_date': '2024-01-01T00:00:00'
        }
        self.new_actor = {
            'name': 'Test Actor',
            'age': 30,
            'gender': 'Male'
        }

        # Auth headers for different roles
        self.assistant_auth_header = {
            'Authorization': f'Bearer {os.environ.get("CASTING_ASSISTANT_TOKEN")}'
        }
        self.director_auth_header = {
            'Authorization': f'Bearer {os.environ.get("CASTING_DIRECTOR_TOKEN")}'
        }
        self.producer_auth_header = {
            'Authorization': f'Bearer {os.environ.get("EXECUTIVE_PRODUCER_TOKEN")}'
        }

        # Binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    # Success behavior tests for each endpoint
    def test_get_actors_success(self):
        """Test successful GET actors"""
        res = self.client().get('/actors', headers=self.assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue('actors' in data)

    def test_get_movies_success(self):
        """Test successful GET movies"""
        res = self.client().get('/movies', headers=self.assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue('movies' in data)

    def test_create_actor_success(self):
        """Test successful POST actor"""
        res = self.client().post('/actors', 
            headers=self.director_auth_header,
            json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['created'])

    def test_create_movie_success(self):
        """Test successful POST movie"""
        res = self.client().post('/movies',
            headers=self.producer_auth_header,
            json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['created'])

    def test_update_actor_success(self):
        """Test successful PATCH actor"""
        # First create an actor
        actor_res = self.client().post('/actors',
            headers=self.director_auth_header,
            json=self.new_actor)
        actor_id = json.loads(actor_res.data)['created']

        # Then update it
        update_data = {'age': 31}
        res = self.client().patch(f'/actors/{actor_id}',
            headers=self.director_auth_header,
            json=update_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['actor']['age'], 31)

    def test_update_movie_success(self):
        """Test successful PATCH movie"""
        # First create a movie
        movie_res = self.client().post('/movies',
            headers=self.producer_auth_header,
            json=self.new_movie)
        movie_id = json.loads(movie_res.data)['created']

        # Then update it
        update_data = {'title': 'Updated Test Movie'}
        res = self.client().patch(f'/movies/{movie_id}',
            headers=self.director_auth_header,
            json=update_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['movie']['title'], 'Updated Test Movie')

    def test_delete_actor_success(self):
        """Test successful DELETE actor"""
        # First create an actor
        actor_res = self.client().post('/actors',
            headers=self.director_auth_header,
            json=self.new_actor)
        actor_id = json.loads(actor_res.data)['created']

        # Then delete it
        res = self.client().delete(f'/actors/{actor_id}',
            headers=self.director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], actor_id)

    def test_delete_movie_success(self):
        """Test successful DELETE movie"""
        # First create a movie
        movie_res = self.client().post('/movies',
            headers=self.producer_auth_header,
            json=self.new_movie)
        movie_id = json.loads(movie_res.data)['created']

        # Then delete it
        res = self.client().delete(f'/movies/{movie_id}',
            headers=self.producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], movie_id)

    # Error behavior tests for each endpoint
    def test_get_actors_error(self):
        """Test error behavior for GET actors"""
        res = self.client().get('/actors')  # No auth header
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])

    def test_get_movies_error(self):
        """Test error behavior for GET movies"""
        res = self.client().get('/movies')  # No auth header
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])

    def test_create_actor_error(self):
        """Test error behavior for POST actor"""
        # Missing required fields
        res = self.client().post('/actors',
            headers=self.director_auth_header,
            json={'name': 'Test Actor'})  # Missing age and gender
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])

    def test_create_movie_error(self):
        """Test error behavior for POST movie"""
        # Missing required fields
        res = self.client().post('/movies',
            headers=self.producer_auth_header,
            json={'title': 'Test Movie'})  # Missing release_date
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])

    def test_update_actor_error(self):
        """Test error behavior for PATCH actor"""
        # Non-existent actor ID
        res = self.client().patch('/actors/9999',
            headers=self.director_auth_header,
            json={'age': 31})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_update_movie_error(self):
        """Test error behavior for PATCH movie"""
        # Non-existent movie ID
        res = self.client().patch('/movies/9999',
            headers=self.director_auth_header,
            json={'title': 'Updated Test Movie'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_actor_error(self):
        """Test error behavior for DELETE actor"""
        # Non-existent actor ID
        res = self.client().delete('/actors/9999',
            headers=self.director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_movie_error(self):
        """Test error behavior for DELETE movie"""
        # Non-existent movie ID
        res = self.client().delete('/movies/9999',
            headers=self.producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    # RBAC tests for Casting Assistant
    def test_casting_assistant_get_actors(self):
        """Test Casting Assistant can get actors"""
        res = self.client().get('/actors', headers=self.assistant_auth_header)
        self.assertEqual(res.status_code, 200)

    def test_casting_assistant_get_movies(self):
        """Test Casting Assistant can get movies"""
        res = self.client().get('/movies', headers=self.assistant_auth_header)
        self.assertEqual(res.status_code, 200)

    def test_casting_assistant_create_actor_forbidden(self):
        """Test Casting Assistant cannot create actor"""
        res = self.client().post('/actors',
            headers=self.assistant_auth_header,
            json=self.new_actor)
        self.assertEqual(res.status_code, 403)

    def test_casting_assistant_create_movie_forbidden(self):
        """Test Casting Assistant cannot create movie"""
        res = self.client().post('/movies',
            headers=self.assistant_auth_header,
            json=self.new_movie)
        self.assertEqual(res.status_code, 403)

    # RBAC tests for Casting Director
    def test_casting_director_create_actor(self):
        """Test Casting Director can create actor"""
        res = self.client().post('/actors',
            headers=self.director_auth_header,
            json=self.new_actor)
        self.assertEqual(res.status_code, 201)

    def test_casting_director_update_movie(self):
        """Test Casting Director can update movie"""
        # First create a movie as producer
        movie_res = self.client().post('/movies',
            headers=self.producer_auth_header,
            json=self.new_movie)
        movie_id = json.loads(movie_res.data)['created']

        # Then update it as director
        res = self.client().patch(f'/movies/{movie_id}',
            headers=self.director_auth_header,
            json={'title': 'Updated Movie'})
        self.assertEqual(res.status_code, 200)

    def test_casting_director_create_movie_forbidden(self):
        """Test Casting Director cannot create movie"""
        res = self.client().post('/movies',
            headers=self.director_auth_header,
            json=self.new_movie)
        self.assertEqual(res.status_code, 403)

    def test_casting_director_delete_movie_forbidden(self):
        """Test Casting Director cannot delete movie"""
        # First create a movie as producer
        movie_res = self.client().post('/movies',
            headers=self.producer_auth_header,
            json=self.new_movie)
        movie_id = json.loads(movie_res.data)['created']

        # Try to delete it as director
        res = self.client().delete(f'/movies/{movie_id}',
            headers=self.director_auth_header)
        self.assertEqual(res.status_code, 403)

    # RBAC tests for Executive Producer
    def test_executive_producer_create_movie(self):
        """Test Executive Producer can create movie"""
        res = self.client().post('/movies',
            headers=self.producer_auth_header,
            json=self.new_movie)
        self.assertEqual(res.status_code, 201)

    def test_executive_producer_delete_movie(self):
        """Test Executive Producer can delete movie"""
        # First create a movie
        movie_res = self.client().post('/movies',
            headers=self.producer_auth_header,
            json=self.new_movie)
        movie_id = json.loads(movie_res.data)['created']

        # Then delete it
        res = self.client().delete(f'/movies/{movie_id}',
            headers=self.producer_auth_header)
        self.assertEqual(res.status_code, 200)

    def test_executive_producer_all_actor_operations(self):
        """Test Executive Producer has full actor permissions"""
        # Create actor
        actor_res = self.client().post('/actors',
            headers=self.producer_auth_header,
            json=self.new_actor)
        self.assertEqual(actor_res.status_code, 201)
        
        actor_id = json.loads(actor_res.data)['created']

        # Update actor
        update_res = self.client().patch(f'/actors/{actor_id}',
            headers=self.producer_auth_header,
            json={'age': 31})
        self.assertEqual(update_res.status_code, 200)

        # Delete actor
        delete_res = self.client().delete(f'/actors/{actor_id}',
            headers=self.producer_auth_header)
        self.assertEqual(delete_res.status_code, 200)

if __name__ == "__main__":
    unittest.main()