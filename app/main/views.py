from datetime import datetime
from os import name
from flask import render_template, abort, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from wtforms.fields import choices
from app import db
from app.auth.forms import RegistrationForm, UserUpdateForm
from app.main.forms import CaseForm, EmptyForm, MessageForm, UpdateCaseForm
from app.models import Case, Role, User, Task
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

@main.route('/', methods=['GET'])
@main.route('/index', methods=['GET'])
@login_required
def index():
    go_to_admin_page()
    cases = Case.query.all()     
    return render_template('workflow_list_case.html', title='Home', cases = cases)

def fill_operator_list():
    choices = [(0, "")]
    for g in User.query.filter(User.role.has(name='Administrator')).order_by('name'):
        choices.append((g.id, g.name)) 

    return choices

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
                    status = 'Created',
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

# add admin dashboard view
@main.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    # prevent non-admins from accessing the page
    check_admin()
    form = RegistrationForm()
    if form.validate_on_submit():
        role_id =  Role.query.filter_by(name=form.role.data).first().id
        user =User(email = form.email.data,
                    username = form.username.data,
                    role_id = role_id,
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
    if form.validate_on_submit():
        user.name = form.fullname.data
        # user.username = form.username.data
        user.email = form.email.data
        user.location = form.location.data
        if (form.password.data != ''):
            user.password = form.password.data
        role_id = Role.query.filter_by(name=form.role.data).first().id
        print(role_id)
        user.role_id = role_id
        db.session.commit()
        flash('You have successfully edited the department.')

        # redirect to the departments page
        return redirect(url_for('main.admin_list_users'))

    form.username.data = user.username
    form.fullname.data = user.name
    form.email.data = user.email
    form.location.data = user.location
    form.role.data = user.role.name
    form.password.data = ''
    return render_template('admin_edit_user.html',  form=form, title="Edit User")