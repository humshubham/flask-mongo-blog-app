import unittest
from app import app, mongo
from flask_jwt_extended import create_access_token

class TestBlogAPIs(unittest.TestCase):

    def setUp(self):
        """Setup the test client and initialize the database."""
        self.test_client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Clear the database before each test
        mongo.db.users.delete_many({})
        mongo.db.blogs.delete_many({})

    def tearDown(self):
        """Clean up after each test."""
        mongo.db.users.delete_many({})
        mongo.db.blogs.delete_many({})
        self.app_context.pop()

    def generate_token(self, username, email, password):
        """Helper function to register a user and generate JWT token."""
        user_data = {
            "username": username,
            "email": email,
            "password": password
        }

        # Register a new user
        self.test_client.post('/register', json=user_data)

        # Generate JWT token
        token = create_access_token(identity=user_data['username'])
        return token

    def test_register_user(self):
        response = self.test_client.post('/register', json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['message'], 'User registered successfully')

    def test_login_user(self):
        self.test_client.post('/register', json={
            "username": "loginuser",
            "email": "loginuser@example.com",
            "password": "loginpassword"
        })
        response = self.test_client.post('/login', json={
            "username": "loginuser",
            "password": "loginpassword"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.get_json())

    def test_login_invalid_credentials(self):
        response = self.test_client.post('/login', json={
            "username": "wronguser",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()['message'], 'Invalid credentials')

    def test_create_blog(self):
        token = self.generate_token("bloguser", "bloguser@example.com", "blogpassword")
        headers = {'Authorization': f'Bearer {token}'}
        response = self.test_client.post('/blogs', json={
            "title": "Test Blog",
            "content": "This is a test blog content."
        }, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()['message'], 'Blog created successfully')

    def test_get_blogs(self):
        token = self.generate_token("bloguser", "bloguser@example.com", "blogpassword")
        headers = {'Authorization': f'Bearer {token}'}
        self.test_client.post('/blogs', json={
            "title": "Test Blog",
            "content": "This is a test blog content."
        }, headers=headers)

        response = self.test_client.get('/blogs', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    def test_get_blog_by_id(self):
        token = self.generate_token("bloguser", "bloguser@example.com", "blogpassword")
        headers = {'Authorization': f'Bearer {token}'}
        self.test_client.post('/blogs', json={
            "title": "Test Blog",
            "content": "This is a test blog content."
        }, headers=headers)

        blog_id = str(mongo.db.blogs.find_one()["_id"])
        response = self.test_client.get(f'/blogs/{blog_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['title'], 'Test Blog')

    def test_update_blog(self):
        token = self.generate_token("bloguser", "bloguser@example.com", "blogpassword")
        headers = {'Authorization': f'Bearer {token}'}
        self.test_client.post('/blogs', json={
            "title": "Old Title",
            "content": "Old content."
        }, headers=headers)

        blog_id = str(mongo.db.blogs.find_one()["_id"])
        response = self.test_client.put(f'/blogs/{blog_id}', json={
            "title": "New Title",
            "content": "New content."
        }, headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['message'], 'Blog updated successfully')

    def test_delete_blog(self):
        token = self.generate_token("bloguser", "bloguser@example.com", "blogpassword")
        headers = {'Authorization': f'Bearer {token}'}
        self.test_client.post('/blogs', json={
            "title": "Delete Me",
            "content": "Delete this content."
        }, headers=headers)

        blog_id = str(mongo.db.blogs.find_one()["_id"])
        response = self.test_client.delete(f'/blogs/{blog_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['message'], 'Blog deleted successfully')

    def test_invalid_blog_id(self):
        token = self.generate_token("bloguser", "bloguser@example.com", "blogpassword")
        headers = {'Authorization': f'Bearer {token}'}
        response = self.test_client.get('/blogs/invalid_id', headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'], 'Invalid blog ID format')

if __name__ == '__main__':
    unittest.main()
