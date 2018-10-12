from flask import Flask, g, render_template, flash, url_for, redirect
from flask_bcrypt import check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_pagedown import PageDown
from flaskext.markdown import Markdown

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'sd7sa76v8*&%7asf7656#dsjksadjwaalcma.caskascjhavs'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

pagedown = PageDown(app)
Markdown(app)


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user

@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response

@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        flash("Yay, you registered!", "success")
        models.User.create_user(
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)

@app.route('/')
def index():
    all_journals = models.Journal.select()
    return render_template('index.html', all_journals=all_journals)

@app.route('/entries')
@app.route('/entries/<slug>')
def entries(slug=None):
    template = 'index.html'
    all_journals = models.Journal.select()
    context = all_journals
    if slug != None:
        context = models.Journal.select().where(models.Journal.slug==slug).get()
        template = 'detail.html'
    return render_template(template, context=context)

@app.route('/entry', methods=('GET', 'POST'))
@login_required
def createjournal():
    form = forms.JournalForm()
    if form.validate_on_submit():
        models.Journal.create(user=g.user.id,
                              title=form.title.data,
                              date=form.date.data,
                              time_spent=form.time_spent.data,
                              learned=form.learned.data,
                              resources=form.resources.data)
        flash("Journal Posted! Thanks!", "success")
        return redirect(url_for('index'))
    return render_template('new.html', form=form)

if __name__ == '__main__':
    models.initialize()
    app.run(debug=DEBUG, host=HOST, port=PORT)