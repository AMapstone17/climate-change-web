"""
This module contains tests for the education views. Each endpoint is tested for security and functionality.
"""

import pytest
from flask_login import logout_user

from flaskapp.models.blog_post import BlogPost
from test.integration.util import test_login_required_endpoint
from test.test_config import test_client, init_filled_database


class TestEducationViews:

    @pytest.fixture(scope='function', autouse=True)
    def clear_session(self, test_client):
        """Clears a session before each test. This logs out any user that may be logged in."""
        with test_client.session_transaction() as session:
            with test_client.application.test_request_context('/'):
                session.clear()
                logout_user()

    def test_all_posts_security(self, test_client, init_filled_database):
        test_login_required_endpoint(test_client, init_filled_database, '/posts', logged_out_status_code=200)

    def test_post_security(self, test_client, init_filled_database):
        post = BlogPost.query.first()
        test_login_required_endpoint(test_client, init_filled_database, '/posts/' + str(post.id), logged_out_status_code=200)

    def test_all_posts(self, test_client, init_filled_database):
        example_post = BlogPost.query.first()

        response = test_client.get('/posts')
        assert response.status_code == 200
        text = response.get_data(as_text=True)

        assert 'Posts' in text
        assert example_post.title in text

    def test_post(self, test_client, init_filled_database):
        example_post = BlogPost.query.first()

        response = test_client.get('/posts/' + str(example_post.id))
        assert response.status_code == 200
        text = response.get_data(as_text=True)

        assert example_post.title in text
        assert example_post.content in text
