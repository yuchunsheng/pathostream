from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.fields.choices import SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')



class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')