"""
Contains model and function for users
"""

import uuid

import bcrypt
import pyotp
from flask import current_app
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID

from flaskapp.extensions import db


def hash_user_password(password) -> str:
    """Hashes user password using bcrypr."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User authentication information.
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    otp_key = db.Column(db.String(32), nullable=False, default=pyotp.random_base32())

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')

    def __init__(self, email, username, firstname, lastname, date_of_birth, password, role):
        self.email = email
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.date_of_birth = date_of_birth
        self.password = hash_user_password(password)
        self.role = role

    @classmethod
    def with_custom_id(cls, user_id, email, username, firstname, lastname, date_of_birth, password, role):
        """Allows custom ID setting, e.g. for build_samples.py"""
        user = cls(email=email, username=username, firstname=firstname, lastname=lastname,
                   date_of_birth=date_of_birth, password=password, role=role)
        user.id = user_id
        return user

    def verify_password(self, password) -> bool:
        """Verify user password using bcrypt."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def verify_otp(self, otp) -> bool:
        """Verify user OTP."""
        if current_app.config.get('BYPASS_2FA', False):
            return True
        return pyotp.totp.TOTP(self.otp_key).verify(otp)

    def get_2fa_uri(self):
        return str(pyotp.totp.TOTP(self.otp_key).provisioning_uri(
            name=self.email,
            issuer_name='ClimateChamps.org')
        )

    def is_admin(self):
        return self.role == 'admin'
