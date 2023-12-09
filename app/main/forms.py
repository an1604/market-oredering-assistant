from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..Models.models import User, Role, Market


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])  # represents an <input> element with type="password"
    remember_me = BooleanField('Keep me logged in')  # represents a checkbox
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    username = StringField('User Name', validators=[DataRequired(), Length(1, 64),
                                                    Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                           'Usernames must have only letters, numbers, dots or '
                                                           'underscores')])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    city = StringField('City', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('password2',
                                                             message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    @staticmethod
    def validate_email(form, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered!')

    @staticmethod
    def validate_username(form, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])

    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)  # Like the <select/> tag in HTML
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        from app.Models.models import User
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        from app.Models.models import User

        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class InitializeMarketProfileForm(FlaskForm):
    market = SelectField('Market')
    market_web_username = StringField('Market Username', validators=[
        DataRequired(), Length(1, 64)])
    market_web_password = PasswordField('Market Password', validators=[DataRequired()])
    submit_btn = SubmitField('Done')

    def __init__(self):
        super(InitializeMarketProfileForm, self).__init__()
        self.market.choices = [market.name
                               for market in Market.query.order_by(Market.name).all()]


class AddMarketAsAdminForm(FlaskForm):
    name = StringField('Market Name', validators=[DataRequired()])
    login_page = StringField('Login Page', validators=[DataRequired()])
    home_page = StringField('Home Page', validators=[DataRequired()])
    thumbnail = StringField('Image source (URL)', validators=[DataRequired()])
    submit_btn = SubmitField('Done')


class PostForm(FlaskForm):
    body = PageDownField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm new password',
                              validators=[DataRequired()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')


class PredictionMLForm(FlaskForm):
    Years_of_experience = StringField('Years Experience', validators=[DataRequired()])
    submit = SubmitField('Predict Salary')


class PredictionDLForm(FlaskForm):
    review = StringField('Review', validators=[DataRequired()])
    submit = SubmitField('Predict')

class MessageForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')
