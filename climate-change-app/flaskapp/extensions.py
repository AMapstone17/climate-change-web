"""
Contains custom extensions (plus database) for the Flask application.
"""

import logging
from datetime import datetime
from functools import wraps
from uuid import UUID

from flask import request, render_template, current_app
from flask_login import current_user
from flask_qrcode import QRcode
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Recaptcha
from sqlalchemy.orm import Query


class UUIDQuery(Query):
    def get_by_id(self, id):
        """Finds an object by its ID, automatically converting to a UUID if necessary."""
        if isinstance(id, str):
            id = UUID(id)
        return self.get(id)


class CustomRecaptcha(Recaptcha):
    """
    Inherits from the Recaptcha class to allow for bypassing the Recaptcha check.
    """

    def __call__(self, form, field):
        bypass_recaptcha = current_app.config.get('BYPASS_RECAPTCHA', False) == 'True'

        if bypass_recaptcha:
            return True

        return super().__call__(form, field)


def roles_required(*roles):
    """Decorator to check if the current user has the required role."""

    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                logging.warning('SECURITY - Unauthorised Access Attempt [%s, %s, %s]',
                                current_user.id,
                                current_user.username,
                                request.remote_addr)

                return render_template('403.html')
            return f(*args, **kwargs)

        return wrapped

    return wrapper


# wrapper function to confirm user is over 16:
def over_16_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.date_of_birth:
            now = datetime.now()
            try:
                dob = datetime.strptime(current_user.date_of_birth, '%d/%m/%Y')
                age = (now - dob)
                if age.days < 5840:
                    return render_template('403.html')
            except:
                return f(*args, **kwargs)
            return f(*args, **kwargs)

    return wrapped


db = SQLAlchemy(query_class=UUIDQuery)
qrcode = QRcode()
