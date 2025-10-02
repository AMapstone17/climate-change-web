"""
This file contains the form used in the quiz section
"""

from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField


class QuizForm(FlaskForm):
    option = RadioField('Choose an option', choices=[], coerce=int)
    submit = SubmitField('Submit')
