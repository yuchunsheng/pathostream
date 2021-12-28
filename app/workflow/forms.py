from flask_wtf.form import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired


class CaseForm(FlaskForm):
    name=StringField('name', validators=[DataRequired()])
    description=StringField('description', validators=[DataRequired()])
    # status=SelectField(u'Status', choices=[('Created', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])
    operator=SelectField('pathologist')

    submit = SubmitField('Submit')

class RejectCaseForm(FlaskForm):
    name = StringField('name', render_kw={'disabled':''})
    description = StringField('description', validators=[DataRequired()])

    submit = SubmitField('Reject')

class UpdateCaseForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    operator=SelectField('pathologist')
    submit = SubmitField('Update')
