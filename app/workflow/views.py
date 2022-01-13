from os import abort
from flask import jsonify, flash, request, current_app
from flask.helpers import url_for
from flask.templating import render_template
from flask_login.utils import login_required, current_user
from flask_sqlalchemy import Pagination
from werkzeug.utils import redirect
import pandas as pd

from sqlalchemy.exc import SQLAlchemyError

from app import db
import app
from app.models import Case, CaseStatus, PCU_Lookup, User
from app.workflow.forms import CSVUplodForm, CaseForm, RejectCaseForm, UpdateCaseForm
from app.workflow import workflow

def paginate(obj=None, page=None, per_page=None, error_out=True, max_per_page=None, count=True):
        """:param obj: Query Object E.g User.query"""
        if obj:
            if request:
                if page is None:
                    try:
                        page = int(request.args.get('page', 1))
                    except (TypeError, ValueError):
                        if error_out:
                            abort(404)
                        page = 1
                if per_page is None:
                    try:
                        per_page = int(request.args.get('per_page', 20))
                    except (TypeError, ValueError):
                        if error_out:
                            abort(404)
                        per_page = 20
            else:
                if page is None:
                    page = 1
                if per_page is None:
                    per_page = 20
            if max_per_page is not None:
                per_page = min(per_page, max_per_page)
            if page < 1:
                if error_out:
                    abort(404)
                else:
                    page = 1
            if per_page < 0:
                if error_out:
                    abort(404)
                else:
                    per_page = 20

            items = obj.limit(per_page).offset((page - 1) * per_page).all()
            if not items and page != 1 :
                page = page - 1
                items = obj.limit(per_page).offset((page - 1) * per_page).all()
                
            if not items and page ==1:
                return None
            # if not items and page != 1 and error_out:
            #     abort(404)
            if not count:
                total = None
            elif page == 1 and len(items) < per_page:
                total = len(items)
            else:
                total = obj.order_by(None).count()
            return Pagination(obj, page, per_page, total, items)
        return None

@workflow.route('/list_case', methods=['GET'])
@login_required
def list_case():
    # cases = Case.query.filter(Case.assignee_id == current_user.id)  
    # cases = Case.query.filter( (Case.status=='Created') | (Case.status=='Assigned')).all()  
    p = db.session.query(Case.operator_id.label('operator_id'), db.func.sum(Case.PCU).label('total_pcu')
        ).filter(Case.status == 'Assigned').group_by(Case.operator_id).cte('p')

    cases_query = db.session.query(
        Case.id.label('id'),
        Case.cp_num.label('cp_num'),
        Case.specimen_class.label('specimen_class')  ,
        Case.part_type.label('part_type'),
        Case.group_external_value.label('group_external_value'),
        Case.part_description.label('part_description'),
        Case.block_count.label('block_count'),
        Case.doctor_code.label('doctor_code'),
        Case.specialty.label('specialty'),
        Case.location.label('location'),
        Case.PCU.label('PCU'),
        Case.status.label('status'),
        User.username.label('operator_name'),
        p.c.total_pcu.label('total_pcu') 
    ).select_from(Case).outerjoin(p, p.c.operator_id==Case.operator_id).outerjoin(
        User, Case.operator_id==User.id).filter(
            (Case.status=='Created') | (Case.status=='Assigned'))

    cases_page = paginate(cases_query, None, current_app.config['PATHOSTREAM_CASES_PER_PAGE'])

    if cases_page:
        next_url = url_for('workflow.list_case', page=cases_page.next_num ) \
            if cases_page.has_next else None
        prev_url = url_for('workflow.list_case', page=cases_page.prev_num) \
            if cases_page.has_prev else None
        
        return render_template('workflow/list_case.html', title='Home', cases = cases_page.items, next_url=next_url,
                            prev_url=prev_url, return_page = cases_page.page)

    else:
        return render_template('workflow/list_case.html', title='Home', cases = None, next_url=None,
                            prev_url=None, return_page = None)


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
        if form.cancel.data:  # if cancel button is clicked, the form.cancel.data will be True
            return redirect(url_for('workflow.list_rejected_cases'))
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
        if form.cancel.data:  # if cancel button is clicked, the form.cancel.data will be True
            return redirect(url_for('workflow.list_case'))
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
        # get total PCU that have been assigned to the pathologist
        pcu = 0.0
        try:
            pcu = db.session.query(db.func.sum(Case.PCU)).filter(
                Case.operator_id == g.id).filter(
                    Case.status == 'Assigned').scalar() or 0 
        except SQLAlchemyError:
            pcu = 0.0
        
        choices.append((g.id, g.name + '(' + str(pcu) + ')' )) 
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
        if form.cancel.data:  # if cancel button is clicked, the form.cancel.data will be True
            return redirect(url_for('workflow.list_case'))
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

@workflow.route('/delete_case', methods=['GET', 'POST'])
@login_required
def delete_case():
    """
    Delete a case from the database
    """
    id = request.args.get('id')
    page = request.args.get('page')
    print(page)
    case = Case.query.get_or_404(id)
    db.session.delete(case)
    db.session.commit()
    flash('You have successfully deleted a case.')

    # redirect to the departments page
    return redirect(url_for('workflow.list_case', page=page))

@workflow.route('/edit_case', methods=['GET', 'POST'])
@login_required
def edit_case():
    """
    Edit a case
    """
    id = request.args.get('id')
    page = request.args.get('page')
    print(page)
    case = Case.query.get_or_404(id)
    form = UpdateCaseForm()
    choices = fill_operator_list()
    form.operator.choices = choices

    if form.validate_on_submit():
        if form.cancel.data:  # if cancel button is clicked, the form.cancel.data will be True
            return redirect(url_for('workflow.list_case', page=page))
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
        return redirect(url_for('workflow.list_case', page=page))
    
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
        if form.cancel.data:  # if cancel button is clicked, the form.cancel.data will be True
            return redirect(url_for('workflow.list_case'))
        filestream = form.file.data
        # filename = secure_filename(filestream.filename)
        df = pd.read_csv( filestream )
        df = df.fillna('')
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