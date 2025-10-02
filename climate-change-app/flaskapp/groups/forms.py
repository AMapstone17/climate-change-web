"""
Contains forms for use in groups/views
"""

import re

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, DateTimeField
from wtforms.validators import DataRequired, Optional
from wtforms.widgets import TextArea


def name_char_check(self, value):
    if re.search('[*?!\^%&()=}\]\[{$#@<>]', value.data):
        raise ValidationError('Must not contain any of the following: * ? ! \' ^ + % & / ( ) = } ] [ { $ # @ < >')


class CreateGroupForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    description = StringField(validators=[DataRequired()], widget=TextArea())
    location = StringField(validators=[DataRequired(), name_char_check])
    event_date = DateTimeField(format='%d-%m-%Y %H:%M', validators=[DataRequired()])
    submit = SubmitField('Create Group')


class EditGroupForm(FlaskForm):
    title = StringField(validators=[Optional()])
    description = StringField(validators=[Optional()], widget=TextArea())
    location = StringField(validators=[name_char_check, Optional()])
    event_date = DateTimeField(validators=[Optional()], format='%d-%m-%Y %H:%M')
    submit = SubmitField('Edit Group')
