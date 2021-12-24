from datetime import datetime
from flask import render_template, abort, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EmptyForm, TaskForm, MessageForm
from app.models import User, Task
from app.main import main


@main.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
@login_required
def index():    
    return render_template('index.html', title='Home')

# add admin dashboard view
@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # prevent non-admins from accessing the page
    if not current_user.is_administrator():
        abort(403)

    return render_template('admin_dashboard.html', title="Dashboard")