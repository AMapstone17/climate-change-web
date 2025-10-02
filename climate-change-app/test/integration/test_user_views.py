"""
This module contains tests for the user views in the Flask application. Each endpoint is tested for security and functionality.
"""
import json

import pytest
from flask_login import logout_user
from pyotp import TOTP

from flaskapp.models.user import User
from test.data.user_forms import RegisterFormData, LoginFormData, ChangePasswordFormData, CreateAdminFormData
from test.integration.util import test_login_required_endpoint, login_as_admin, login_as_user
from test.test_config import test_client, init_filled_database, init_empty_database


class TestUserViews:

    @pytest.fixture(scope='function', autouse=True)
    def clear_session(self, test_client):
        """Clears a session before each test. This logs out any user that may be logged in."""
        with test_client.session_transaction() as session:
            with test_client.application.test_request_context('/'):
                session.clear()
                logout_user()

    @staticmethod
    def perform_registration_test(test_client, data, expected_to_be_duplicate=False):
        """Performs a test to register a user. Calls the endpoint, and makes assertions based on the data provided."""
        response = test_client.post('/register', data=data.to_data(), follow_redirects=True)

        if data.expected:
            assert response.status_code == 200
            user = User.query.filter_by(username=data.username).first()
            assert user is not None
            assert user.email == data.email
            assert response.request.path.endswith('setup_2fa')
        else:
            assert response.status_code == 400
            user = User.query.filter_by(username=data.username).first()
            if expected_to_be_duplicate:
                assert user is not None
            else:
                assert user is None
            assert response.request.path.endswith('register')

    @pytest.mark.parametrize('data', [
        RegisterFormData(expected=True, email='bob@bob.com'),
        RegisterFormData(expected=True, email='myemail@gmail.com', password='LongEnough123!', confirm_password='LongEnough123!'),
        RegisterFormData(expected=False, email='invalid@email'),
        RegisterFormData(expected=False, email='invalid@.com'),
        RegisterFormData(expected=True, date_of_birth='01/01/2020'),
        RegisterFormData(expected=False, email=''),
        RegisterFormData(expected=False, username=''),
        RegisterFormData(expected=False, password=''),
    ])
    def test_register(self, test_client, init_empty_database, data: RegisterFormData):
        self.perform_registration_test(test_client, data)

    @pytest.mark.parametrize('data', [
        RegisterFormData(expected=False, username='admin1'),  # duplicate username
        RegisterFormData(expected=False, username='bob123'),  # duplicate username
        RegisterFormData(expected=False, email='admin@user.com'),  # duplicate email
    ])
    def test_register_with_existing_user(self, test_client, init_filled_database, data):
        self.perform_registration_test(test_client, data, expected_to_be_duplicate=True)

    def test_register_when_logged_in(self, test_client, init_filled_database):
        assert test_client.get('/register').status_code == 200
        login_as_admin(test_client, init_filled_database)
        assert test_client.get('/register').status_code == 400

    @pytest.mark.parametrize('data', [
        LoginFormData(expected=True, username='bob123', password='Password123!', _fill_otp=True),
        LoginFormData(expected=False, username='bob123', password='Password123!', _fill_otp=False),
        LoginFormData(expected=False, username='bob123', password='WrongPassword!', _fill_otp=True),
        LoginFormData(expected=False, username='bob123', password='WrongPasswordAndOTP!', _fill_otp=False),
        LoginFormData(expected=True, username='amelia123', password='Amelia123@', _fill_otp=True),
        LoginFormData(expected=False, username='amelia123', password='amelia123@', _fill_otp=True),
        LoginFormData(expected=False, username='amelia123', password=''),
        LoginFormData(expected=False, username=''),
    ])
    def test_login(self, test_client, init_filled_database, data: LoginFormData):
        if data._fill_otp:
            user = init_filled_database.session.query(User).filter_by(username=data.username).first()
            if user:
                data.pin = TOTP(user.otp_key).now()

        response = test_client.post('/login', data=data.to_data(), follow_redirects=True)

        assert response.status_code == (200 if data.expected else 400)

    def test_login_when_logged_in(self, test_client, init_filled_database):
        assert test_client.get('/login').status_code == 200
        login_as_admin(test_client, init_filled_database)
        assert test_client.get('/login').status_code == 400

    def test_login_attempts(self, test_client, init_filled_database):
        data = LoginFormData(expected=False, username='bob123', password='WrongPassword!', _fill_otp=False)
        for _ in range(3):
            last_response = test_client.post('/login', data=data.to_data(), follow_redirects=True)
            assert last_response.status_code == 400

        assert 'Number of incorrect login attempts exceeded' in last_response.get_data(as_text=True)

        assert test_client.get('/reset', follow_redirects=True).status_code == 200

        data = LoginFormData(expected=True)
        user = init_filled_database.session.query(User).filter_by(username=data.username).first()
        data.pin = TOTP(user.otp_key).now()
        assert test_client.post('/login', data=data.to_data(), follow_redirects=True).status_code == 200

    def test_account(self, test_client, init_filled_database):
        test_login_required_endpoint(test_client, init_filled_database, '/account')

    def test_leaderboard(self, test_client, init_filled_database):
        test_login_required_endpoint(test_client, init_filled_database, '/leaderboard')

    def test_game_dashboard(self, test_client, init_filled_database):
        test_login_required_endpoint(test_client, init_filled_database, '/game_dashboard')

    def test_game(self, test_client, init_filled_database):
        test_login_required_endpoint(test_client, init_filled_database, '/game')

    def test_account_delete(self, test_client, init_filled_database):
        user = init_filled_database.session.query(User).filter_by(username='bob123').first()
        assert user is not None

        test_login_required_endpoint(test_client, init_filled_database, '/account/delete',
                                     logged_in_status_code=302)  # redirects to home

        user = init_filled_database.session.query(User).filter_by(username='bob123').first()
        assert user is None

    def test_settings(self, test_client, init_filled_database):
        test_login_required_endpoint(test_client, init_filled_database, '/settings')

    def test_reset(self, test_client, init_filled_database):
        with test_client.session_transaction() as session:
            session['authentication_attempts'] = 2

        assert test_client.get('/reset').status_code == 302  # redirects to login

        with test_client.session_transaction() as session:
            assert session.get('authentication_attempts') == 0

    def test_logout(self, test_client, init_filled_database):
        test_login_required_endpoint(test_client, init_filled_database, '/logout', logged_in_status_code=302)

    def test_setup_2fa_with_valid_username(self, test_client, init_filled_database):
        with test_client.session_transaction() as session:
            session['username'] = 'bob123'

        response = test_client.get('/setup_2fa')
        assert response.status_code == 200

    def test_setup_2fa_with_invalid_username(self, test_client, init_filled_database):
        with test_client.session_transaction() as session:
            session['username'] = 'some_unknown_username'

        response = test_client.get('/setup_2fa')
        assert response.status_code == 302

    def test_setup_2fa_with_no_username(self, test_client, init_filled_database):
        with test_client.session_transaction() as session:
            if 'username' in session:
                del session['username']

        response = test_client.get('/setup_2fa')
        assert response.status_code == 302

    @pytest.mark.parametrize('data', [
        ChangePasswordFormData(expected=True, current_password='Admin1!', new_password='NewPassword123!', confirm_new_password='NewPassword123!'),
        ChangePasswordFormData(expected=False, current_password='Admin1!', new_password='NewPassword123!', confirm_new_password='NewPassword123', _incorrect_password_error_message=False, _must_be_different_error_message=False),
        ChangePasswordFormData(expected=False, current_password='Admin1!', new_password='Admin1!', confirm_new_password='Admin1', _incorrect_password_error_message=False, _must_be_different_error_message=False),
        ChangePasswordFormData(expected=False, current_password='Admin1', new_password='NewPassword123!', confirm_new_password='NewPassword123!', _incorrect_password_error_message=True, _must_be_different_error_message=False),
        ChangePasswordFormData(expected=False, current_password='Admin1', new_password='NewPassword123!', confirm_new_password='', _incorrect_password_error_message=False, _must_be_different_error_message=False),
        ChangePasswordFormData(expected=False, current_password='Admin1!', new_password='Admin1!', confirm_new_password='Admin1!', _incorrect_password_error_message=False, _must_be_different_error_message=True),
    ])
    def test_change_password(self, test_client, init_filled_database, data):
        login_as_admin(test_client, init_filled_database)

        response = test_client.post('/settings/change_password', data=data.to_data(), follow_redirects=True)
        assert response.request.path.endswith('settings')
        assert response.status_code == 200

        response_text = response.get_data(as_text=True)

        if data.expected:
            assert 'Password changed successfully' in response_text
            user = init_filled_database.session.query(User).filter_by(username='admin1').first()
            assert user is not None
            assert user.verify_password(data.new_password)
        else:
            if data._general_error_message:
                assert 'Failed to change password' in response_text
            if data._incorrect_password_error_message:
                assert 'Incorrect password' in response_text
            if data._must_be_different_error_message:
                assert 'New password must be different from old password' in response_text

            user = init_filled_database.session.query(User).filter_by(username='admin1').first()
            assert user is not None

    @pytest.mark.parametrize('data', [
        CreateAdminFormData(expected=True, email='bobsmith123@gmail.com', username='bob123', _insufficient_permissions_error_message=False),
        CreateAdminFormData(expected=False, email='wrong@email.com', username='bob123', _insufficient_permissions_error_message=False),
        CreateAdminFormData(expected=False, email='bobsmith123@gmail.com', username='wrongusername', _insufficient_permissions_error_message=False),
        CreateAdminFormData(expected=False, email='', username='', _user_does_not_exist_error_message=False, _insufficient_permissions_error_message=False),
    ])
    def test_add_admin_as_admin(self, test_client, init_filled_database, data):
        login_as_admin(test_client, init_filled_database)

        response = test_client.post('/settings/create_admin', data=data.to_data(), follow_redirects=True)
        assert response.request.path.endswith('settings')
        assert response.status_code == 200

        if data.expected:
            assert 'New administrator added successfully' in response.get_data(as_text=True)
            user = init_filled_database.session.query(User).filter_by(username=data.username).first()
            assert user is not None
            assert user.role == 'admin'
        else:
            if data._general_error_message:
                assert 'Failed to add new administrator' in response.get_data(as_text=True)
            if data._user_does_not_exist_error_message:
                assert 'Incorrect information provided or user does not exist' in response.get_data(as_text=True)
            if data._insufficient_permissions_error_message:
                assert 'You are not authorised to perform this action' in response.get_data(as_text=True)
            user = init_filled_database.session.query(User).filter_by(username=data.username).first()
            if user:
                assert user.role != 'admin'

    def test_add_admin_as_user(self, test_client, init_filled_database):
        login_as_user(test_client, init_filled_database)
        response = test_client.post('/settings/create_admin', data=CreateAdminFormData(expected=False).to_data(), follow_redirects=True)
        assert response.status_code == 200

        assert 'You are not authorised to perform this action' in response.get_data(as_text=True)

    def test_update_highsore(self, test_client, init_filled_database):
        login_as_admin(test_client, init_filled_database)

        def test_score(score, expected: bool):
            data = json.dumps({'score': score})
            response = test_client.post('/update-highscore', data=data, headers={'Content-Type': 'application/json'})
            assert response.status_code == 200

            json_response = json.loads(response.data)
            if expected:
                assert json_response['high_score'] == score
            else:
                assert json_response['high_score'] != score

        test_score(100, True)
        test_score(200, True)
        test_score(5, False)
        test_score(-1, False)
        test_score(201, True)
