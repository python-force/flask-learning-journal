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

@app.template_filter()
def datetimefilter(value, format='%B %d, %Y'):
    """Convert a datetime to a different format."""
    return value.strftime(format)

app.jinja_env.filters['datetimefilter'] = datetimefilter


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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))

@app.route('/')
def index():
    context = models.Journal.select()
    return render_template('index.html', context=context)

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

@app.route('/entries/edit/<slug>', methods=('GET', 'POST'))
@login_required
def editentry(slug=None):
    context = models.Journal.select().where(models.Journal.slug == slug).get()
    form = forms.JournalForm()
    form.tags.choices = [(tag.id, tag.title) for tag in models.Tag.select()]
    if form.validate_on_submit():
        context.title=form.title.data
        context.tags=form.tags.data
        context.date = form.date.data
        context.time_spent = form.time_spent.data
        context.learned = form.learned.data
        context.resources = form.resources.data
        context.save()
        flash("Journal Posted! Thanks!", "success")
        return redirect(url_for('index'))
    else:
        form.title.data = context.title
        form.date.data = context.date
        form.time_spent.data = context.time_spent
        form.learned.data = context.learned
        form.resources.data = context.resources
    return render_template('edit.html', form=form)


@app.route('/entries/delete/<slug>', methods=('GET', 'POST'))
@login_required
def deleteentry(slug=None):
    models.Journal.delete().where(models.Journal.slug == slug).execute()
    flash("Journal Deleted!", "success")
    return redirect(url_for('index'))

@app.route('/addtag', methods=('GET', 'POST'))
@login_required
def createtag():
    form = forms.TagForm()
    if form.validate_on_submit():
        models.Tag.create(title=form.title.data,)
        flash("Tag Created! Thanks!", "success")
        return redirect(url_for('index'))
    return render_template('addtag.html', form=form)

@app.route('/entry', methods=('GET', 'POST'))
@login_required
def createjournal():
    form = forms.JournalForm()
    form.tags.choices = [(tag.id, tag.title) for tag in models.Tag.select()]
    if form.validate_on_submit():
        journal = models.Journal.create(user=g.user.id,
                                        title=form.title.data,
                                        date=form.date.data,
                                        time_spent=form.time_spent.data,
                                        learned=form.learned.data,
                                        resources=form.resources.data)
        journal.tags.add(form.tags.data)
        flash("Journal Posted! Thanks!", "success")
        return redirect(url_for('index'))
    return render_template('new.html', form=form)

@app.route('/tags')
@app.route('/tags/<slug>')
def tags(slug=None):
    template = 'tags.html'
    all_tags = models.Tag.select()
    context = all_tags
    if slug != None:
        context = (models.Journal
                           .select()
                           .join(models.TagJornal)
                           .join(models.Tag)
                           .where(models.Tag.slug == slug))
        template = 'index.html'
    return render_template(template, context=context)

if __name__ == '__main__':
    models.initialize()
    app.run(debug=DEBUG, host=HOST, port=PORT)