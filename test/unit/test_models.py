"""
Contains unit tests for the models in the Flask app. Each model is tested by creating and editing its attributes, and using methods.
"""

from datetime import datetime

from flaskapp.models.leaderboard_entry import LeaderboardEntry
from flaskapp.models.quiz_question import QuizQuestion
from flaskapp.models.user import User


class TestModels:

    @staticmethod
    def get_test_users() -> tuple[User, User]:
        """Return two test users."""
        bob = User(
            username='bob123',
            firstname='Bob',
            lastname='Smith',
            date_of_birth=datetime(1980, 1, 1),
            password='password123',
            email='bobsmith123@gmail.com',
            role='user'
        )
        amelia = User(
            username='amelia123',
            firstname='Amelia',
            lastname='Jones',
            date_of_birth=datetime(1990, 1, 1),
            password='password123',
            email='ameliajones123@gmail.com',
            role='user'
        )
        return bob, amelia

    def test_user_model(self):
        bob, amelia = self.get_test_users()

        assert bob.username == 'bob123'
        assert amelia.username == 'amelia123'

        assert bob.verify_password('password123')
        assert not bob.verify_password('password')

        assert amelia.verify_password('password123')
        assert not amelia.verify_password('Password123')

        assert amelia.password != 'password123'  # password should be hashed

    def test_quiz_question_model(self):
        questions = []
        for i in range(1, 4):
            question = QuizQuestion(
                question=f'Question {i}',
                answer=f'Answer {i}',
                option1=f'Incorrect 1 {i}',
                option2=f'Incorrect 2 {i}',
                option3=f'Incorrect 3 {i}'
            )
            questions.append(question)

        a, b, c = questions[:3]

        assert a.question == 'Question 1'
        assert a.answer == 'Answer 1'

        assert a.check_answer('Answer 1')
        assert not a.check_answer('answer 1')  # case insensitivity not needed; multiple choice

        assert not a.check_answer('Incorrect 1 1')
        assert not a.check_answer('Incorrect 2 1')
        assert not a.check_answer('Incorrect 3 1')

        assert a != b
        assert a != c
        assert a == a
        assert b == b

    def test_leaderboard_entry_model(self):
        bob, amelia = self.get_test_users()

        bob_entry = LeaderboardEntry(user_id=bob.id, score=100, game_highscore=4)
        amelia_entry = LeaderboardEntry(user_id=amelia.id, score=200, game_highscore=9)

        assert bob_entry.user_id == bob.id
        assert bob_entry.score == 100

        assert amelia_entry.user_id == amelia.id
        assert amelia_entry.score == 200

        assert amelia_entry > bob_entry
        assert amelia_entry >= bob_entry

        assert bob_entry < amelia_entry
        assert bob_entry <= amelia_entry

        assert 12 > amelia_entry.game_highscore > bob_entry.game_highscore > 3
