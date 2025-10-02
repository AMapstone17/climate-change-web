"""
Contains testing config for Pytest. Includes fixtures for testing.
"""

import os
from datetime import datetime

import pytest

from flaskapp import create_app, User
from flaskapp.extensions import db
from flaskapp.models.blog_post import BlogPost
from flaskapp.models.leaderboard_entry import LeaderboardEntry
from flaskapp.models.quiz_question import QuizQuestion


class TestConfig:
    """Contains configuration for testing a Flask app."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'SECRET_KEY'
    WTF_CSRF_ENABLED = False
    RECAPTCHA_PUBLIC_KEY = os.getenv('FLASK_RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('FLASK_RECAPTCHA_PRIVATE_KEY')
    BYPASS_2FA = False
    LOGIN_DISABLED = False


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app(TestConfig)
    testing_client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # testing happens here

    ctx.pop()


@pytest.fixture(scope='function')
def init_empty_database(test_client):
    db.create_all()

    yield db  # testing happens here

    # db.session.rollback()
    db.session.remove()
    db.drop_all()


@pytest.fixture(scope='function')
def init_filled_database(test_client):
    db.create_all()

    admin_user = User(
        username='admin1',
        password='Admin1!',
        firstname='Admin',
        lastname='User',
        date_of_birth=datetime(1990, 1, 1),
        email='admin@user.com',
        role='admin'
    )
    bob = User(
        username='bob123',
        firstname='Bob',
        lastname='Smith',
        date_of_birth=datetime(1980, 1, 1),
        password='Password123!',
        email='bobsmith123@gmail.com',
        role='user'
    )
    amelia = User(
        username='amelia123',
        firstname='Amelia',
        lastname='Jones',
        date_of_birth=datetime(1990, 1, 1),
        password='Amelia123@',
        email='ameliajones123@gmail.com',
        role='user'
    )



    db.session.add(admin_user)
    db.session.add(bob)
    db.session.add(amelia)

    admin_user = User.query.filter_by(username='admin1').first()
    bob = User.query.filter_by(username='bob123').first()
    amelia = User.query.filter_by(username='amelia123').first()

    admin_leaderboard_entry = LeaderboardEntry(admin_user.id, 0, 0)
    bob_leaderboard_entry = LeaderboardEntry(bob.id, 0, 0)
    amelia_leaderboard_entry = LeaderboardEntry(amelia.id, 0, 0)

    db.session.add(admin_leaderboard_entry)
    db.session.add(bob_leaderboard_entry)
    db.session.add(amelia_leaderboard_entry)

    example_question = QuizQuestion(
        question='What is the capital of France?',
        answer='Paris',
        option1='London',
        option2='Berlin',
        option3='Madrid'
    )

    example_question2 = QuizQuestion(
        question='Example 2nd question',
        answer='Example 2nd answer',
        option1='option 1',
        option2='option 2',
        option3='option 3'
    )

    admin_user = User.query.filter_by(username='admin1').first()

    example_post = BlogPost(
        title='Test Post',
        content='This is a test post.',
        author_id=admin_user.id
    )

    db.session.add(example_question)
    db.session.add(example_question2)
    quiz_question_count = QuizQuestion.query.count()
    print(f"Number of quiz questions in the database: {quiz_question_count}")
    db.session.add(example_post)

    yield db

    db.session.remove()
    db.drop_all()
