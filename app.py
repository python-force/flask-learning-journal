from flask import Flask, g, render_template, flash, url_for, redirect
from flask_bcrypt import check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

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

@app.route('/')
def index():
    all_journals = models.Journal.select()
    return render_template('index.html', all_journals=all_journals)

@app.route('/entry', methods=('GET', 'POST'))
def createjournal():
    form = forms.JournalForm()
    if form.validate_on_submit():
        models.Journal.create(user=g.user.id,
                              title=form.title.data,
                              time_spent=form.time_spent.data,
                              learned=form.learned.data,
                              resources=form.resources.data)
        flash("Journal Posted! Thanks!", "success")
        return redirect(url_for('index'))
    return render_template('new.html', form=form)

if __name__ == '__main__':
    models.initialize()
    app.run(debug=DEBUG, host=HOST, port=PORT)