from flask import Flask, render_template, redirect, request, abort, make_response, session, jsonify, url_for
from data import db_session
from data.users import User
from data.twits import Twits
from data.comments import Comment
from forms.user import RegisterForm, LoginForm
from forms.twits import TwitsForm
from forms.comments import CommentsForm

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session, twits_api


app = Flask(__name__)
app.config['SECRET_KEY'] = 'rosstweet_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


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
        current_user.news.append(twit)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template("new_twitt.html", title='Новый твит',
                           form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/success')
def success():
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/twits/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_twit(id):
    form = TwitsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        twit = db_sess.query(Twits).filter(Twits.id == id,
                                          Twits.user == current_user
                                          ).first()
        if twit:
            form.title.data = twit.title
            form.content.data = twit.content
            form.is_private.data = twit.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(Twits).filter(Twits.id == id,
                                          Twits.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('new_twitt.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/twits_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def twit_delete(id):
    db_sess = db_session.create_session()
    twit = db_sess.query(Twits).filter(Twits.id == id,
                                      Twits.user == current_user
                                      ).first()
    if twit:
        db_sess.delete(twit)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db_sess = db_session.create_session()
    twits = db_sess.query(Twits).filter(Twits.user_id == current_user.id).all()
    return render_template('profile.html', twits=twits)


@app.route('/comments/<int:id>', methods=['GET', 'POST'])
@login_required
def comments(id):
    db_sess = db_session.create_session()
    comments = db_sess.query(Comment).filter(Comment.twit_id == id
                                       ).all()
    twit = db_sess.query(Twits).filter(Twits.id == id
                                       ).first()
    form = CommentsForm()
    if form.validate_on_submit():
        comment = Comment()
        comment.content = form.content.data
        comment.twit_id = id
        comment.user_id = current_user.id
        db_sess.add(comment)
        db_sess.commit()
        return redirect(f'/comments/{id}')
    else:
        return render_template('comments.html', twit=twit, comments=comments, title='Обсуждение',
                               form=form)


@app.route('/comments_delete/<int:twit_id>/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def comment_delete(comment_id, twit_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).filter(Comment.twit_id == twit_id,
                                            Comment.id == comment_id,
                                            Comment.user == current_user
                                            ).first()
    if comment:
        db_sess.delete(comment)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/comments/{twit_id}')


@app.route('/comments_editing/<int:twit_id>/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id, twit_id):
    form = CommentsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).filter(Comment.twit_id == twit_id,
                                               Comment.id == comment_id,
                                               Comment.user == current_user
                                               ).first()
        if comment:
            form.content.data = comment.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).filter(Comment.twit_id == twit_id,
                                               Comment.id == comment_id,
                                               Comment.user == current_user
                                               ).first()
        if comment:
            comment.content = form.content.data
            db_sess.commit()
            return redirect(f'/comments/{twit_id}')
        else:
            abort(404)
    return render_template('comment_editing.html',
                           title='Редактирование комментрария',
                           form=form
                           )



def main():
    db_session.global_init('db/twitter.sqlite')
    app.register_blueprint(twits_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()
