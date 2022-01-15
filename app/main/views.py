from datetime import datetime
from flask import abort, redirect, url_for
from flask_login import current_user, login_required
from app import db
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
        return redirect(url_for('user.list_users'))


def get_next_page():
    next_url = ''
    if current_user.is_administrator():
        next_url =  'user.list_users'
    if current_user.is_assignee():
        next_url = ('workflow.list_case')
    if current_user.is_pathologist():
        next_url = ('workflow.list_assigned_cases')
    if current_user.is_supervisor():
        next_url = 'workflow.list_rejected_cases'
        
    return next_url

@main.route('/', methods=['GET'])
@main.route('/index', methods=['GET'])
@login_required
def index():
    redirect_url = get_next_page() 
    print(redirect_url)
    return redirect(url_for(redirect_url))


