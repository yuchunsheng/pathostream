
from flask import render_template, abort, flash, redirect, url_for
from flask_login.utils import login_required
from app import user
from app.main.views import check_admin
from app.models import Role, User
from app.user.forms import RegistrationForm, UserUpdateForm
from app import db
from app.user import user


def fill_role_list():
    choices = []
    for r in Role.query.order_by('name'):
        choices.append((r.id, r.name)) 
    return choices

# add admin dashboard view
@user.route('/user/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
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
        return redirect(url_for('user.list_users'))

    return render_template('user/add_user.html', title="Add User", form=form)

@user.route('/user/list_users', methods=['GET'])
@login_required
def list_users():
    check_admin()
    users = User.query.all()
    return render_template('user/list_users.html', title='List Users', users=users)

@user.route('/user/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    """
    Delete a user from the database
    """
    check_admin()
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('You have successfully deleted a user.')

    # redirect to the departments page
    return redirect(url_for('user.list_users'))

@user.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
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
        return redirect(url_for('user.list_users'))
    form.role.default = user.role_id
    form.process()
    form.username.data = user.username
    form.fullname.data = user.name
    form.email.data = user.email
    form.location.data = user.location
    form.password.data = ''
    return render_template('user/edit_user.html',  form=form, title="Edit User")