"""
File: forms.py
Created: 2014-11-14 - C.Shaw <shaw.colin@gmail.com>
Description: 
    Forms and custom validators for form fields.
"""
from .model import User
from flask.ext.wtf import Form
import wtforms
from flask.ext.login import current_user
from wtforms import TextField, SubmitField, PasswordField, TextAreaField, \
        FieldList, FileField, BooleanField, FormField, RadioField, IntegerField
from wtforms.validators import InputRequired, Length, EqualTo, \
        ValidationError, DataRequired, Email

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

def uniqueUserNameCheck(form, field):
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
    email = TextField("Email", validators=[InputRequired(),
            Email(message="Invalid email address format.")])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class RegisterForm(Form):
    """
    User registration.
    """
    email = TextField("Email", validators=[InputRequired(),
            Email(message="Invalid email address format."), uniqueEmailCheck])
    user_name = TextField("User Name", validators=[DataRequired(),
            uniqueUserNameCheck])
    password = PasswordField("New Password", validators=[InputRequired(),
            EqualTo("confirm", message="Passwords must match."),
            Length(min=8, max=64, message="Password must be between 8 and 64 "
            "characters.")])
    confirm = PasswordField("Confirm Password", validators=[InputRequired()])
    submit = SubmitField("Register")

class ServiceRequestForm(Form):
    """
    Allows users to input their email to process service requests.
    """
    email = TextField("Email", validators=[InputRequired(), emailExistsCheck] )
    submit = SubmitField("Send Request")

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
    subtitle = TextField('Subtitle')
    body = TextAreaField('Body')
    submit = SubmitField("Post")

class EditImageDataForm(wtforms.Form):
    """
    For editing picture data.
    """
    title = TextField('Title')
    position = IntegerField('position')
    delete = BooleanField('Delete', default=False)

class EditPostForm(CreatePostForm):
    """
    Post editing and updating posts.
    """
    pic_forms = FieldList(FormField(EditImageDataForm))
    submit = SubmitField("Update")

class CommentForm(Form):
    """
    Form for adding comments to post.
    """
    body = TextAreaField('Leave a comment', validators=[InputRequired()])
    parent_id = IntegerField('Parent ID', default=0)
    submit = SubmitField("Comment")
