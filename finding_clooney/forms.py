"""
File: forms.py
Created: 2014-10-06 by Colin Shaw
Description: Forms and custom validators for form fields.
"""
from . model import User
from flask.ext.wtf import Form
from wtforms import TextField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import Required, Length, EqualTo, ValidationError

"""
Custom validator functions.
"""

def emailCheck(form, field):
    """
    Unique email validation.
    """
    if User.query.filter_by(email=field.data).first():
        raise ValidationError(
                '"{}" is already registered'.format(field.data))

def userNameCheck(form, field):
    """
    Unique user name validation.
    """
    if User.query.filter_by(user_name=field.data).first():
        raise ValidationError(
                '"{}" is already taken'.format(field.data))


"""
Forms for user input.
"""

class LoginForm(Form):
    """
    Form for login.
    """
    email = TextField("email", validators=[Required()])
    password = PasswordField("password")
    submit = SubmitField("Login")

class RegisterForm(Form):
    """
    Form for registration.
    """
    email = TextField("@", validators=[Required(), emailCheck] )
    first_name = TextField("First", validators=[Required()])
    last_name = TextField("Last", validators=[Required()])
    user_name = TextField("User", validators=[Required(), userNameCheck])
    password = PasswordField("New Password", validators=[Required(), 
        EqualTo("confirm", message="Passwords must match.")])
    confirm = PasswordField("Confirm Password")
    submit = SubmitField("Register")

class EditPostForm(Form):
    """
    Form for creating and editing blog posts.
    """
    title = TextField('Title', validators=[Required()])
    subtitle = TextField('Subtitle', validators=[Required()])
    body = TextAreaField('Body', validators=[Required()])
    submit = SubmitField("Post")
