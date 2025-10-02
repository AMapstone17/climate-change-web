"""
Contains utility functions for integration tests.
"""

from flask_login import logout_user
from pyotp import TOTP

from flaskapp.models.user import User
from test.data.user_forms import LoginFormData


# Credit: https://stackoverflow.com/a/71164113
def nottest(obj):
    obj.__test__ = False
    return obj


@nottest
def test_login_required_endpoint(test_client, db, endpoint, force_logout=False, logged_out_status_code=401,
                                 logged_in_status_code=200):
    """
    Tests an endpoint that requires the user to be logged in. It first tests the endpoint without logging in, then
    logs in and tests the endpoint again. If force_logout is True, the user will be logged out before testing.
    """
    if force_logout:
        with test_client.application.test_request_context('/'):
            logout_user()


    # Test the endpoint without logging in
    assert test_client.get(endpoint).status_code == logged_out_status_code

    # Log in
    data = LoginFormData(expected=True)
    otp_key = db.session.query(User).filter_by(username=data.username).first().otp_key
    otp = TOTP(otp_key).now()
    data.pin = otp
    assert test_client.post('/login', data=data.to_data(), follow_redirects=True).status_code == 200

    # Test the endpoint after logging in
    assert test_client.get(endpoint).status_code == logged_in_status_code


@nottest
def login_as_admin(test_client, db):
    data = LoginFormData(expected=True, username='admin1', password='Admin1!')
    otp_key = db.session.query(User).filter_by(username=data.username).first().otp_key
    otp = TOTP(otp_key).now()
    data.pin = otp
    assert test_client.post('/login', data=data.to_data(), follow_redirects=True).status_code == 200


@nottest
def login_as_user(test_client, db):
    data = LoginFormData(expected=True)
    otp_key = db.session.query(User).filter_by(username=data.username, role='user').first().otp_key
    otp = TOTP(otp_key).now()
    data.pin = otp
    assert test_client.post('/login', data=data.to_data(), follow_redirects=True).status_code == 200
