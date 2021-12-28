from flask_wtf.form import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired


class CaseForm(FlaskForm):
    cp_num = StringField('cp_num', validators=[DataRequired()])
    specimen_class = StringField('specimen_class', validators=[DataRequired()])
    part_type = StringField('part_type', validators=[DataRequired()])
    group_external_value = StringField('group_external_value', validators=[DataRequired()])
    part_description = StringField('part_description', validators=[DataRequired()])
    blcok_count = IntegerField('block_count', validators=[DataRequired()])
    doctor_code = StringField('doctor_code', validators=[DataRequired()])
    specialty = StringField('specialty', validators=[DataRequired()])
    location = StringField('location', validators=[DataRequired()])
    pcu = IntegerField('PCU', validators=[DataRequired()])
    operator=SelectField('pathologist')

    submit = SubmitField('Submit')

class UpdateCaseForm(FlaskForm):
    cp_num = StringField('cp_num', validators=[DataRequired()])
    specimen_class = StringField('specimen_class', validators=[DataRequired()])
    part_type = StringField('part_type', validators=[DataRequired()])
    group_external_value = StringField('group_external_value', validators=[DataRequired()])
    part_description = StringField('part_description', validators=[DataRequired()])
    blcok_count = IntegerField('block_count', validators=[DataRequired()])
    doctor_code = StringField('doctor_code', validators=[DataRequired()])
    specialty = StringField('specialty', validators=[DataRequired()])
    location = StringField('location', validators=[DataRequired()])
    pcu = IntegerField('PCU', validators=[DataRequired()])
    operator=SelectField('pathologist')
    submit = SubmitField('Update')

class RejectCaseForm(FlaskForm):
    cp_num = StringField('cp_num', validators=[DataRequired()])
    specimen_class = StringField('specimen_class', validators=[DataRequired()])
    part_type = StringField('part_type', validators=[DataRequired()])
    group_external_value = StringField('group_external_value', validators=[DataRequired()])
    part_description = StringField('part_description', validators=[DataRequired()])
    blcok_count = IntegerField('block_count', validators=[DataRequired()])
    doctor_code = StringField('doctor_code', validators=[DataRequired()])
    specialty = StringField('specialty', validators=[DataRequired()])
    location = StringField('location', validators=[DataRequired()])
    pcu = IntegerField('PCU', validators=[DataRequired()])


    submit = SubmitField('Reject')

