"""
Contains unit tests for the forms used in the application. Each form is tested by creating an instance,
setting the data to the expected values, and then validating the form.
"""

import pytest

from flaskapp.admin.forms import QuizQuestionForm
from flaskapp.groups.forms import CreateGroupForm
from flaskapp.quiz.forms import QuizForm
from flaskapp.users.forms import RegisterForm, LoginForm, ChangePasswordForm, CreateAdminForm
from test.data.admin_forms import AdminQuizQuestionFormData
from test.data.base_form import BaseFormData
from test.data.group_forms import CreateGroupFormData
from test.data.quiz_forms import QuizFormData
from test.data.user_forms import RegisterFormData, LoginFormData, ChangePasswordFormData, CreateAdminFormData


class TestForms:

    @staticmethod
    def perform_test(form_class, form_data: BaseFormData, strip_submit=False, inject=None, strip_fields=None):
        """
        Performs a test by creating a form instance and validating it against the expected result.
        :param form_class: The form class to test
        :param form_data: A dataclass instance containing the test data
        :param strip_submit: Set to True if the form does not contain a submit field
        :param inject: A function that can be used to inject data into the form before validation
        """
        if strip_fields is None:
            strip_fields = []

        if strip_submit:
            strip_fields.append('submit')

        converted_data = form_data.to_data(strip_fields=strip_fields)
        form = form_class(data=converted_data, meta={'csrf': False})

        if inject:
            form = inject(form)

        assert form.validate() == form_data.expected
        if form_data.expected:
            assert len(form.errors) == 0

        assert form.data == converted_data

    @pytest.mark.parametrize('data', [
        RegisterFormData(expected=True),
        RegisterFormData(expected=False, confirm_password='Password123'),
        RegisterFormData(expected=False, email='bob@invalid'),
        RegisterFormData(expected=False, password='short', confirm_password='short'),
    ])
    def test_register_form(self, test_client, data):
        with test_client.application.test_request_context('/'):
            self.perform_test(RegisterForm, data)

    @pytest.mark.parametrize('data', [
        LoginFormData(expected=True),
        LoginFormData(expected=False, pin=None),
        LoginFormData(expected=False, username=None),
        LoginFormData(expected=True, username='123'),
        LoginFormData(expected=False, username=None),
    ])
    def test_login_form(self, test_client, data):
        with test_client.application.test_request_context('/'):
            self.perform_test(LoginForm, data)

    @pytest.mark.parametrize('data', [
        ChangePasswordFormData(expected=True),
        ChangePasswordFormData(expected=False, new_password='short', confirm_new_password='short'),
        ChangePasswordFormData(expected=True, new_password='Acceptable1!', confirm_new_password='Acceptable1!'),
        ChangePasswordFormData(expected=False, confirm_new_password='Password123'),
    ])
    def test_change_password_form(self, test_client, data):
        with test_client.application.test_request_context('/'):
            self.perform_test(ChangePasswordForm, data)

    @pytest.mark.parametrize('data', [
        CreateAdminFormData(expected=True),
        CreateAdminFormData(expected=False, email='invalidemail'),
        CreateAdminFormData(expected=False, username=''),
    ])
    def test_create_admin_form(self, test_client, data):
        with test_client.application.test_request_context('/'):
            self.perform_test(CreateAdminForm, data)

    @pytest.mark.parametrize('data', [
        AdminQuizQuestionFormData(expected=True),
        AdminQuizQuestionFormData(expected=False, question=''),
        AdminQuizQuestionFormData(expected=False, answer=''),
        AdminQuizQuestionFormData(expected=False, option1=''),
        AdminQuizQuestionFormData(expected=False, option2=''),
        AdminQuizQuestionFormData(expected=False, option3=''),
    ])
    def test_admin_quiz_question_form(self, test_client, data):

        with test_client.application.test_request_context('/'):
            self.perform_test(QuizQuestionForm, data, strip_submit=True, strip_fields=['edit', 'delete', 'id'])

    @pytest.mark.parametrize('data', [
        CreateGroupFormData(expected=True),
        CreateGroupFormData(expected=False, title=''),
        CreateGroupFormData(expected=False, description=''),
        CreateGroupFormData(expected=False, location=''),
        CreateGroupFormData(expected=False, event_date=''),
        CreateGroupFormData(expected=False, event_date='01/06 12:00'),  # invalid date
        CreateGroupFormData(expected=False, location='> Newcastle upon Tyne <'),  # invalid characters
    ])
    def test_create_group_form(self, test_client, data):
        with test_client.application.test_request_context('/'):
            self.perform_test(CreateGroupForm, data)

    @pytest.mark.parametrize('data', [
        QuizFormData(expected=True),
        QuizFormData(expected=False, option=-1),
        QuizFormData(expected=True, option=0),
        QuizFormData(expected=False, option=4),
        QuizFormData(expected=True, option=2),
    ])
    def test_quiz_form(self, test_client, data):
        def set_sample_choices(form):
            form.option.choices = [(0, 'A'), (1, 'B'), (2, 'C'), (3, 'D')]
            return form

        with test_client.application.test_request_context('/'):
            self.perform_test(QuizForm, data, inject=set_sample_choices)
