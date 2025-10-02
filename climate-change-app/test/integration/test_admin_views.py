"""
This module contains tests for the admin views. Each endpoint is tested for security and functionality.
"""

from uuid import UUID

import pytest
from flask_login import logout_user

from flaskapp.models.quiz_question import QuizQuestion
from test.data.admin_forms import AdminQuizQuestionFormData
from test.integration.util import test_login_required_endpoint, login_as_admin
from test.test_config import test_client, init_filled_database


class TestAdminViews:

    @pytest.fixture(scope='function', autouse=True)
    def clear_session(self, test_client):
        """Clears a session before each test. This logs out any user that may be logged in."""
        with test_client.session_transaction() as session:
            with test_client.application.test_request_context('/'):
                session.clear()
                logout_user()

    def test_admin_edit_questions_security(self, test_client, init_filled_database):
        test_login_required_endpoint(test_client, init_filled_database, '/admin/edit_questions')

    @pytest.mark.parametrize('data', [
        AdminQuizQuestionFormData(expected=True),
        AdminQuizQuestionFormData(expected=False, question=''),
        AdminQuizQuestionFormData(expected=False, answer=''),
        AdminQuizQuestionFormData(expected=False, option1=''),
        AdminQuizQuestionFormData(expected=False, option2=''),
        AdminQuizQuestionFormData(expected=False, option3=''),
    ])
    def test_admin_new_question(self, test_client, init_filled_database, data: AdminQuizQuestionFormData):
        login_as_admin(test_client, init_filled_database)
        response = test_client.post('/admin/new_question', data=data.to_data(), follow_redirects=True)

        if data.expected:
            assert response.status_code == 200
            question = QuizQuestion.query.filter_by(question=data.question).first()
            assert question is not None
            assert question.answer == data.answer
            assert question.option1 == data.option1
            assert question.option2 == data.option2
            assert question.option3 == data.option3
        else:
            question = QuizQuestion.query.filter_by(question=data.question).first()
            assert question is None
            assert response.request.path.endswith('edit_questions')

    @pytest.mark.parametrize('data', [
        AdminQuizQuestionFormData(expected=True, edit=True, question='The capital of France is what?'),
        AdminQuizQuestionFormData(expected=True, edit=True, answer='Paris!!'),
        AdminQuizQuestionFormData(expected=False, edit=True, question=''),
        AdminQuizQuestionFormData(expected=False, edit=True, option2=''),
    ])
    def test_admin_edit_questions_edit(self, test_client, init_filled_database, data: AdminQuizQuestionFormData):
        # find example question id
        question = QuizQuestion.query.all()[0]
        data.id = question.id

        login_as_admin(test_client, init_filled_database)
        response = test_client.post('/admin/edit_questions', data=data.to_data(), follow_redirects=True)

        if data.expected:
            assert response.status_code == 200
            question = QuizQuestion.query.get_by_id(data.id)
            assert question is not None
            assert question.question == data.question
            assert question.answer == data.answer
            assert question.option1 == data.option1
            assert question.option2 == data.option2
            assert question.option3 == data.option3
        else:
            question = QuizQuestion.query.get_by_id(data.id)
            assert question is not None  # ensure the question still exists
            assert response.request.path.endswith('edit_questions')

    @pytest.mark.parametrize('data', [
        AdminQuizQuestionFormData(expected=True, delete=True),
        AdminQuizQuestionFormData(expected=False, delete=True, id=UUID('00000000-0000-0000-0000-000000000000')),
    ])
    def test_admin_edit_questions_delete(self, test_client, init_filled_database, data: AdminQuizQuestionFormData):
        if not data.id:
            question = QuizQuestion.query.all()[0]
            data.id = question.id

        question_exists_before = QuizQuestion.query.get_by_id(data.id) is not None

        login_as_admin(test_client, init_filled_database)
        response = test_client.post('/admin/edit_questions', data=data.to_data(), follow_redirects=True)

        if data.expected:
            assert response.status_code == 200
            question = QuizQuestion.query.get_by_id(data.id)
            assert question is None
        else:
            question = QuizQuestion.query.get_by_id(data.id)
            if question_exists_before:
                assert question is not None
            else:
                assert question is None
            assert response.request.path.endswith('edit_questions')
