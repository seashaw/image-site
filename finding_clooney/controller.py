"""
File: controller.py
Authors: 
    2014-10-10 - C. Shaw
Description: Routing for web application, generates views using templates,
             and handles logic for user interaction.
"""

import hashlib
from datetime import datetime
import pytz
from pytz import timezone

from . import app, bc, dbh, mail, db
from . model import SumResult, User
from . forms import LoginForm, RegisterForm

from flask import (Flask,
        render_template,
        jsonify,
        request,
        redirect,
        url_for,
        flash)

from flask.ext.login import login_required, login_user, logout_user
from flask.ext.mail import Message

"""
Routing functions, controller logic.
"""

@app.route("/")
@app.route("/index")
@login_required
def index():
    """
    Greeter page containing information about web application.
    Should link to user registration and login.
    """
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Feed form data to User object creation.
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
@login_required
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
                flash("Login successful.")
                return redirect(request.args.get("next") or url_for("index"))
            else:
                flash("Wrong password.")
                return redirect(url_for("login"))
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout successful.")
    return redirect(url_for("login"))

@app.route("/_add-numbers")
def addNumbers():
    """
    Sums two GET request variables and returns result.
    """
    a = request.args.get("a", 0, type=int)
    b = request.args.get("b", 0, type=int)
    return jsonify(sum=a+b)

@app.route("/_insert-sum")
def insertSum():
    """
    Inserts sum into database.
    """
    sum = SumResult(request.args.get("sum", 0, type=int))
    return dbh.insertSum(sum)

@app.route("/view-sums")
@login_required
def viewSums():
    """
    Display all sum results.
    """
    return render_template("view-sums.html", sums=dbh.fetchAllSums())

@app.route("/view-users")
@login_required
def viewUsers():
    """
    Displays list of usernames.
    """
    return render_template("view-users.html", users=dbh.fetchAllUserNames())
