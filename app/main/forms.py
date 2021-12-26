import operator
from os import name
from flask import request
from flask.typing import StatusCode
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.fields.choices import SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class CaseForm(FlaskForm):
    name=StringField('name', validators=[DataRequired()])
    description=StringField('description', validators=[DataRequired()])
    # status=SelectField(u'Status', choices=[('Created', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])
    operator=SelectField('pathologist')

    submit = SubmitField('Submit')

class UpdateCaseForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    operator=SelectField('pathologist')
    submit = SubmitField('Update')

class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')