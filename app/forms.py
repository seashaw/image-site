"""
File: forms.py
Created: 2014-11-14 - C.Shaw <shaw.colin@gmail.com>
Description: 
    Forms and custom validators for form fields.
"""
from . model import User
from flask.ext.wtf import Form
from wtforms import (TextField, SubmitField, PasswordField, TextAreaField,
        FieldList, FileField)
from wtforms.validators import (InputRequired, Length, EqualTo, ValidationError,
        DataRequired, Email)

"""
Custom validator functions.
"""

def uniqueEmailCheck(form, field):
    """
    Unique email validation.
    """
    if User.query.filter_by(email=field.data).first():
        raise ValidationError('"{}" is already registered'.format(field.data))

def emailExistsCheck(form, field):
    """
    Ensures that email address exists in the database.
    """
    if not User.query.filter_by(email=field.data).first():
        raise ValidationError('"{}" is not registered'.format(field.data))

def userNameCheck(form, field):
    """
    Unique user name validation.
    """
    if User.query.filter_by(user_name=field.data).first():
        raise ValidationError('"{}" is already taken'.format(field.data))


"""
Forms for user input.
"""

class LoginForm(Form):
    """
    User authentication.
    """
    email = TextField("Email", validators=[InputRequired()])
    password = PasswordField("password")
    submit = SubmitField("Login")

class RegisterForm(Form):
    """
    User registration.
    """
    email = TextField("Email", validators=[InputRequired(),
            Email(message="Invalid email address format."), uniqueEmailCheck])
    user_name = TextField("User Name", validators=[DataRequired(), userNameCheck])
    password = PasswordField("New Password", validators=[InputRequired(),
            EqualTo("confirm", message="Passwords must match."),
            Length(min=8, max=64, message="Password must be between 8 and 64 "
            "characters.")])
    confirm = PasswordField("Confirm Password", validators=[InputRequired()])
    submit = SubmitField("Register")

class ConfirmationRequestForm(Form):
    """
    Allows users to input their email to receive a confirmation link.
    """
    email = TextField("Email", validators=[InputRequired(), emailExistsCheck] )
    submit = SubmitField("Request Link")
        
class RequestPasswordResetForm(Form):
    """
    User request password reset form.
    """
    email = TextField("Email", validators=[InputRequired(), emailExistsCheck] )
    submit = SubmitField("Request Reset")

class PasswordResetForm(Form):
    """
    Password reset form.
    """
    password = PasswordField("New Password", validators=[InputRequired(),
            EqualTo("confirm", message="Passwords must match."),
            Length(min=8, max=64, message="Password must be between 8 and 64 "
            "characters.")])
    confirm = PasswordField("Confirm Password", validators=[InputRequired()])
    submit = SubmitField("Reset")

class CreatePostForm(Form):
    """
    Post creation.
    """
    pics = FileField('Add Pictures')
    title = TextField('Title', validators=[InputRequired()])
    subtitle = TextField('Subtitle', validators=[InputRequired()])
    body = TextAreaField('Body', validators=[InputRequired()])
    submit = SubmitField("Post")

class EditPostForm(CreatePostForm):
    """
    Post editing and updating.
    """
    submit = SubmitField("Update")
