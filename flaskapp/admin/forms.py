"""
This file contains form for use in Admin section
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class QuizQuestionForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    answer = StringField('Correct Option', validators=[DataRequired()])
    option1 = StringField('Incorrect Option 1', validators=[DataRequired()])
    option2 = StringField('Incorrect Option 2', validators=[DataRequired()])
    option3 = StringField('Incorrect Option 3', validators=[DataRequired()])
