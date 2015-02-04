"""
File: controller.py
Authors: 
    2014-11-14 - C.Shaw <shaw.colin@gmail.com>
Description:
    Routing for web application, generates views using templates,
    and handles logic for user input.
"""

import os
import uuid
import math
from datetime import datetime
import pytz
from pytz import timezone, utc
from PIL import Image
from werkzeug import secure_filename

from flask import (Flask, render_template, jsonify, request, redirect,
        url_for, flash, current_app, session, abort)
from flask.ext.login import (login_required, login_user, logout_user,
        current_user)
from flask.ext.mail import Message
from flask.ext.principal import Identity, AnonymousIdentity, identity_changed

from . import app, bc, mail, db, EditBlogPostPermission
from .model import User, Post, Picture
from .forms import (LoginForm, RegisterForm, CreatePostForm,  EditPostForm,
        ServiceRequestForm, PasswordResetForm, EditImageDataForm, RadioField)

"""
Helper functions.
"""

def allowedFile(file_name):
    """
    Checks file name for allowed extension.
    """
    # Split file_name from the right at period, check if in extensions set, 
    # and return.
    return "." in file_name and file_name.rsplit(".", 1)[1] in \
            app.config["EXTENSIONS"]


"""
Routing functions, controller logic, view redirection.
"""

