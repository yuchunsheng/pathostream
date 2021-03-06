from distutils.text_file import TextFile
from flask_wtf.form import FlaskForm
from flask_wtf.file import  FileRequired
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import FloatField, IntegerField
from wtforms.fields.simple import FileField, StringField, SubmitField
from wtforms import BooleanField, TextAreaField



class CaseForm(FlaskForm):
    cp_num = StringField('cp_num')
    specimen_class = StringField('specimen_class')
    part_type = StringField('part_type')
    group_external_value = StringField('group_external_value')
    part_description = StringField('part_description')
    block_count = IntegerField('block_count', default=0)
    doctor_code = StringField('doctor_code')
    specialty = StringField('specialty')
    location = StringField('location')
    pcu = FloatField('PCU', default=0)
    operator=SelectField('pathologist')

    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')

class UpdateCaseForm(FlaskForm):
    cp_num = StringField('cp_num')
    specimen_class = StringField('specimen_class')
    part_type = StringField('part_type')
    group_external_value = StringField('group_external_value')
    part_description = StringField('part_description')
    block_count = IntegerField('block_count')
    doctor_code = StringField('doctor_code')
    specialty = StringField('specialty')
    location = StringField('location')
    pcu = FloatField('PCU')
    operator=SelectField('pathologist')
    submit = SubmitField('Update')
    cancel = SubmitField('Cancel')

class RejectCaseForm(FlaskForm):
    cp_num = StringField('cp_num', render_kw={'disabled':''})
    specimen_class = StringField('specimen_class', render_kw={'disabled':''})
    part_type = StringField('part_type', render_kw={'disabled':''})
    group_external_value = StringField('group_external_value', render_kw={'disabled':''})
    part_description = StringField('part_description', render_kw={'disabled':''})
    block_count = IntegerField('block_count', render_kw={'disabled':''})
    doctor_code = StringField('doctor_code', render_kw={'disabled':''})
    specialty = StringField('specialty', render_kw={'disabled':''})
    location = StringField('location', render_kw={'disabled':''})

    pcu = FloatField('PCU')
    comments = TextAreaField('Comments')

    submit = SubmitField('Reject')
    cancel = SubmitField('Cancel')

class CSVUplodForm(FlaskForm):
    file = FileField('CSV File', validators=[FileRequired('no file!')])
    submit = SubmitField('Submit')