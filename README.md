# Blog API Project

This project is a RESTful API for a blog application built using Flask, MongoDB, and JWT authentication. It supports basic CRUD operations for blog posts, user registration, and authentication.

## Table of Contents
- [Blog API Project](#blog-api-project)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Application](#running-the-application)
  - [Running Unit Tests](#running-unit-tests)
  - [API Endpoints](#api-endpoints)

## Prerequisites

Ensure you have the following software installed on your machine:

- **Python 3.10+**: Download from [python.org](https://www.python.org/downloads/)
- **MongoDB**: Download and install from [mongodb.com](https://www.mongodb.com/try/download/community)

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/humshubham/flask-mongo-blog-app.git
    cd blog-app
    ```

2. **Create a virtual environment**:

    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment**:

    - On Windows:

        ```bash
        venv\Scripts\activate
        ```

    - On macOS/Linux:

        ```bash
        source venv/bin/activate
        ```

4. **Install the required Python packages**:

    ```bash
    pip install -r requirements.txt
    ```

5. **Install MongoDB**:

    Follow the installation instructions on the [MongoDB website](https://docs.mongodb.com/manual/installation/) according to your operating system.

6. **Start the MongoDB server**:

    - On Windows:

        ```bash
        "C:\Program Files\MongoDB\Server\<version>\bin\mongod.exe"
        ```

    - On macOS/Linux:

        ```bash
        mongod --config /usr/local/etc/mongod.conf
        ```

## Configuration

1. **Create a `.env` file** in the root directory of the project to store your environment variables:

    ```bash
    touch .env
    ```

2. **Add the following environment variables** to your `.env` file:

    ```env
    SECRET_KEY=your-secret-key
    MONGODB_URI=mongodb://localhost:27017/blogs_db
    ```

3. **Configuration file**:
    - The `Config` class in `config.py` handles the configuration for Flask and the MongoDB connection. Modify it if necessary.

## Running the Application

1. **Start the Flask application**:

    ```bash
    flask run
    ```

    The application should now be running at `http://127.0.0.1:5000/`.

2. **Access the API**:
    - Test the API using tools like [Postman](https://www.postman.com/) or [cURL](https://curl.se/).

## Running Unit Tests

To ensure your application works as expected, unit tests are included. Follow these steps to run the tests:

1. **Ensure your MongoDB server is running**.

2. **Run the tests using `unittest`**:

    ```bash
    pytest test_api.py
    ```

    The `tests_api` file contains all the test cases, and running the above command will execute them.

## API Endpoints

The following are the primary endpoints of the API:

- **User Registration**: `POST /register`
- **User Login**: `POST /login`
- **Get All Blogs**: `GET /blogs`
- **Get Blog by ID**: `GET /blogs/<id>`
- **Create Blog**: `POST /blogs`
- **Update Blog**: `PUT /blogs/<id>`
- **Delete Blog**: `DELETE /blogs/<id>`
