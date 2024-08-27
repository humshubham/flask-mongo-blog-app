from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from config import Config
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.exceptions import BadRequest

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
mongo = PyMongo(app)

class User:
    """Represents a user in the system."""

    collection = mongo.db.users

    def __init__(self, username, email, password):
        """
        Initialize a new User instance.

        Args:
            username (str): The username of the user.
            email (str): The email of the user.
            password (str): The plaintext password of the user.
        """
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def save(self):
        """Save the user instance to the database."""
        self.collection.insert_one(self.to_dict())

    @classmethod
    def find_by_username(cls, username):
        """
        Find a user by their username.

        Args:
            username (str): The username to search for.

        Returns:
            dict or None: The user document if found, else None.
        """
        return cls.collection.find_one({'username': username})

    @classmethod
    def find_by_email(cls, email):
        """
        Find a user by their email.

        Args:
            email (str): The email to search for.

        Returns:
            dict or None: The user document if found, else None.
        """
        return cls.collection.find_one({'email': email})

    def to_dict(self):
        """
        Convert the User instance to a dictionary.

        Returns:
            dict: A dictionary representation of the User instance.
        """
        return {
            'username': self.username,
            'email': self.email,
            'password': self.password
        }

class Blog:
    """Represents a blog post in the system."""

    collection = mongo.db.blogs

    def __init__(self, title, content, author, timestamp, _id=None):
        """
        Initialize a new Blog instance.

        Args:
            title (str): The title of the blog post.
            content (str): The content of the blog post.
            author (str): The author of the blog post.
            timestamp (datetime): The timestamp when the blog was created.
            _id (str, optional): The unique identifier of the blog post. Defaults to None.
        """
        self.title = title
        self.content = content
        self.author = author
        self.timestamp = timestamp
        self._id = ObjectId(_id) if _id else None

    def save(self):
        """Save the blog instance to the database."""
        if self._id is None:
            result = self.collection.insert_one(self.to_dict(exclude_id=True))
            self._id = result.inserted_id
        else:
            self.update()

    @classmethod
    def find_all(cls):
        """
        Retrieve all blog posts from the database.

        Returns:
            list: A list of Blog instances.
        """
        documents = cls.collection.find()
        return [Blog(**document) for document in documents]

    @classmethod
    def find_by_id(cls, blog_id):
        """
        Find a blog post by its ID.

        Args:
            blog_id (str): The ID of the blog post.

        Returns:
            Blog or None: The Blog instance if found, else None.
        """
        try:
            document = cls.collection.find_one({'_id': ObjectId(blog_id)})
        except Exception as e:
            raise BadRequest(f"Invalid blog ID format: {e}")
        if document:
            return Blog(**document)
        return None

    def update(self):
        """Update the blog post in the database."""
        update_data = self.to_dict()
        update_data.pop('_id', None)  # Exclude '_id' from the update operation
        self.collection.update_one({'_id': self._id}, {'$set': update_data})

    def delete(self):
        """Delete the blog post from the database."""
        self.collection.delete_one({'_id': self._id})

    def to_dict(self, exclude_id=False):
        """
        Convert the Blog instance to a dictionary.

        Args:
            exclude_id (bool): Whether to exclude the '_id' field.

        Returns:
            dict: A dictionary representation of the Blog instance.
        """
        blog_dict = {
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'timestamp': self.timestamp
        }
        if not exclude_id:
            blog_dict['_id'] = str(self._id)
        return blog_dict

@app.route('/', methods=['GET'])
def hello_world():
    """
    Health check route to confirm the API server is running.

    Returns:
        Response: JSON response with a success message.
    """
    return jsonify({'message': 'API server running successfully'})

