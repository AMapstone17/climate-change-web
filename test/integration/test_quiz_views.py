"""
This module contains tests for the quiz views. Each endpoint is tested for security and functionality.
"""

import pytest
from flask_login import logout_user, current_user
from flaskapp.models.quiz_question import QuizQuestion
from flaskapp.models.leaderboard_entry import LeaderboardEntry
from test.integration.util import test_login_required_endpoint, login_as_admin


class TestQuizViews:
    @pytest.fixture(scope='function', autouse=True)
    def clear_session(self, test_client):
        """Clears a session before each test. This logs out any user that may be logged in."""
        with test_client.session_transaction() as session:
            with test_client.application.test_request_context('/'):
                session.clear()
                logout_user()

    def test_quiz_security(self, test_client, init_filled_database):
        test_login_required_endpoint(test_client, init_filled_database, '/quiz')

    def test_quiz_start_security(self, test_client, init_filled_database):
        test_login_required_endpoint(test_client, init_filled_database, '/quiz-start', logged_in_status_code=302)

    def test_quiz_result_security(self, test_client, init_filled_database):
        test_login_required_endpoint(test_client, init_filled_database, '/quiz-result', logged_in_status_code=302)

    def test_generate_quiz(self, test_client, init_filled_database):
        with test_client.application.app_context():
            quiz_question_count = QuizQuestion.query.count()
            assert quiz_question_count > 0, "Database should contain quiz questions"
            from flaskapp.quiz.views import generate_quiz
            quiz_questions = generate_quiz()
            assert len(quiz_questions) == 10

    def test_quiz_scoring(self, test_client, init_filled_database):
        with test_client as client:
            login_as_admin(test_client, init_filled_database)
            record = LeaderboardEntry.query.get_by_id(current_user.id)
            user_score = record.score
            response = client.get('/quiz-start', follow_redirects=True, data={'question_index':0, 'option':'1'})
            assert response.status_code == 200

            with client.session_transaction() as sess:
                quiz_questions = sess['quiz_questions']
                score = sess['score']
                print(f"Initial score: {score}")

                # Simulate answering each question correctly
            for i in range(len(quiz_questions)):
                question = quiz_questions[i]
                index = int(i)
                response = client.post(f'/quiz-play/{i}', data={'question_index': index, 'option': '1'}, follow_redirects=True)
                assert response.status_code == 200  # Ensure each quiz play page is loaded successfully

                with client.session_transaction() as sess:
                    score = sess['score']
                    print(f"Score after question {i + 1}: {score}")

                # Ensure the score is 10
            assert score == 10

            # Finish the quiz and check the result
            response = client.get('/quiz-result')
            assert response.status_code == 200
            assert b'Score: 10' in response.data

            new_record = LeaderboardEntry.query.get_by_id(current_user.id)
            new_user_score = new_record.score

            assert new_user_score != user_score


