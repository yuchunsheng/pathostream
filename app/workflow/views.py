from flask import flash
from flask.helpers import url_for
from flask.templating import render_template
from flask_login.utils import login_required, current_user
from werkzeug.utils import redirect

from app import db
from app.models import Case, CaseStatus, User
from app.workflow.forms import CaseForm, RejectCaseForm, UpdateCaseForm
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
    return redirect(url_for('main.assigned_cases'))

@workflow.route('/reject_case/<int:id>', methods=['GET', 'POST'])
@login_required
def reject_case(id):
    rejected_case = Case.query.get_or_404(id)
    form = RejectCaseForm()
    if form.validate_on_submit():
        rejected_case.status = CaseStatus.Rejected
        rejected_case.description = form.description.data
        db.session.commit() 
        return redirect(url_for('main.assigned_cases'))

    form.name.data = rejected_case.name
    form.description.data = rejected_case.description
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
        rejected_case.description = form.description.data
        db.session.commit() 
        return redirect(url_for('workflow.list_rejected_cases'))

    form.name.data = rejected_case.name
    form.description.data = rejected_case.description
    return render_template('workflow/update_approve_case.html', title='Reject', form=form)

def fill_operator_list():
    choices = [(0, "")]
    for g in User.query.filter(User.role.has(name='Pathologist')).order_by('name'):
        choices.append((g.id, g.name)) 
    return choices
    
@workflow.route('/add_case', methods=['GET', 'POST'])
@login_required
def add_case():
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

    return render_template('workflow/edit_case.html',  form=form, title="Edit Case")

