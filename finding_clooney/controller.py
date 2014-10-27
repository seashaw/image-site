"""
File: controller.py
Authors: 
    2014-10-10 - C.Shaw
Description: Routing for web application, generates views using templates,
             and handles logic for user interaction.
"""

import hashlib
from datetime import datetime
import pytz
from pytz import timezone

from . import app, bc, dbh, mail, db, EditBlogPostPermission
from . model import User, Post
from . forms import LoginForm, RegisterForm, EditPostForm

from flask import (Flask, render_template, jsonify, request, redirect,
        url_for, flash, current_app, session)
from flask.ext.login import login_required, login_user, logout_user, current_user
from flask.ext.mail import Message
from flask.ext.principal import (Identity, AnonymousIdentity, identity_changed,
        Permission, RoleNeed)
from flask.ext.admin import BaseView, expose

"""
Routing functions, controller logic, view redirection.
"""

@app.route("/")
@app.route("/index")
@login_required
def index():
    """
    Greeter page containing information about web application.
    Should link to user registration and login.
    """
    posts = Post.query.order_by(Post.id).all()
    return render_template("index.html", posts=posts)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Feed form data into User object creation.
        user = User(form.email.data,
                bc.generate_password_hash(form.password.data, rounds=12),
                False, form.first_name.data, form.last_name.data, 
                form.user_name.data, [])
        # Try to insert new user into database.
        if dbh.insertUser(user):
            # URL for user confirmation.
            confirm_url = url_for("confirmUser", user_email=user.email,
                    id_hash=hashlib.sha1(str(user.id).encode()).hexdigest(),
                    _external=True)
            # Create and send confirmation email.
            subject = "Please confirm your account."
            html = "Click <a href='{}'>here</a> to confirm.".format(confirm_url)
            msg = Message(subject=subject, recipients=[user.email], html=html)
            mail.send(msg)
            flash("Confirmation email sent.")
            return redirect(request.args.get("next") or url_for("login"))
        else:
            flash("Registration failed.")
            return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/confirm/<user_email>/<id_hash>")
def confirmUser(user_email, id_hash):
    """
    Confirms user account.
    """
    user = User.query.filter_by(email=user_email).first()
    if hashlib.sha1(str(user.id).encode()).hexdigest() != id_hash:
        return abort(404)
    else:
        if user.confirmed_at is None:
            user.confirmed_at = datetime.utcnow()
            user.active = True
            db.session.commit()
            flash("Account confirmation successful.")
        else:
            flash("Account already confirmed.")
    return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash('No account for "{}'.format(email))
            return redirect(url_for("login"))
        elif not user.confirmed_at:
            flash("Account requires confirmation.")
            return redirect(url_for("login"))
        else: 
            if bc.check_password_hash(user.password, form.password.data):
                login_user(user)

                # Signal Principal that identity changed.
                identity_changed.send(current_app._get_current_object(),
                        identity=Identity(user.id))

                flash("Login successful.")
                return redirect(request.args.get("next") or url_for("index"))
            else:
                flash("Wrong password.")
                return redirect(url_for("login"))
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    """
    Exit point for logged in users.
    """
    logout_user()

    # Remove session keys set by Principal.
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    
    # Signal Principal that identity changed.
    identity_changed.send(current_app._get_current_object(),
            identity=AnonymousIdentity())

    flash("Logout successful.")
    return redirect(url_for("login"))

@app.route('/users/<user_name>')
@login_required
def viewProfile(user_name):
    """
    Display user information and profile.
    """
    user = User.query.filter_by(user_name=user_name).first()
    return render_template('view-profile.html', user=user)

@app.route('/create', methods=["GET", "POST"])
@login_required
def createPost():
    """
    Creating and posting new blog posts.
    """
    form = EditPostForm()
    if form.validate_on_submit():
        # Feed form data into post object.
        post = Post(form.title.data, form.subtitle.data, form.body.data,
                datetime.utcnow(), current_user.id)
        # Add new post object to database.
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create-post.html', form=form)

@app.route('/edit/<post_id>', methods=["GET", "POST"])
@login_required
def editPost(post_id):
    """
    Editing existing posts.
    """
    permission = EditBlogPostPermission(post_id)
    if permission.can():
        form = EditPostForm()
        post = Post.query.get(post_id)
        if form.title.data is None:
            form.title.data = post.title
            form.subtitle.data = post.subtitle
            form.body.data = post.body
        if form.validate_on_submit():
            form.populate_obj(post)
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('edit-post.html', form=form, post_id=post.id)
    else:
        flash('You lack editing rights.')
        return redirect(url_for('index'))

@app.route('/post/<post_id>', methods=["GET", "POST"])
@login_required
def viewPost(post_id):
    """
    Viewing an individual post.
    """
    post = Post.query.get(post_id)
    return render_template('view-post.html', post=post)

@app.route("/_add-numbers")
def addNumbers():
    """
    Sums two GET request variables and returns result.
    """
    a = request.args.get("a", 0, type=int)
    b = request.args.get("b", 0, type=int)
    return jsonify(sum=a+b)

@app.route("/view-users")
@login_required
def viewUsers():
    """
    Displays list of usernames.
    """
    admin_permission = Permission(RoleNeed('Administrator'))
    if admin_permission.can():
        return render_template("view-users.html", users=dbh.fetchAllUserNames())
    else:
        flash('You lack admin rights.')
        return redirect(url_for('index'))

class EditPostView(BaseView):
    """
    Admin view for editing blog posts.
    """

    def is_accessible(self):
        """
        Restrict access to authenticated users.
        """
        admin_permission = Permission(RoleNeed('Administrator'))
        return admin_permission.can()

    @expose('/')
    def index(self):
        """
        Renders administrative edit page.
        """
        return self.render('editpost.html')
