"""
Contains database test functions, including testing database connection, creating, querying, editing, and deleting users and quiz questions.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from flaskapp.models.quiz_question import QuizQuestion
from flaskapp.models.user import User
from test.test_config import init_empty_database, test_client


class TestDatabase:

    def test_database_connection(self, test_client, init_empty_database):
        with test_client.application.app_context():
            try:
                init_empty_database.session.execute(text('SELECT 1'))
            except OperationalError:
                assert False, 'Database connection failed'
            else:
                assert True, 'Database connection successful'

    @pytest.fixture(scope='function')
    def test_create_user(self, init_empty_database):
        user = User(
            username='bob123',
            firstname='Bob',
            lastname='Smith',
            date_of_birth='1980-01-01',
            password='password123',
            email='bobsmith123@gmail.com',
            role='user'
        )
        init_empty_database.session.add(user)
        init_empty_database.session.commit()

    def test_query_user(self, init_empty_database, test_create_user):
        user = init_empty_database.session.query(User).filter_by(username='bob123').first()
        assert user.firstname == 'Bob'
        assert user.lastname == 'Smith'
        assert user.email == 'bobsmith123@gmail.com'
        assert user.password != 'password123'

    def test_edit_user(self, init_empty_database, test_create_user):
        user = init_empty_database.session.query(User).filter_by(username='bob123').first()
        user.firstname = 'Robert'
        user.lastname = 'Smyth'
        user.email = 'bobsmyth123@gmail.com'
        init_empty_database.session.commit()

        user = init_empty_database.session.query(User).filter_by(username='bob123').first()
        assert user.firstname == 'Robert'
        assert user.lastname == 'Smyth'
        assert user.email == 'bobsmyth123@gmail.com'

    def test_delete_user(self, init_empty_database, test_create_user):
        user = init_empty_database.session.query(User).filter_by(username='bob123').first()
        assert user is not None
        init_empty_database.session.delete(user)
        init_empty_database.session.commit()
        user = init_empty_database.session.query(User).filter_by(username='bob123').first()
        assert user is None

    @pytest.fixture(scope='function')
    def test_create_quiz_question(self, init_empty_database):
        question = QuizQuestion(
            question='Question 1',
            answer='Answer 1',
            option1='Incorrect 1',
            option2='Incorrect 2',
            option3='Incorrect 3'
        )
        init_empty_database.session.add(question)
        init_empty_database.session.commit()

    def test_query_quiz_question(self, init_empty_database, test_create_quiz_question):
        question = init_empty_database.session.query(QuizQuestion).filter_by(question='Question 1').first()
        assert question.answer == 'Answer 1'
        assert question.option1 == 'Incorrect 1'
        assert question.option2 == 'Incorrect 2'
        assert question.option3 == 'Incorrect 3'

    def test_edit_quiz_question(self, init_empty_database, test_create_quiz_question):
        question = init_empty_database.session.query(QuizQuestion).filter_by(question='Question 1').first()
        question.answer = 'Answer 2'
        question.option1 = 'Incorrect 1'
        question.option2 = 'Incorrect 2'
        question.option3 = 'Incorrect 3'
        init_empty_database.session.commit()

        question = init_empty_database.session.query(QuizQuestion).filter_by(question='Question 1').first()
        assert question.answer == 'Answer 2'
        assert question.option1 == 'Incorrect 1'
        assert question.option2 == 'Incorrect 2'
        assert question.option3 == 'Incorrect 3'

    def test_delete_quiz_question(self, init_empty_database, test_create_quiz_question):
        question = init_empty_database.session.query(QuizQuestion).filter_by(question='Question 1').first()
        assert question is not None
        init_empty_database.session.delete(question)
        init_empty_database.session.commit()

        question = init_empty_database.session.query(QuizQuestion).filter_by(question='Question 1').first()
        assert question is None
