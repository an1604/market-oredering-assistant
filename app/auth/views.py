from . import auth
from .. import db
from flask import flash, url_for, abort, request, make_response, render_template
from flask import redirect as flask_redirect
from flask_login import login_required, logout_user, current_user, login_user
from ..main.forms import (LoginForm, RegisterForm, EditProfileForm, EditProfileAdminForm,
                          InitializeMarketProfileForm, AddMarketAsAdminForm, PostForm,
                          CommentForm, ChangePasswordForm, PasswordResetRequestForm, ChangeEmailForm)
from ..api.decorators import admin_required, permission_required
from sqlalchemy.exc import IntegrityError
from ..helper_functions import (safe_url, send_email_to_confirm_user, send_email_to_reset_password,
                                send_email_to_change_email)
from ..Models.models import User
import pdb


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return flask_redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return flask_redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return flask_redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('Logged in successfully.')
            next = request.args.get('next')

            if next is None or not safe_url(next):
                next = url_for('main.index')

            return flask_redirect(next)
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return flask_redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        password = form.password.data
        username = form.username.data
        email = form.email.data
        city = form.city.data
        address = form.address.data
        location = address + ',' + city + ',' + form.location.data
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email is already exist, try again.')
            return flask_redirect(url_for('auth.register'))
        user = User(username=username, email=email, city=city, address=address,
                    password=password, location=location)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email_to_confirm_user(user=user, token=token)
        return flask_redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return flask_redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return flask_redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email_to_confirm_user(current_user, token)
    flash('A new confirmation email has been sent to you by email.')
    return flask_redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return flask_redirect(url_for('main.index'))
    else:
        flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return flask_redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email_to_reset_password(tokenm, user)
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return flask_redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return flask_redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Your password has been updated.')
            return flask_redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email_to_change_email(token, user)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return flask_redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return flask_redirect(url_for('main.index'))
