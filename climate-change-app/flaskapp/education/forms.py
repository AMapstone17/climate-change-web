"""
Contains form for use in posts section
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Type here...', validators=[DataRequired()])
    submit = SubmitField('Add Post')
