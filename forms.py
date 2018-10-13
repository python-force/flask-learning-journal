from flask_wtf import Form

from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectMultipleField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Email, Regexp, Length, EqualTo

from flask_pagedown.fields import PageDownField

from models import User, Journal, Tag

def email_exist(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')

def title_exist(form, field):
    if Journal.select().where(Journal.title == field.data).exists():
        raise ValidationError('Record with this title already exists, to edit the this entry, go to main menu and click edit.')

def tag_title_exist(form, field):
    if Tag.select().where(Tag.title == field.data).exists():
        raise ValidationError('Record with this title already exists, to edit the this entry, go to main menu and click edit.')

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
    title = StringField('Title', validators=[DataRequired(), tag_title_exist])

class JournalForm(Form):
    tags = SelectMultipleField('Tags', choices=[('1', 'Space to Mars'), ('2', 'Earth')])
    title = StringField('Title', validators=[DataRequired(), title_exist])
    date = DateField('Date', validators=[DataRequired()])
    time_spent = IntegerField('Time Spent', validators=[DataRequired(), positive_value])
    learned = TextAreaField('What I learned', validators=[DataRequired()])
    resources = PageDownField('Resources to Remember', validators=[DataRequired()])