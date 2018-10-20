from flask_wtf import Form

from wtforms import (StringField, PasswordField,
                     IntegerField, SelectMultipleField)
from wtforms.fields.html5 import DateField
from wtforms.validators import (ValidationError, DataRequired,
                                Email, Length, EqualTo)

from flask_pagedown.fields import PageDownField

from models import User


def email_exist(form, field):
    """Duplicate Email check"""
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')


def positive_value(form, field):
    """Positive value for Time Spent"""
    if field.data < 0:
        raise ValidationError('The number must be positive and greater than 0')


class RegistrationForm(Form):
    """Registration Form"""
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
    """Login Form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class TagForm(Form):
    """Tag Form"""
    title = StringField('Title', validators=[DataRequired()])


class JournalForm(Form):
    """Journal Form"""
    tags = SelectMultipleField(
        'Tags',
        coerce=int)

    title = StringField('Title', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time_spent = IntegerField('Time Spent',
                              validators=[DataRequired(), positive_value])
    learned = PageDownField('What I learned',
                            validators=[DataRequired()])
    resources = PageDownField('Resources to Remember',
                              validators=[DataRequired()])
