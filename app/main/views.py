from datetime import datetime
from flask import render_template, abort, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app import db
from app.main.forms import CaseForm, RejectCaseForm, UpdateCaseForm
from app.models import Case, CaseStatus, User
from app.main import main


@main.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_administrator():
        abort(403)

def go_to_admin_page():
    if current_user.is_administrator():
        return redirect(url_for('main.admin_list_users'))


def get_next_page():
    next_url = ''
    if current_user.is_administrator():
        next_url =  'user.list_users'
    if current_user.is_assignee():
        next_url = ('main.workflow_list_case')
    if current_user.is_pathologist():
        next_url = ('main.workflow_assigned_cases')
    if current_user.is_supervisor():
        next_url = 'main.workflow_list_rejected_cases'
        
    return next_url

@main.route('/', methods=['GET'])
@main.route('/index', methods=['GET'])
@login_required
def index():
    redirect_url = get_next_page() 
    print(redirect_url)
    return redirect(url_for(redirect_url))

def fill_operator_list():
    choices = [(0, "")]
    for g in User.query.filter(User.role.has(name='Pathologist')).order_by('name'):
        choices.append((g.id, g.name)) 
    return choices

@main.route('/workflow/list_case', methods=['GET'])
@login_required
def workflow_list_case():
    # cases = Case.query.filter(Case.assignee_id == current_user.id)  
    cases = Case.query.all()     
    return render_template('workflow_list_case.html', title='Home', cases = cases)

@main.route('/workflow/assigned_cases', methods=['GET'])
@login_required
def workflow_assigned_cases():
    cases = Case.query.filter(Case.operator_id == current_user.id)     
    return render_template('workflow_assigned_cases.html', title='Home', cases = cases)

@main.route('/workflow/accept_case/<int:id>', methods=['GET', 'POST'])
@login_required
def workflow_accept_case(id):
    accepted_case = Case.query.get_or_404(id)
    accepted_case.status = CaseStatus.Accepted
    db.session.commit()   
    return redirect(url_for('main.workflow_assigned_cases'))

@main.route('/workflow/reject_case/<int:id>', methods=['GET', 'POST'])
@login_required
def workflow_reject_case(id):
    rejected_case = Case.query.get_or_404(id)
    form = RejectCaseForm()
    if form.validate_on_submit():
        rejected_case.status = CaseStatus.Rejected
        rejected_case.description = form.description.data
        db.session.commit() 
        return redirect(url_for('main.workflow_assigned_cases'))

    form.name.data = rejected_case.name
    form.description.data = rejected_case.description
    return render_template('workflow_reject_case.html', title='Reject', form=form)

@main.route('/workflow/list_rejected_cases', methods=['GET'])
@login_required
def workflow_list_rejected_cases():
    cases = Case.query.filter(Case.status == CaseStatus.Rejected)     
    return render_template('workflow_list_rejected_cases.html', title='Home', cases = cases)

@main.route('/workflow/approve_case/<int:id>', methods=['GET', 'POST'])
@login_required
def workflow_approve_case(id):
    accepted_case = Case.query.get_or_404(id)
    accepted_case.status = CaseStatus.Approved
    db.session.commit() 
    return redirect(url_for('main.workflow_list_rejected_cases'))

@main.route('/workflow/update_approve_case/<int:id>', methods=['GET', 'POST'])
@login_required
def workflow_update_approve_case(id):
    rejected_case = Case.query.get_or_404(id)
    form = RejectCaseForm()
    if form.validate_on_submit():
        rejected_case.status = CaseStatus.Rejected
        rejected_case.description = form.description.data
        db.session.commit() 
        return redirect(url_for('main.workflow_list_rejected_cases'))

    form.name.data = rejected_case.name
    form.description.data = rejected_case.description
    return render_template('workflow_update_approve_case.html', title='Reject', form=form)

@main.route('/workflow/add_case', methods=['GET', 'POST'])
@login_required
def workflow_add_case():
    go_to_admin_page()
    form = CaseForm()
    
    choices = fill_operator_list()
    form.operator.choices=choices
    form.operator.default = 0
    
    if form.validate_on_submit():

        case =Case(name = form.name.data,
                    description = form.description.data,
                    status = CaseStatus.Created,
                    assignee_id = current_user.id,
                    operator_id = form.operator.data
        )
        db.session.add(case)
        db.session.commit()

        flash('A new case has been added!')
        return redirect(url_for('main.index'))

    
    return render_template('workflow_add_case.html', title='Add Case', form = form)

@main.route('/workflow/delete_case/<int:id>', methods=['GET', 'POST'])
@login_required
def workflow_delete_case(id):
    """
    Delete a case from the database
    """
    go_to_admin_page()

    case = Case.query.get_or_404(id)
    db.session.delete(case)
    db.session.commit()
    flash('You have successfully deleted a case.')

    # redirect to the departments page
    return redirect(url_for('main.index'))

@main.route('/workflow/edit_case/<int:id>', methods=['GET', 'POST'])
@login_required
def workflow_edit_case(id):
    """
    Edit a case
    """
    go_to_admin_page()
    case = Case.query.get_or_404(id)
    form = UpdateCaseForm()
    choices = fill_operator_list()
    form.operator.choices = choices

    if form.validate_on_submit():
        case.name = form.name.data
        case.description = form.description.data
        case.operator_id = form.operator.data

        db.session.commit()
        flash('You have successfully edited the case.')

        # redirect to the departments page
        return redirect(url_for('main.index'))
    
    form.operator.default = case.operator_id
    form.process()
    form.name.data = case.name
    form.description.data = case.description

    return render_template('workflow_edit_case.html',  form=form, title="Edit Case")

