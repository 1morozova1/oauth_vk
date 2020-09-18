from app import app
from flask import render_template, redirect, url_for, flash, request
from flask_login import logout_user, current_user, login_required, login_user
from sqlalchemy.sql import func

from app import db
from app.oauth import OAuthSignIn
from app.models import User, Friend


@app.route('/auth', methods=['GET', 'POST'])
def authorization():
    return render_template('auth.html')


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template(
        'index.html',
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        friends=db.session.query(Friend).order_by(func.random()).limit(5).all()
    )


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    db.session.query(User).filter(User.id == current_user.id).delete()
    db.session.query(Friend).filter(Friend.user_id == current_user.id).delete()
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    user_information, friends = oauth.callback(request.args.get('code'))
    if user_information is None or friends is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=user_information['id']).first()
    if not user:
        user = User(
            social_id=user_information['id'],
            first_name=user_information['first_name'],
            last_name=user_information['last_name'],
            friends=friends
        )
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))
