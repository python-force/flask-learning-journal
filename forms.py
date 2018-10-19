from flask_wtf import Form

from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectMultipleField, widgets
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Email, Regexp, Length, EqualTo

from flask_pagedown.fields import PageDownField

from models import User, Journal, Tag

def email_exist(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')

def positive_value(form, field):
    if field.data < 0:
        raise ValidationError('The number must be positive and greater than 0')

class RegistrationForm(Form):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exist
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
        ])


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class TagForm(Form):
    title = StringField('Title', validators=[DataRequired()])

class JournalForm(Form):
    tags = SelectMultipleField(
        'Tags',
        coerce=int)

    title = StringField('Title', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time_spent = IntegerField('Time Spent', validators=[DataRequired(), positive_value])
    learned = PageDownField('What I learned', validators=[DataRequired()])
    resources = PageDownField('Resources to Remember', validators=[DataRequired()])