@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user.

    Request Body:
        - username (str): The username of the new user.
        - email (str): The email of the new user.
        - password (str): The plaintext password of the new user.

    Returns:
        Response: JSON response with a success message and JWT token, or an error message.
    """
    data = request.get_json()

    # Validate input
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    username = data['username']
    email = data['email']
    password = data['password']

    if not (username and email and password):
        return jsonify({'message': 'All fields must be non-empty'}), 400

    # Check if user already exists
    existing_user = User.find_by_username(username) or User.find_by_email(email)
    if existing_user:
        return jsonify({'message': 'User already exists'}), 400

    # Create new user
    user = User(username, email, password)
    user.save()

    # Generate JWT token
    access_token = create_access_token(identity=user.username)

    return jsonify({'message': 'User registered successfully', 'access_token': access_token})

@app.route('/login', methods=['POST'])
def login():
    """
    Log in a user and generate a JWT token.

    Request Body:
        - username (str): The username of the user.
        - password (str): The plaintext password of the user.

    Returns:
        Response: JSON response with a success message and JWT token, or an error message.
    """
    data = request.get_json()

    # Validate input
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    username = data['username']
    password = data['password']

    if not (username and password):
        return jsonify({'message': 'Both username and password must be provided'}), 400

    user = User.find_by_username(username)
    if user and bcrypt.check_password_hash(user['password'], password):
        access_token = create_access_token(identity=user['username'])
        return jsonify({'message': 'Login successful', 'access_token': access_token})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/blogs', methods=['GET'])
@jwt_required()
def get_blogs():
    """
    Retrieve all blog posts.

    Returns:
        Response: JSON response with a list of blog posts.
    """
    blogs = Blog.find_all()
    return jsonify([blog.to_dict() for blog in blogs])

@app.route('/blogs/<string:id>', methods=['GET'])
@jwt_required()
def get_blog(id):
    """
    Retrieve a specific blog post by its ID.

    Args:
        id (str): The ID of the blog post.

    Returns:
        Response: JSON response with the blog post details, or an error message if not found.
    """
    if not ObjectId.is_valid(id):
        return jsonify({'message': 'Invalid blog ID format'}), 400

    blog = Blog.find_by_id(id)
    if blog:
        return jsonify(blog.to_dict())
    else:
        return jsonify({'message': 'Blog not found'}), 404

@app.route('/blogs', methods=['POST'])
@jwt_required()
def create_blog():
    """
    Create a new blog post.

    Request Body:
        - title (str): The title of the blog post.
        - content (str): The content of the blog post.

    Returns:
        Response: JSON response with a success message.
    """
    data = request.get_json()

    # Validate input
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    title = data['title']
    content = data['content']

    if not (title and content):
        return jsonify({'message': 'Both title and content must be provided'}), 400

    # Create new blog post
    blog = Blog(
        title=title,
        content=content,
        author=get_jwt_identity(),
        timestamp=datetime.now()
    )
    blog.save()
    return jsonify({'message': 'Blog created successfully'}), 201

@app.route('/blogs/<string:id>', methods=['PUT'])
@jwt_required()
def update_blog(id):
    """
    Update an existing blog post.

    Args:
        id (str): The ID of the blog post to update.

    Request Body:
        - title (str): The new title of the blog post.
        - content (str): The new content of the blog post.

    Returns:
        Response: JSON response with a success message, or an error message if not found.
    """
    if not ObjectId.is_valid(id):
        return jsonify({'message': 'Invalid blog ID format'}), 400

    blog = Blog.find_by_id(id)
    if blog:
        data = request.get_json()

        # Validate input
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'message': 'Missing required fields'}), 400
        
        title = data['title']
        content = data['content']

        if not (title and content):
            return jsonify({'message': 'Both title and content must be provided'}), 400

        blog.title = title
        blog.content = content
        blog.update()
        return jsonify({'message': 'Blog updated successfully'})
    else:
        return jsonify({'message': 'Blog not found'}), 404

@app.route('/blogs/<string:id>', methods=['DELETE'])
@jwt_required()
def delete_blog(id):
    """
    Delete a blog post.

    Args:
        id (str): The ID of the blog post to delete.

    Returns:
        Response: JSON response with a success message, or an error message if not found.
    """
    if not ObjectId.is_valid(id):
        return jsonify({'message': 'Invalid blog ID format'}), 400

    blog = Blog.find_by_id(id)
    if blog:
        blog.delete()
        return jsonify({'message': 'Blog deleted successfully'})
    else:
        return jsonify({'message': 'Blog not found'}), 404

if __name__ == '__main__':
    app.run()
