"""
This module contains tests for the home views in the Flask application. Each endpoint is tested for security and functionality.
"""

import pytest
from flask_login import logout_user

from test.test_config import test_client, init_empty_database


class TestHomeViews:

    @pytest.fixture(scope='function', autouse=True)
    def clear_session(self, test_client):
        """Clears a session before each test. This logs out any user that may be logged in."""
        with test_client.session_transaction() as session:
            with test_client.application.test_request_context('/'):
                session.clear()
                logout_user()

    def test_index(self, test_client, init_empty_database):
        assert test_client.get('/').status_code == 200

    def test_internal_test(self, test_client, init_empty_database):
        response = test_client.get('/internal/test')
        assert response.status_code == 200
        assert b'Internal test endpoint reached.' in response.data
