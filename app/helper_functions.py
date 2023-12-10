from flask import request, flash
from flask_login import current_user

from app import db
from .Models.models import Post, Market, UserMarkets, Role
from .email import send_email


def safe_url(target):
    return target.startswith('/') or target.startswith('http://') or target.startswith('https://')


def send_email_to_confirm_user(user, token):
    send_email(user.email, 'Confirm Your Account',
               'auth/email/confirm', user=user, token=token, )
    flash('A confirmation email has been sent to you by email.')


def send_email_to_reset_password(token, user):
    send_email(user.email, 'Reset your password',
               'auth/email/reset_password', user=user, token=token)


def send_email_to_change_email(toke, user):
    send_email(new_email, 'Confirm your email address',
               'auth/email/change_email',
               user=current_user, token=token)


def update_user_by_form_data(user, form):
    user.email = form.email.data
    user.username = form.username.data
    user.confirmed = form.confirmed.data
    user.role = Role.query.get(form.role.data)
    user.name = form.name.data
    user.location = form.location.data
    user.about_me = form.about_me.data


def update_form_by_user_data(user, form):
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.location.data = user.location


def update_user_market_details(market_username, market_password, market_name):
    if current_user.is_authenticated:
        # Get the Market object corresponding to the market_name
        market = Market.query.filter_by(name=market_name).first()

        # Check if the market exists
        if market:
            # Create an instance of the user_markets association table
            new_market_entry = UserMarkets(
                user_id=current_user.id,
                market_id=market.id,
                market_login_username=market_username,
                market_login_password=market_password
            )

            db.session.add(new_market_entry)
            db.session.commit()
        else:
            flash('Market not found.')


def get_showing_followed_posts_query():
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed'''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    return query

