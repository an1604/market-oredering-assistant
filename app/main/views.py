from flask import render_template, url_for, request, abort, flash, make_response, current_app
from flask import redirect as flask_redirect
from . import main
from .. import db
from ..helper_functions import get_showing_followed_posts_query
from .forms import PostForm, InitializeMarketProfileForm, AddMarketAsAdminForm
from flask_login import login_required, logout_user, current_user, login_user
from ..Models.models import Permission, Post, User, Market, Comment, Order, Message, Chat
from .forms import EditProfileForm, EditProfileAdminForm, CommentForm, MessageForm
from ..helper_functions import (update_form_by_user_data, update_user_by_form_data,
                                update_user_market_details)
from ..api.decorators import permission_required, admin_required
from scraper.handle_login import handle_login


@main.context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.route('/', methods=['GET', 'POST'])
def index():
    query = get_showing_followed_posts_query()
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return flask_redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=10,
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           pagination=pagination)


"""User routes -----------------------------------------------"""


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = (user.orders.order_by(Order.manufacturing_date.desc(), Order.manufacturing_time.desc()).
                  paginate(page=page, per_page=3, error_out=False))
    orders = pagination.items
    markets = user.markets.all()
    return render_template('user/user.html', user=user, orders=orders, markets=markets, pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return flask_redirect(url_for('main.user', username=current_user.username))
    form.location.data = current_user.location
    return render_template('user/edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        update_user_by_form_data(user=user, form=form)
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return flask_redirect(url_for('main.user', username=user.username))
    update_form_by_user_data(user=user, form=form)
    return render_template('user/edit_profile.html',
                           form=form, user=user)


@main.route('/user_posts')
@login_required
def user_posts():
    posts = current_user.posts.all()
    return render_template('user/user_posts.html', posts=posts)


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')

    if not current_user.is_following(user):
        flash('You are already unfollowing this user.')

    current_user.unfollow(user)
    db.session.commit()
    flash('You are now unfollowed %s.' % username)
    return flask_redirect(url_for('main.user', username=username))


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return flask_redirect(url_for('.index'))

    if current_user.is_following(user):
        flash('You are already following this user.')
        return flask_redirect(url_for('.user', username=username))

    current_user.follow(user)
    db.session.commit()
    flash('You are now following %s.' % username)
    return flask_redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page=page, per_page=20,
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('user/following.html', user=user, title='Followers of',
                           endpoint='followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return flask_redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page=page, per_page=20,
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('user/following.html', user=user, title='Following by',
                           endpoint='followers', pagination=pagination,
                           follows=follows)


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(flask_redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)  # 30 days
    return resp


@main.route('/all')
@login_required
def show_all():
    resp = make_response(flask_redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)  # 30 days
    return resp


"""End User routes -----------------------------------------------"""

"""Market routes --------------------------------------------------"""


@main.route('/market-information', methods=['GET', 'POST'])
@login_required
def market_information():
    form = InitializeMarketProfileForm()
    if form.validate_on_submit():
        market_username = form.market_web_username.data
        market_password = form.market_web_password.data
        market_name = form.market.data
        if handle_login(market_username, market_password):
            flash('Change complete!')
            update_user_market_details(market_username, market_password, market_name)
            return flask_redirect(url_for('main.index'))
        flash('Cannot make the things right, try again.')
    return render_template('market/market-information.html', form=form)


@main.route('/add_market_admin', methods=['GET', 'POST'])
@login_required
@admin_required
def add_market():
    form = AddMarketAsAdminForm()
    if form.validate_on_submit():
        market_name = form.name.data
        login_page = form.login_page.data
        home_page = form.home_page.data
        img_src = form.thumbnail.data
        market = Market.add_new_market(market_name, login_page, home_page, img_src)
        if market:
            flash('Market successfully added!')
            return flask_redirect(url_for('main.user', username=current_user.username))
    return render_template('market/add_market.html', form=form)


"""End Market routes --------------------------------------------------"""
"""Orders routes--------------------------------------------------------------"""


@main.route('/order_details/<order>')
@login_required
def order_details(order):
    return render_template('order/order_details.html', order=order)


"""End Orders routes--------------------------------------------------------------"""

"""Posts routs --------------------------------------------------------------"""


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        try:
            db.session.commit()
            flash('Your comment has been published.')
        except IntegrityError as e:
            pass

        return flask_redirect(url_for('main.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
               10 + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page=page, per_page=10,
        error_out=False)
    comments = pagination.items
    return render_template('post/post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)

    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return flask_redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('post/edit_post.html', form=form)


"""End Posts routs --------------------------------------------------------------"""


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/predict_lr', methods=['GET', 'POST'])
def predict_lr():
    import joblib
    from .forms import PredictionMLForm
    import numpy as np

    form = PredictionMLForm()
    if form.validate_on_submit():
        years_exp = float(form.Years_of_experience.data)
        years_exp = np.array([years_exp]).reshape(-1, 1)
        model_file_path = r"C:\Users\adina\PycharmProjects\pythonProject1\ML-deployment\linear_regression_model.pkl"
        model = open(model_file_path, 'rb')
        lr_model = joblib.load(model)
        model_prediction = lr_model.predict_lr()
        model_prediction = round(float(model_prediction), 2)
        flash('Model prediction is: {}'.format(model_prediction))
    return render_template('predict.html', form=form)


@main.route('/predict_review', methods=['GET', 'POST'])
def predict_review():
    from .forms import PredictionDLForm
    from ..helper_functions import sentiment_prediction
    form = PredictionDLForm()
    if form.validate_on_submit():
        review = form.review.data
        prediction = sentiment_prediction(review)
        flash('Model prediction: {} '.format(prediction))
    return render_template('predict.html', form=form)


@main.route('/new_order', methods=['GET', 'POST'])
@login_required
def new_order():
    form = MessageForm()
    chat = Chat(user_id=current_user.id)
    if form.validate_on_submit():
        message_body = form.message.data
        message = Message(body=message_body)
        chat.messages.append(message)
        db.session.add(chat)
        db.session.commit()
        return flask_redirect(url_for('main.existing_order_chat', id=chat.id))
    return render_template('order/new_order.html', form=form)


@main.route('/existing_order_chat/<int:id>', methods=['GET', 'POST'])
@login_required
def existing_order_chat(id):
    chat = Chat.query.filter_by(id=id).first()
    form = MessageForm()
    if form.validate_on_submit() and chat:
        message_body = form.message.data
        message = Message(body=message_body)
        chat.messages.append(message)
        db.session.add(chat)
        db.session.commit()
        return flask_redirect(url_for('main.existing_order_chat', id=chat.id))
    return render_template('order/existing_order_chat.html', id=chat.id,
                           form=form,
                           messages=chat.messages)