@app.route("/", defaults={"page": 1})
@app.route('/index/', defaults={"page": 1})
@app.route("/index/<int:page>")
def index(page):
    """
    Application index, contains list of recent posts.
    """
    # Number of posts per page.
    ppp = 2
    # Get posts for page.
    posts = db.session.query(Post, User).join(User).order_by(
            Post.id.desc()).offset((page-1) * ppp).limit(ppp).all()
    # Get total number of posts and divide into number of pages.
    count = Post.query.count() # Is this the best way to get count?
    pages = math.ceil(count / ppp)
    # Check if end was reached.
    if len(posts) < ppp or page == pages:
        end = True
    else:
        end = False
    return render_template("index.html", posts=posts, page=page, pages=pages,
            end=end)

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Create and set up new user.
    """
    form = RegisterForm()
    if form.validate_on_submit():
        # Feed form data into User object creation.
        user = User(email=form.email.data,
                password=bc.generate_password_hash(form.password.data,
                rounds=12), user_name=form.user_name.data)
        # Generate cryptographic nonce with datetime.
        user.confirm_nonce = uuid.uuid4().hex
        user.confirm_nonce_issued_at = datetime.now(tz=utc)
        try:
            # Add new users to session and commit.
            db.session.add(user)
            db.session.commit()
            # URL for user confirmation.
            confirm_url = url_for("confirmUser", nonce=user.confirm_nonce,
                    _external=True)
            # Create and send confirmation email.
            subject = "Please confirm your account."
            html = "Click <a href='{}'>here</a> to confirm.".format(
                    confirm_url)
            msg = Message(sender=app.config["MAIL_USERNAME"], subject=subject,
                    recipients=[user.email], html=html)
            mail.send(msg)
            flash("Confirmation email sent.", "info")
            return redirect(request.args.get("next") or url_for("login"))
        except Exception as e:
            flash("Registration failed.", "danger")
            return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/confirm/<nonce>")
def confirmUser(nonce):
    """
    Confirms user account.
    """
    user = User.query.filter_by(confirm_nonce=nonce).first()
    if user is None:
        return abort(404)
    else:
        now = datetime.now(tz=utc)
        if (now - user.confirm_nonce_issued_at).days >= 1:
            flash("Confirmation link has expired.", "warning")
        else:
            if user.confirmed_at is None:
                path = "{}/{}".format(app.config['UPLOAD_FOLDER'], user.id)
                os.mkdir(path)
                os.chmod(path, mode=0o777)
                user.confirmed_at = now
                flash("Account confirmation successful.", "success")
            else:
                flash("Account already confirmed.", "warning")
        user.confirm_nonce = None
        user.confirm_nonce_issued_at = None
        db.session.commit()
        return redirect(url_for("login"))

@app.route("/reconfirm", methods=["GET", "POST"])
def reconfirm():
    """
    Allows registered users to request a new confirmation link.
    """
    form = ServiceRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user.confirmed_at:
            # Generate cryptographic nonce with datetime.
            user.confirm_nonce = uuid.uuid4().hex
            user.confirm_nonce_issued_at = datetime.now(tz=utc)
            try:
                db.session.commit()
                # URL for user confirmation.
                confirm_url = url_for("confirmUser", nonce=user.confirm_nonce,
                        _external=True)
                # Create and send confirmation email.
                subject = "Please confirm your account."
                html = "Click <a href='{}'>here</a> to confirm.".format(
                        confirm_url)
                msg = Message(sender=app.config["MAIL_USERNAME"], subject=subject,
                        recipients=[user.email], html=html)
                mail.send(msg)
                flash("Confirmation email sent.", "info")
                return redirect(request.args.get("next") or url_for("login"))
            except Exception as e:
                flash("Confirmation request failed.", "danger")
                return redirect(url_for("login"))
        else:
            flash("Account already confirmed.", "warning")
        return redirect(url_for("login"))
    return render_template("reconfirm.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("No account for '{}'".format(form.email.data), "warning")
            return redirect(url_for("login"))
        elif not user.confirmed_at:
            flash("Account is not yet confirmed.  "
                    "Check your email for a confirmation link.", "warning")
            return redirect(url_for("login"))
        elif user.active is False:
            flash("Account has been deactivated, contact support.", "warning")
            return redirect(url_for("index"))
        else: 
            if bc.check_password_hash(user.password, form.password.data):
                login_user(user)
                # Signal Principal that identity changed.
                identity_changed.send(current_app._get_current_object(),
                        identity=Identity(user.id))
                flash("Login successful.", "success")
                return redirect(request.args.get("next") or url_for("index"))
            else:
                flash("Incorrect email / password.", "warning")
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
    flash("Logout successful.", "success")
    return redirect(url_for("login"))

@app.route("/reset", methods=["GET", "POST"])
def requestReset():
    """
    Endpoint to allow users to request a password reset.
    """
    form = ServiceRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # Generate cryptographic nonce with datetime.
        user.reset_nonce = uuid.uuid4().hex
        user.reset_nonce_issued_at = datetime.now(tz=utc)
        try:
            db.session.commit()
            # URL for user confirmation.
            confirm_url = url_for("passwordReset", nonce=user.reset_nonce,
                    _external=True)
            # Create and send confirmation email.
            subject = "Password reset request."
            html = "Click <a href='{}'>here</a> to reset password.".format(
                    confirm_url)
            msg = Message(sender=app.config["MAIL_USERNAME"], subject=subject,
                    recipients=[user.email], html=html)
            mail.send(msg)
            flash("Check your email for instructions to reset your password.",
                    "info")
            return redirect(request.args.get("next") or url_for("login"))
        except Exception as e:
            flash("Request failed.", "danger")
            return redirect(url_for("login"))
    return render_template("reset-request.html", form=form)

@app.route("/reset/<nonce>", methods=["GET", "POST"])
def passwordReset(nonce):
    """
    Reset password form.
    """
    user = User.query.filter_by(reset_nonce=nonce).first()
    if user is None:
        return abort(404)
    else:
        now = datetime.now(tz=utc)
        if (now - user.reset_nonce_issued_at).days >= 1:
            user.reset_nonce = None
            user.reset_nonce_issued_at = None
            db.session.commit()
            flash("Password reset link has expired.", "warning")
            return redirect(url_for("login"))
        else:
            form = PasswordResetForm()
            if form.validate_on_submit():
                user.password = bc.generate_password_hash(
                        form.password.data, rounds=12)
                user.reset_nonce = None
                user.reset_nonce_issued_at = None
                db.session.commit()
                flash("Password reset successful.  You can now login.",
                        "success")
                return redirect(url_for("login"))
    return render_template("password-reset.html", form=form, nonce=nonce)

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
    form = CreatePostForm()
    if form.validate_on_submit():
        # Feed form data into post object.
        post = Post(form.title.data, form.subtitle.data, form.body.data,
                datetime.now(tz=utc), current_user.id)
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
            os.chmod(pic_dest, mode=0o777)
            # Path and size of thumbnails.
            thumb_dest = "{}/{}".format(pic_dest, "thumbnails")
            thumb_size = (256, 256)
            # Create directory for thumbnails.
            os.mkdir(thumb_dest)
            os.chmod(thumb_dest, mode=0o777)
            # Get list of upload files.
            pics = request.files.getlist('pics')
            if len(pics) > 8:
                flash("Posts cannot have more than 8 pictures.", "warning")
            for pic, count in zip(pics, list(range(8))):
                if allowedFile(pic.filename):
                    # Secure filename and save picture.
                    file_name = secure_filename(pic.filename)
                    pic.save("{}/{}".format(pic_dest, file_name))
                    # Create and save thumbnail.
                    thumb = Image.open("{}/{}".format(pic_dest, file_name))
                    thumb.thumbnail(thumb_size)
                    thumb.save("{}/{}".format(thumb_dest, file_name),
                            thumb.format)
                    # Create Picture model object and add to list in post.
                    picture = Picture(file_name)
                    post.gallery.append(picture)
                    if pic.filename == request.form['choice']:
                        post.cover = picture
        # Commit changes to database.
        try:
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            flash("Post creation failed.", "danger")
            return redirect(url_for("createPost"))
    return render_template('create-post.html', form=form)

@app.route('/edit')
@login_required
def userPosts():
    """
    Lists user posts.
    """
    posts = Post.query.filter_by(user_id=current_user.id).order_by(
            Post.id).all()
    return render_template("user-posts.html", posts=posts)

@app.route('/edit/<post_id>', methods=["GET", "POST"])
@login_required
def editPost(post_id):
    """
    Editing existing posts.
    This whole thing is a horrible, horrible mess... Jesus, Lord have mercy!
    """
    permission = EditBlogPostPermission(post_id)
    if permission.can():
        # Get post object from database.
        post = Post.query.get(post_id)
        # Create new form instance.
        form = EditPostForm()
        if request.method == "GET":
            for pic in post.gallery:
                form.pic_forms.append_entry()
            for p, f in zip(post.gallery, form.pic_forms):
                f.title.data = p.title
            form.title.data = post.title
            form.subtitle.data = post.subtitle
            form.body.data = post.body
        elif request.method == "POST" and form.validate_on_submit():
            # Check to make sure that post will have 8 or less pictures.
            deletes = 0
            for fp in form.pic_forms:
                if fp.delete.data:
                    deletes += 1
            # Get list of uploaded pics, if any.
            uploads = 0
            pics = request.files.getlist('pics')
            uploads = len(pics)
            if uploads == 1:
                if not pics[0].filename:
                    uploads = 0
            if len(post.gallery) + uploads - deletes <= 8:
                # Paths for pictures and thumbnails.
                pic_dest = os.path.join("{}/{}/{}".format(
                        app.config["UPLOAD_FOLDER"], current_user.id, post.id))
                thumb_dest = os.path.join("{}/{}".format(pic_dest,
                        "thumbnails"))
                # Get radio choice value from submitted form.
                choice = request.form['choice']
                # Loop through form fields and gallery pics.
                for fp, pp in zip(form.pic_forms, list(post.gallery)):
                    # If pic selected for deletion.
                    if fp.delete.data:
                        os.remove("{}/{}".format(pic_dest, pp.filename))
                        os.remove("{}/{}".format(thumb_dest, pp.filename))
                        post.gallery.remove(pp)
                        # If deleted pic was post cover, reassign to
                        # first pic in gallery.
                        if pp == post.cover:
                            post.cover = post.gallery[0]
                        # Remove from database and reset form field.
                        db.session.delete(pp)
                        fp.delete.data = False
                    # Or assign new title if post renamed.
                    elif fp.title.data != pp.title:
                        pp.title= fp.title.data
                # Check form for changes and save.
                if post.title != form.title.data:
                    post.title = form.title.data
                if post.subtitle != form.subtitle.data:
                    post.subtitle = form.subtitle.data
                if post.body != form.body.data:
                    post.body = form.body.data
                # Set thumbnail size.
                thumb_size = (256, 256)
                if pics[0].filename:
                    for pic in pics:
                        if allowedFile(pic.filename):
                            # Secure filename and save picture.
                            file_name = secure_filename(pic.filename)
                            pic.save("{}/{}".format(pic_dest, file_name))
                            # Create and save thumbnail.
                            thumb = Image.open("{}/{}".format(pic_dest,
                                    file_name))
                            thumb.thumbnail(thumb_size)
                            thumb.save("{}/{}".format(thumb_dest, file_name),
                                    thumb.format)
                            # Add Picture object to post list.
                            picture = Picture(file_name)
                            post.gallery.append(picture)
                            # Really hacky way of adding form entry... 
                            form.pic_forms.append_entry()
                            last_index = len(form.pic_forms) - 1
                            form.pic_forms[last_index].title.data = \
                                    picture.filename
                        else:
                            flash("Invalid file extension: {}".format(
                                    pic.filename), "warning")
                # Set selected pic as post cover.
                for pic in post.gallery:
                    if pic.filename == request.form['choice']:
                        post.cover = pic
                try:
                    db.session.commit()
                    flash("Post has been updated.", "success")
                except Exception as e:
                    flash("Error saving post data.", "danger")
            else:
                flash("Posts cannot have more than 8 pictures.", "warning")
        # Zip pics and forms for easy iterating in template.
        return render_template('edit-post.html', form=form, post=post,
                zipped=zip(form.pic_forms, post.gallery))
    else:
        flash("You lack editing rights for this post.", "warning")
        return redirect(url_for('userPosts'))

@app.route('/view/<post_id>', methods=["GET", "POST"])
def viewPost(post_id):
    """
    View an individual post.
    """
    post = db.session.query(Post, User.user_name).filter_by(id=post_id).join(
            User).first()
    return render_template('view-post.html', post=post)

@app.route("/test", methods=["GET", "POST"])
def test():
    """
    endpoint for testing
    """
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            print(file.filename)
        print(request.form['choice'])
    return render_template('test.html')
