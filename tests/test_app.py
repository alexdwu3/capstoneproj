import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app.app import create_app
from app.models import setup_db, Actor, Movie
from datetime import datetime
from app.models import db  # ✅ Import existing db instance
from unittest.mock import patch
from app.auth import verify_decode_jwt


class CastingAgencyTestCase(unittest.TestCase):
    """This class represents the casting agency test case"""

    def setUp(self):
        """Define test variables and initialize app"""
        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app)  # ✅ Correctly initializes DB

        # Test data
        self.new_movie = {'title': 'Test Movie', 'release_date': '2024-01-01T00:00:00'}
        self.new_actor = {'name': 'Test Actor', 'age': 30, 'gender': 'Male'}

        # Mocked permissions
        self.assistant_permissions = {"sub": "assistant", "permissions": ["get:actors", "get:movies"]}
        self.director_permissions = {"sub": "director", "permissions": [
            "get:actors", "post:actors", "patch:actors", "delete:actors",
            "get:movies", "patch:movies"
        ]}
        self.producer_permissions = {"sub": "producer", "permissions": [
            "get:actors", "post:actors", "patch:actors", "delete:actors",
            "get:movies", "post:movies", "patch:movies", "delete:movies"
        ]}

        # Define authorization headers for different roles
        self.assistant_auth_header = {
            'Authorization': 'Bearer assistant_token'
        }
        self.director_auth_header = {
            'Authorization': 'Bearer director_token'
        }
        self.producer_auth_header = {
            'Authorization': 'Bearer producer_token'
        }

    def tearDown(self):
        """Executed after each test"""
        pass

    def mock_verify_decode_jwt(self, token):
        """Mock function to return different permissions based on the token"""
        if token == 'assistant_token':
            return self.assistant_permissions
        elif token == 'director_token':
            return self.director_permissions
        elif token == 'producer_token':
            return self.producer_permissions
        else:
            return {}

    # Success behavior tests for each endpoint
    def test_get_actors_success(self):
        """Test successful GET actors"""
        with patch('app.auth.verify_decode_jwt', return_value=self.assistant_permissions):
            res = self.client().get('/actors', headers=self.assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue('actors' in data)

    def test_get_movies_success(self):
        """Test successful GET movies"""
        with patch('app.auth.verify_decode_jwt', return_value=self.assistant_permissions):
            res = self.client().get('/movies', headers=self.assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue('movies' in data)

    def test_create_actor_success(self):
        """Test successful POST actor"""
        with patch('app.auth.verify_decode_jwt', return_value=self.director_permissions):
            res = self.client().post('/actors', headers=self.director_auth_header, json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['created'])

    def test_create_movie_success(self):
        """Test successful POST movie"""
        with patch('app.auth.verify_decode_jwt', return_value=self.producer_permissions):
            res = self.client().post('/movies', headers=self.producer_auth_header, json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['created'])

    def test_update_actor_success(self):
        """Test successful PATCH actor"""
        with patch('app.auth.verify_decode_jwt', return_value=self.director_permissions):
            actor_res = self.client().post('/actors', headers=self.director_auth_header, json=self.new_actor)
            actor_id = json.loads(actor_res.data)['created']

        update_data = {'age': 31}
        with patch('app.auth.verify_decode_jwt', return_value=self.director_permissions):
            res = self.client().patch(f'/actors/{actor_id}', headers=self.director_auth_header, json=update_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['actor']['age'], 31)

    def test_update_movie_success(self):
        """Test successful PATCH movie"""
        with patch('app.auth.verify_decode_jwt', return_value=self.producer_permissions):
            movie_res = self.client().post('/movies', headers=self.producer_auth_header, json=self.new_movie)
            movie_id = json.loads(movie_res.data)['created']

        update_data = {'title': 'Updated Test Movie'}
        with patch('app.auth.verify_decode_jwt', return_value=self.director_permissions):
            res = self.client().patch(f'/movies/{movie_id}', headers=self.director_auth_header, json=update_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['movie']['title'], 'Updated Test Movie')

    def test_delete_actor_success(self):
        """Test successful DELETE actor"""
        with patch('app.auth.verify_decode_jwt', return_value=self.director_permissions):
            actor_res = self.client().post('/actors', headers=self.director_auth_header, json=self.new_actor)
            actor_id = json.loads(actor_res.data)['created']

        with patch('app.auth.verify_decode_jwt', return_value=self.director_permissions):
            res = self.client().delete(f'/actors/{actor_id}', headers=self.director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], actor_id)

    def test_delete_movie_success(self):
        """Test successful DELETE movie"""
        with patch('app.auth.verify_decode_jwt', return_value=self.producer_permissions):
            movie_res = self.client().post('/movies', headers=self.producer_auth_header, json=self.new_movie)
            movie_id = json.loads(movie_res.data)['created']

        with patch('app.auth.verify_decode_jwt', return_value=self.producer_permissions):
            res = self.client().delete(f'/movies/{movie_id}', headers=self.producer_auth_header)
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
        with patch('app.auth.verify_decode_jwt', return_value=self.director_permissions):
            res = self.client().post('/actors', headers=self.director_auth_header, json={'name': 'Test Actor'})  # Missing age and gender
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])

    def test_create_movie_error(self):
        """Test error behavior for POST movie"""
        # Missing required fields
        with patch('app.auth.verify_decode_jwt', return_value=self.producer_permissions):
            res = self.client().post('/movies', headers=self.producer_auth_header, json={'title': 'Test Movie'})  # Missing release_date
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])

    def test_update_actor_error(self):
        """Test error behavior for PATCH actor"""
        # Non-existent actor ID
        with patch('app.auth.verify_decode_jwt', return_value=self.director_permissions):
            res = self.client().patch('/actors/9999', headers=self.director_auth_header, json={'age': 31})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_update_movie_error(self):
        """Test error behavior for PATCH movie"""
        # Non-existent movie ID
        with patch('app.auth.verify_decode_jwt', return_value=self.director_permissions):
            res = self.client().patch('/movies/9999', headers=self.director_auth_header, json={'title': 'Updated Test Movie'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_actor_error(self):
        """Test error behavior for DELETE actor"""
        # Non-existent actor ID
        with patch('app.auth.verify_decode_jwt', return_value=self.director_permissions):
            res = self.client().delete('/actors/9999', headers=self.director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_movie_error(self):
        """Test error behavior for DELETE movie"""
        # Non-existent movie ID
        with patch('app.auth.verify_decode_jwt', return_value=self.producer_permissions):
            res = self.client().delete('/movies/9999', headers=self.producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    # RBAC tests for Casting Assistant
    def test_casting_assistant_get_actors(self):
        """Test Casting Assistant can get actors"""
        with patch('app.auth.verify_decode_jwt', return_value=self.assistant_permissions):
            res = self.client().get('/actors', headers=self.assistant_auth_header)
        self.assertEqual(res.status_code, 200)

    def test_casting_assistant_get_movies(self):
        """Test Casting Assistant can get movies"""
        with patch('app.auth.verify_decode_jwt', return_value=self.assistant_permissions):
            res = self.client().get('/movies', headers=self.assistant_auth_header)
        self.assertEqual(res.status_code, 200)

    def test_casting_assistant_create_actor_forbidden(self):
        """Test Casting Assistant cannot create actor"""
        with patch('app.auth.verify_decode_jwt', return_value=self.assistant_permissions):
            res = self.client().post('/actors', headers=self.assistant_auth_header, json=self.new_actor)
        self.assertEqual(res.status_code, 403)

    def test_casting_assistant_create_movie_forbidden(self):
        """Test Casting Assistant cannot create movie"""
        with patch('app.auth.verify_decode_jwt', return_value=self.assistant_permissions):
            res = self.client().post('/movies', headers=self.assistant_auth_header, json=self.new_movie)
        self.assertEqual(res.status_code, 403)

    # RBAC tests for Casting Director
    def test_casting_director_create_actor(self):
        """Test Casting Director can create actor"""
        with patch('app.auth.verify_decode_jwt', return_value=self.director_permissions):
            res = self.client().post('/actors', headers=self.director_auth_header, json=self.new_actor)
        self.assertEqual(res.status_code, 201)

    def test_casting_director_update_movie(self):
        """Test Casting Director can update movie"""
        with patch('app.auth.verify_decode_jwt', return_value=self.producer_permissions):
            # First create a movie as producer
            movie_res = self.client().post('/movies', headers=self.producer_auth_header, json=self.new_movie)
            movie_id = json.loads(movie_res.data).get('created')

            if movie_id:
                # Then update it as director
                with patch('app.auth.verify_decode_jwt', return_value=self.director_permissions):
                    res = self.client().patch(f'/movies/{movie_id}', headers=self.director_auth_header, json={'title': 'Updated Movie'})
                self.assertEqual(res.status_code, 200)
            else:
                self.fail("Movie creation failed in test_casting_director_update_movie")

    def test_casting_director_create_movie_forbidden(self):
        """Test Casting Director cannot create movie"""
        with patch('app.auth.verify_decode_jwt', return_value=self.director_permissions):
            res = self.client().post('/movies', headers=self.director_auth_header, json=self.new_movie)
        self.assertEqual(res.status_code, 403)

    def test_casting_director_delete_movie_forbidden(self):
        """Test Casting Director cannot delete movie"""
        with patch('app.auth.verify_decode_jwt', return_value=self.producer_permissions):
            # First create a movie as producer
            movie_res = self.client().post('/movies', headers=self.producer_auth_header, json=self.new_movie)
            movie_id = json.loads(movie_res.data).get('created')

            if movie_id:
                # Try to delete it as director
                with patch('app.auth.verify_decode_jwt', return_value=self.director_permissions):
                    res = self.client().delete(f'/movies/{movie_id}', headers=self.director_auth_header)
                self.assertEqual(res.status_code, 403)
            else:
                self.fail("Movie creation failed in test_casting_director_delete_movie_forbidden")

    # RBAC tests for Executive Producer
    def test_executive_producer_create_movie(self):
        """Test Executive Producer can create movie"""
        with patch('app.auth.verify_decode_jwt', return_value=self.producer_permissions):
            res = self.client().post('/movies', headers=self.producer_auth_header, json=self.new_movie)
        self.assertEqual(res.status_code, 201)

    def test_executive_producer_delete_movie(self):
        """Test Executive Producer can delete movie"""
        with patch('app.auth.verify_decode_jwt', return_value=self.producer_permissions):
            # First create a movie
            movie_res = self.client().post('/movies', headers=self.producer_auth_header, json=self.new_movie)
            movie_id = json.loads(movie_res.data)['created']

            # Then delete it
            res = self.client().delete(f'/movies/{movie_id}', headers=self.producer_auth_header)
        self.assertEqual(res.status_code, 200)

    def test_executive_producer_all_actor_operations(self):
        """Test Executive Producer has full actor permissions"""
        with patch('app.auth.verify_decode_jwt', return_value=self.producer_permissions):
            # Create actor
            actor_res = self.client().post('/actors', headers=self.producer_auth_header, json=self.new_actor)
            self.assertEqual(actor_res.status_code, 201)
            
            actor_id = json.loads(actor_res.data)['created']

            # Update actor
            update_res = self.client().patch(f'/actors/{actor_id}', headers=self.producer_auth_header, json={'age': 31})
            self.assertEqual(update_res.status_code, 200)

            # Delete actor
            delete_res = self.client().delete(f'/actors/{actor_id}', headers=self.producer_auth_header)
            self.assertEqual(delete_res.status_code, 200)

if __name__ == "__main__":
    unittest.main()