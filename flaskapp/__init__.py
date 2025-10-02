

from flask import Flask, render_template
from flask_login import LoginManager
from werkzeug.exceptions import HTTPException

from flaskapp.extensions import db, qrcode
from flaskapp.models.user import User

login_manager = LoginManager()


def create_app(config_class):
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_prefixed_env()

    db.init_app(app)
    qrcode.init_app(app)
    login_manager.init_app(app)

    from .home import views as home_views
    app.register_blueprint(home_views.bp)

    from .users import views as users_views
    app.register_blueprint(users_views.bp)

    from .quiz import views as quiz_views
    app.register_blueprint(quiz_views.bp)

    from .admin import views as admin_views
    app.register_blueprint(admin_views.bp)

    from .groups import views as groups_views
    app.register_blueprint(groups_views.bp)

    from .education import views as education_views
    app.register_blueprint(education_views.bp)

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        """
        Handles any HTTP exception. If the error code is in the custom_page_codes list, it will render the
        corresponding error page. Otherwise, it will render the 500 error page.
        """

        custom_page_codes = [400, 401, 403, 404, 500, 503]
        if e.code in custom_page_codes:
            return render_template(f'{e.code}.html'), e.code
        return render_template('500.html'), 500

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get_by_id(user_id)
