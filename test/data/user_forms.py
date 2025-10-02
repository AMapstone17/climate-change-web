"""
Contains dataclasses for user forms.
"""

from dataclasses import dataclass

from test.data.base_form import BaseFormData


@dataclass
class RegisterFormData(BaseFormData):
    email: str = 'bob@bob.com'
    username: str = 'bob123'
    firstname: str = 'Bob'
    lastname: str = 'Smith'
    password: str = 'Password123!'
    confirm_password: str = 'Password123!'
    date_of_birth: str = '01/01/1980'


@dataclass
class LoginFormData(BaseFormData):
    username: str = 'bob123'
    password: str = 'Password123!'
    recaptcha: str = None  # recaptcha is needed here to confirm test data, but is not actually validated
    pin: str = '123456'

    _fill_otp: bool = True


@dataclass
class ChangePasswordFormData(BaseFormData):
    current_password: str = 'Password123!'
    show_password: bool = False
    new_password: str = 'Password123!'
    confirm_new_password: str = 'Password123!'

    _general_error_message: bool = True
    _incorrect_password_error_message: bool = True
    _must_be_different_error_message: bool = True


@dataclass
class CreateAdminFormData(BaseFormData):
    email: str = 'newadmin@example.com'
    username: str = 'admin'

    _general_error_message: bool = True
    _user_does_not_exist_error_message: bool = True
    _insufficient_permissions_error_message: bool = True
