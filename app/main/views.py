from datetime import datetime
from os import name
from flask import render_template, abort, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from wtforms.fields import choices
from app import db
from app.auth.forms import RegistrationForm, UserUpdateForm
from app.main.forms import CaseForm, EmptyForm, MessageForm, RejectCaseForm, UpdateCaseForm
from app.models import Case, CaseStatus, Role, User, Task
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
        next_url =  'main.admin_list_users'
    if current_user.is_assignee():
        next_url = ('main.workflow_list_case')
    if current_user.is_pathologist():
        next_url = ('main.workflow_assigned_cases')
    if current_user.is_supervisor():
        next_url = 'main.workflow_list_case'
        
    return next_url

@main.route('/', methods=['GET'])
@main.route('/index', methods=['GET'])
@login_required
def index():
    redirect_url = get_next_page() 
    return redirect(url_for(redirect_url))

def fill_operator_list():
    choices = [(0, "")]
    for g in User.query.filter(User.role.has(name='Pathologist')).order_by('name'):
        choices.append((g.id, g.name)) 
    return choices

@main.route('/workflow/list_case', methods=['GET'])
@login_required
def workflow_list_case():
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

def fill_role_list():
    choices = []
    for g in Role.query.order_by('name'):
        choices.append((g.id, g.name)) 
    return choices

# add admin dashboard view
@main.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    # prevent non-admins from accessing the page
    check_admin()
    form = RegistrationForm()
    choices = fill_role_list()
    form.role.choices = choices

    if form.validate_on_submit():
        user =User(email = form.email.data,
                    username = form.username.data,
                    role_id = form.role.data,
                    password = form.password.data,
                    name=form.fullname.data,
                    location=form.location.data
        )

        db.session.add(user)
        db.session.commit()
        flash('A new user has been added!')
        return redirect(url_for('main.admin_list_users'))

    return render_template('admin_add_user.html', title="Add User", form=form)

@main.route('/admin/list_users', methods=['GET'])
@login_required
def admin_list_users():
    check_admin()
    users = User.query.all()
    return render_template('admin_list_users.html', title='List Users', users=users)

@main.route('/admin/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_delete_user(id):
    """
    Delete a user from the database
    """
    check_admin()
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('You have successfully deleted a user.')

    # redirect to the departments page
    return redirect(url_for('main.admin_list_users'))

@main.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(id):
    """
    Edit a user
    """
    check_admin()
    user = User.query.get_or_404(id)
    form = UserUpdateForm()
    choices = fill_role_list()
    form.role.choices = choices

    if form.validate_on_submit():
        user.name = form.fullname.data
        user.username = form.username.data
        user.email = form.email.data
        user.location = form.location.data
        if (form.password.data != ''):
            user.password = form.password.data

        user.role_id = form.role.data
        db.session.commit()
        flash('You have successfully edited the User.')

        # redirect to the departments page
        return redirect(url_for('main.admin_list_users'))
    form.role.default = user.role_id
    form.process()
    form.username.data = user.username
    form.fullname.data = user.name
    form.email.data = user.email
    form.location.data = user.location
    form.password.data = ''
    return render_template('admin_edit_user.html',  form=form, title="Edit User")