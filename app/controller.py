"""
File: controller.py
Authors: 
    2014-11-14 - C.Shaw <shaw.colin@gmail.com>
Description:
    Routing for web application, generates views using templates,
    and handles logic for user interaction.
"""

import os
from werkzeug import secure_filename
import hashlib
from datetime import datetime
import pytz
from pytz import timezone

from . import app, bc, mail, db, EditBlogPostPermission
from .model import User, Post, Picture
from .forms import LoginForm, RegisterForm, EditPostForm, UploadForm

from flask import (Flask, render_template, jsonify, request, redirect,
        url_for, flash, current_app, session)
from flask.ext.login import (login_required, login_user, logout_user,
        current_user)
from flask.ext.mail import Message
from flask.ext.principal import (Identity, AnonymousIdentity, identity_changed,
        Permission, RoleNeed)
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import expose, BaseView

def idHash(id):
    """
    Creates hash from user id.
    """
    return hashlib.sha1(str(id).encode()).hexdigest()

def allowedFile(file_name):
    """
    Checks file name for allowed extension.
    """

    # Set of allowed file extensions.
    extensions = set(["png", "jpg", "jpeg", "gif"])

    # Split file_name from the right at period, check if in extensions set, 
    # and return.
    return "." in file_name and file_name.rsplit(".", 1)[1] in extensions


"""
Routing functions, controller logic, view redirection.
"""

@app.route("/")
@app.route("/index")
def index():
    """
    Greeter page containing information about web application.
    Should link to user registration and login.
    """
    posts = db.session.query(Post, User).join(User).order_by(Post.id).all()
    return render_template("index.html", posts=posts)

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Create and set up new user.
    """
    form = RegisterForm()
    if form.validate_on_submit():
        # Feed form data into User object creation.
        user = User(form.email.data,
                bc.generate_password_hash(form.password.data, rounds=12),
                False, form.first_name.data, form.last_name.data, 
                form.user_name.data, [])
        try:
            # Try to insert new user into database.
            db.session.add(user)
            db.session.commit()
            # URL for user confirmation.
            confirm_url = url_for("confirmUser", user_email=user.email,
                    id_hash=idHash(user.id),
                    _external=True)
            # Create and send confirmation email.
            subject = "Please confirm your account."
            html = "Click <a href='{}'>here</a> to confirm.".format(
                    confirm_url)
            msg = Message(subject=subject, recipients=[user.email], html=html)
            mail.send(msg)
            flash("Confirmation email sent.")
            return redirect(request.args.get("next") or url_for("login"))
        except Exception as e:
            flash("Registration failed.")
            return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/confirm/<user_email>/<id_hash>")
def confirmUser(user_email, id_hash):
    """
    Confirms user account.
    """
    user = User.query.filter_by(email=user_email).first()
    if idHash(user.id) != id_hash:
        return abort(404)
    elif user.confirmed_at is None:
        try:
            os.mkdir(app.config['UPLOAD_FOLDER'].join("/", user.id))
            user.confirmed_at = datetime.utcnow()
            user.active = True
            db.session.commit()
            flash("Account confirmation successful.")
        except Exception as e:
            flash("Account confirmation failed.")
            return redirect(url_for('register'))
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
            flash("No account for '{}'".format(email))
            return redirect(url_for("login"))
        elif not user.confirmed_at:
            flash("confirmation.")
            return redirect(url_for("login"))
        elif not user.active:
            flash("Account is not active, contact support.")
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
    # Log out user.
    logout_user()
    # Remove session keys set by Principal.
    for key in ("identity.name", "identity.auth_type"):
        session.pop(key, None)
    # Signal Principal that identity changed.
    identity_changed.send(current_app._get_current_object(),
            identity=AnonymousIdentity())
    flash("Logout successful.")
    return redirect(url_for("login"))

@app.route('/users/<user_name>')
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
    Create, save, and post new entries.
    """
    form = EditPostForm()
    if form.validate_on_submit():
        # Feed form data into post object.
        post = Post(form.title.data, form.subtitle.data, form.body.data,
                datetime.utcnow(), current_user.id)
        # Add post to session and flush to update post object.
        db.session.add(post)
        db.session.flush()
        # Check submitted form if any files have been loaded.
        if form.pics.data:
            # Generate path for post uploads.
            pic_dest = os.path.join("{}/{}/{}".format(
                    app.config["UPLOAD_FOLDER"], current_user.id, post.id))
            # Create post directory on file system.
            os.mkdir(pic_dest)
            # Get list of upload files.
            pics = request.files.getlist('pics')
            for pic in pics:
                if allowedFile(pic.filename):
                    # Secure file name, save file to system and append file
                    # name to post object pictures list.
                    file_name = secure_filename(pic.filename)
                    pic.save("{}/{}".format(pic_dest, file_name))
                    picture = Picture(file_name)
                    post.pictures.append(picture)
        # Add post object to database.
        try:
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            flash("Post creation failed.")
            return redirect(url_for("createPost"))
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
        flash('You lack editing rights for this post.')
        return redirect(url_for('index'))

@app.route('/view/<post_id>', methods=["GET", "POST"])
def viewPost(post_id):
    """
    View an individual post.
    """
    post = db.session.query(Post, User.user_name).filter_by(
            id=post_id).join(User).first()
    return render_template('view-post.html', post=post)

"""
Administrative views.
"""

class HomeView(BaseView):
    """
    Index view route for administration.
    """
    def is_accessible(self):
        """
        Restrict access to authenticated users.
        """
        admin_permission = Permission(RoleNeed('Administrator'))
        return admin_permission.can()

    @expose('/')
    def index(self):
        return self.render('admin/index.html') # Do I need to create this view?

class UsersView(ModelView):
    """
    Admin view for user management.
    """

    def is_accessible(self):
        """
        Restrict access to authenticated users.
        """
        admin_permission = Permission(RoleNeed('Administrator'))
        return admin_permission.can()

class RolesView(ModelView):
    """
    Admin view for role management.
    """

    def is_accessible(self):
        """
        Restrict access to authenticated users.
        """
        admin_permission = Permission(RoleNeed('Administrator'))
        return admin_permission.can()

class PostsView(ModelView):
    """
    Admin view for post management.
    """

    def is_accessible(self):
        """
        Restrict access to authenticated users.
        """
        admin_permission = Permission(RoleNeed('Administrator'))
        return admin_permission.can()
