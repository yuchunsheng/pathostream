from flask import jsonify, flash
from flask.helpers import url_for
from flask.templating import render_template
from flask_login.utils import login_required, current_user
from werkzeug.utils import redirect
import pandas as pd

from app import db
from app.models import Case, CaseStatus, PCU_Lookup, User
from app.workflow.forms import CSVUplodForm, CaseForm, RejectCaseForm, UpdateCaseForm
from app.workflow import workflow


@workflow.route('/list_case', methods=['GET'])
@login_required
def list_case():
    # cases = Case.query.filter(Case.assignee_id == current_user.id)  
    cases = Case.query.all()     
    return render_template('workflow/list_case.html', title='Home', cases = cases)

@workflow.route('/assigned_cases', methods=['GET'])
@login_required
def assigned_cases():
    cases = Case.query.filter(Case.operator_id == current_user.id)     
    return render_template('workflow/assigned_cases.html', title='Home', cases = cases)

@workflow.route('/accept_case/<int:id>', methods=['GET', 'POST'])
@login_required
def accept_case(id):
    accepted_case = Case.query.get_or_404(id)
    accepted_case.status = CaseStatus.Accepted
    db.session.commit()   
    return redirect(url_for('workflow.assigned_cases'))

@workflow.route('/reject_case/<int:id>', methods=['GET', 'POST'])
@login_required
def reject_case(id):
    rejected_case = Case.query.get_or_404(id)
    form = RejectCaseForm()
    if form.validate_on_submit():
        rejected_case.status = CaseStatus.Rejected
        print(form.pcu.data)
        rejected_case.PCU = form.pcu.data

        db.session.commit() 
        return redirect(url_for('workflow.assigned_cases'))

    form.cp_num.data=rejected_case.cp_num
    form.specimen_class.data=rejected_case.specimen_class
    form.part_type.data=rejected_case.part_type
    form.group_external_value.data=rejected_case.group_external_value
    form.part_description.data=rejected_case.part_description
    form.block_count.data= rejected_case.block_count
    form.doctor_code.data=rejected_case.doctor_code
    form.specialty.data=rejected_case.specialty
    form.location.data=rejected_case.location
    form.pcu.data=rejected_case.PCU

    return render_template('workflow/reject_case.html', title='Reject', form=form)

@workflow.route('/list_rejected_cases', methods=['GET'])
@login_required
def list_rejected_cases():
    cases = Case.query.filter(Case.status == CaseStatus.Rejected)     
    return render_template('workflow/list_rejected_cases.html', title='Home', cases = cases)

@workflow.route('/approve_case/<int:id>', methods=['GET', 'POST'])
@login_required
def approve_case(id):
    accepted_case = Case.query.get_or_404(id)
    accepted_case.status = CaseStatus.Approved
    db.session.commit() 
    return redirect(url_for('workflow.list_rejected_cases'))

@workflow.route('/update_approve_case/<int:id>', methods=['GET', 'POST'])
@login_required
def update_approve_case(id):
    rejected_case = Case.query.get_or_404(id)
    form = RejectCaseForm()
    if form.validate_on_submit():
        rejected_case.status = CaseStatus.Rejected
        rejected_case.PCU = form.pcu.data
        db.session.commit() 
        return redirect(url_for('workflow.list_rejected_cases'))

    form.cp_num.data=rejected_case.cp_num
    form.specimen_class.data=rejected_case.specimen_class
    form.part_type.data=rejected_case.part_type
    form.group_external_value.data=rejected_case.group_external_value
    form.part_description.data=rejected_case.part_description
    form.block_count.data= rejected_case.block_count
    form.doctor_code.data=rejected_case.doctor_code
    form.specialty.data=rejected_case.specialty
    form.location.data=rejected_case.location
    form.pcu.data=rejected_case.PCU

    return render_template('workflow/update_approve_case.html', title='Reject', form=form)

def fill_operator_list():
    choices = [(0, "")]
    for g in User.query.filter(User.role.has(name='Pathologist')).order_by('name'):
        choices.append((g.id, g.name)) 
    return choices

@workflow.route('/get_pcu/<part_type>', methods=['GET'])
@login_required
def get_pcu(part_type):
    # print(part_type)
    pcu_lookup = PCU_Lookup.query.filter_by(part_type = part_type).first()
    return jsonify({"message": pcu_lookup.new_jk_pcu})
        
