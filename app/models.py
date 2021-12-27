from datetime import datetime
import enum
import hashlib
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

import bleach
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from wtforms.validators import Email
from app.exceptions import ValidationError
from . import db, login_manager


class Permission():
    MODIFY_PCU = 1
    CREATE_TASK = 2
    APPROVE_TASK = 4
    ADMIN = 8


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'Assignee': [Permission.CREATE_TASK],
            'Pathologist': [Permission.MODIFY_PCU],
            'Supervisor':[Permission.APPROVE_TASK],
            'Administrator': [Permission.ADMIN],
        }
        default_role = 'Assignee'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return f"<Role {self.name}>"


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    # confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))   

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def is_assignee(self):
        return self.can(Permission.CREATE_TASK)
    def is_pathologist(self):
        return self.can(Permission.MODIFY_PCU)
    def is_supervisor(self):
        return self.can(Permission.APPROVE_TASK)

    @staticmethod
    def insert_admin():
        admin = User(email = 'admin@admin.com',
                    username = 'admin',
                    role_id = 4,
                    password = 'admin123',
                    name='admin',
                    location='admin'
        )
        db.session.add(admin)
        db.session.commit()

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts_url': url_for('api.get_user_posts', id=self.id),
            'followed_posts_url': url_for('api.get_user_followed_posts',
                                          id=self.id),
            'post_count': self.posts.count()
        }
        return json_user

    def __repr__(self):
        return f"<User {self.username}"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class CaseStatus():
    Created = "Created"
    Assigned = 'Assigned'
    Accepted = 'Accepted'
    Rejected = 'Rejected'
    Approved = 'Approved'

class Case(db.Model):
    """
    Create a Case table
    """
    __tablename__ = 'cases'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    description = db.Column(db.String(200))
    status = db.Column(db.String(10))
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assignees = db.relationship('User',  foreign_keys=[assignee_id], backref=backref('assignees'))
    operators = db.relationship('User',  foreign_keys=[operator_id], backref=backref('operators'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    

    def __repr__(self):
        return f"Case:{self.name}"


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            value,
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id),
            'comments_url': url_for('api.get_post_comments', id=self.id),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Task(body=body)


db.event.listen(Task.body, 'set', Task.on_changed_body)
