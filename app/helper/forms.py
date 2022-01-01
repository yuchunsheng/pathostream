from flask_wtf.form import FlaskForm
from wtforms.fields.simple import FileField, SubmitField
from flask_wtf.file import  FileRequired


class PCUCSVUplodForm(FlaskForm):
    file = FileField('CSV File', validators=[FileRequired('no file!')])
    submit = SubmitField('Submit')