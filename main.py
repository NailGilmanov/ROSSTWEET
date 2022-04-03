from flask import Flask, render_template, redirect, request, abort, make_response, session
from data import db_session
from data.users import User
from data.twits import Twits
from forms.user import RegisterForm, LoginForm
from forms.twits import TwitsForm

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rosstweet_secret_key'


@app.route("/")
def index():
    session = db_session.create_session()
    twits = session.query(Twits).all()
    return render_template("index.html", twits=twits)


@app.route("/new_twit", methods=['GET', 'POST'])
def new_twit():
    form = TwitsForm()
    session = db_session.create_session()
    if form.validate_on_submit():
        twit = Twits()
        twit.title = form.title.data
        twit.content = form.content.data
        twit.is_private = form.is_private.data
        session.add(twit)
        session.commit()
        return redirect('/')
    return render_template("new_twitt.html", title='Новый твит',
                           form=form)


def main():
    db_session.global_init('db/twitter.sqlite')
    app.run()


if __name__ == '__main__':
    main()