@workflow.route('/add_case', methods=['GET', 'POST'])
@login_required
def add_case():
    form = CaseForm()
    
    choices = fill_operator_list()
    form.operator.choices=choices
    form.operator.default = 0
    
    if form.validate_on_submit():
        status = CaseStatus.Created
        if form.operator.data !='':
            status = CaseStatus.Assigned
        case =Case(cp_num=form.cp_num.data,
                    specimen_class=form.specimen_class.data,
                    part_type=form.part_type.data,
                    group_external_value=form.group_external_value.data,
                    part_description=form.part_description.data,
                    block_count=form.block_count.data,
                    doctor_code=form.doctor_code.data,
                    specialty=form.specialty.data,
                    location=form.location.data,
                    PCU=form.pcu.data,
                    status = status,
                    assignee_id = current_user.id,
                    operator_id = form.operator.data
        )
        db.session.add(case)
        db.session.commit()

        flash('A new case has been added!')
        return redirect(url_for('main.index'))

    
    return render_template('workflow/add_case.html', title='Add Case', form = form)

@workflow.route('/delete_case/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_case(id):
    """
    Delete a case from the database
    """
    case = Case.query.get_or_404(id)
    db.session.delete(case)
    db.session.commit()
    flash('You have successfully deleted a case.')

    # redirect to the departments page
    return redirect(url_for('main.index'))

@workflow.route('/edit_case/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_case(id):
    """
    Edit a case
    """
    case = Case.query.get_or_404(id)
    form = UpdateCaseForm()
    choices = fill_operator_list()
    form.operator.choices = choices

    if form.validate_on_submit():
        status = CaseStatus.Created
        if form.operator.data != '':
            status = CaseStatus.Assigned

        case.cp_num=form.cp_num.data
        case.specimen_class=form.specimen_class.data
        case.part_type=form.part_type.data
        case.group_external_value=form.group_external_value.data
        case.part_description=form.part_description.data
        case.block_count=form.block_count.data
        case.doctor_code=form.doctor_code.data
        case.specialty=form.specialty.data
        case.location=form.location.data
        case.PCU=form.pcu.data
        case.status = status
        case.assignee_id = current_user.id
        case.operator_id = form.operator.data

        db.session.commit()
        flash('You have successfully edited the case.')

        # redirect to the departments page
        return redirect(url_for('main.index'))
    
    form.operator.default = case.operator_id
    form.process()
    form.cp_num.data=case.cp_num
    
    form.specimen_class.data=case.specimen_class
    form.part_type.data=case.part_type
    form.group_external_value.data=case.group_external_value
    form.part_description.data=case.part_description
    form.block_count.data= case.block_count
    form.doctor_code.data=case.doctor_code
    form.specialty.data=case.specialty
    form.location.data=case.location
    form.pcu.data=case.PCU

    return render_template('workflow/edit_case.html',  form=form, title="Edit Case")

@workflow.route('/upload_csv', methods=['GET', 'POST'])
@login_required
def upload_csv():
    form = CSVUplodForm()

    if form.validate_on_submit():
        filestream = form.file.data
        # filename = secure_filename(filestream.filename)
        df = pd.read_csv( filestream )
        df = df.fillna('')
        df = df.iloc[5:10]
        cases = []
        for index, row in df.iterrows():
            # print(row['CP_NUM'], row['PartType'], row['Group'], row['Location'])
            new_part_type = row['PartType']
            pcu_value = 0.0
            new_pcu_lookup = PCU_Lookup.query.filter(PCU_Lookup.part_type == new_part_type).first()
            if (new_pcu_lookup is not None):
                pcu_value = new_pcu_lookup.new_jk_pcu

            new_case = Case(
                cp_num=row['CP_NUM'],
                specimen_class=row['SpecimenClass'],
                part_type=row['PartType'],
                group_external_value=row['Group'],
                part_description=row['PartDescription'],
                block_count=row['BlockCount'],
                doctor_code=row['DoctorCode'],
                specialty=row['Specialty'],
                location=row['Location'],
                PCU=pcu_value,
                status = CaseStatus.Created,
                assignee_id = current_user.id

            )
            cases.append(new_case)

        print(len(cases))
        db.session.add_all(cases)
        db.session.commit()

        return redirect(url_for('main.index'))
    
    return render_template('workflow/upload_csv.html', title='Upload CSV', form=form)