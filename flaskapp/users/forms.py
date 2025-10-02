
import re

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, ValidationError, Length, EqualTo, NoneOf

from flaskapp.extensions import CustomRecaptcha


def validate_password(form, password):
    p = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])')
    if not p.match(password.data):
        raise ValidationError('Password must contain at least 1 digit, '
                              '1 lowercase letter, 1 uppercase letter and 1 special character')


def validate_date_of_birth(form, date_of_birth):
    d = re.compile(r'^\d{2}/\d{2}/\d{4}$')
    if not d.match(date_of_birth.data):
        raise ValidationError('Date must only contain appropriate digits'
                              ' and forward slashes (/) of the form: DD/MM/YYYY')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    firstname = StringField('First Name', validators=[DataRequired(), NoneOf("*?!'^+%&/()=[]{}$#@<>")])
    lastname = StringField('Last Name', validators=[DataRequired(), NoneOf("*?!'^+%&/()=[]{}$#@<>")])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6), validate_password])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    date_of_birth = StringField('Date of Birth', validators=[DataRequired(), validate_date_of_birth])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    pin = StringField(validators=[DataRequired()])
    recaptcha = RecaptchaField(validators=[CustomRecaptcha()])
    submit = SubmitField()


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(id='password', validators=[DataRequired()])
    show_password = BooleanField('Show password', id='check')
    new_password = PasswordField(
        validators=[DataRequired(), Length(min=6, message="Must be at least 6 characters long"),
                    validate_password])
    confirm_new_password = PasswordField(
        validators=[DataRequired(), EqualTo('new_password', message='Both new password fields must be equal')])
    submit = SubmitField('Change Password')


class CreateAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Add Administrator')
