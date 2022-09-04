from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, RadioField, EmailField, TelField, SelectField, PasswordField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo, Optional, ValidationError
from paula.model import ImageData, User


class Register(FlaskForm):
    first = StringField('First Name', validators=[Length(min=2,max=20), DataRequired()])
    last = StringField('Last Name', validators=[Length(min=2,max=20), DataRequired()])
    email = EmailField('E-Mail', validators=[DataRequired()])
    telephone = TelField('Telephone', validators=[Length(min=10, max=12), Optional()])
    mobile = TelField('Mobile/Whatsapp')
    company = StringField('Company', validators=[Length(min=2,max=20), Optional()])
    address1 = StringField('Address 1', validators=[Length(min=2,max=20), Optional()])
    address2 = StringField('Address 2', validators=[Length(min=2,max=20), Optional()])
    city = StringField('City', validators=[Length(min=2,max=20)])
    post_code = StringField('Post Code', validators=[Length(min=2,max=20), Optional()])
    country = SelectField('Country', choices=['Kenya','Uganda','Tanzania','Rwanda'])
    town = SelectField('Town', choices=['Nairobi','Mombasa','Kisumu','Nakuru'])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords did not match!')])
    newsletter = RadioField('Subscribe', choices=[('value','Yes'),('value-2','No')], validators=[Optional()])
    privacy = BooleanField()
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email already exists. Please choose another')

    def validate_mobile(self, mobile):
        user = User.query.filter_by(mobile=mobile.data).first()
        if user:
            raise ValidationError('That mobile number is already in use. Please use another')


class Login(FlaskForm):
    email = EmailField('Email Address', validators=[Length(min=2,max=30), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField()
    submit = SubmitField('Login')


class ImageForm(FlaskForm):
    image_name = StringField('Art name', validators=[DataRequired(), Length(min=2,max=30)])
    image_desc = TextAreaField('Art description', validators=[DataRequired()])
    price = StringField('Cost of Art', validators=[DataRequired()])
    category = RadioField('Category', choices=['Running Banner','Lower Banner','Best Seller', 'Featured', 'Special'], validators=[DataRequired()])
    group = RadioField('Group Image By', choices=['Decorative Art','Photography','Fine Art', 'Painting', 'New Media', 'Drawing', 'Antic Images'], validators=[DataRequired()])
    image = FileField('Upload', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField('Submit')

    def validate_image_name(self, image_name):
        image = ImageData.query.filter_by(image_name=image_name.data).first()
        if image:
            raise ValidationError('That Image name already exists. Please choose another')


def db_image_list():
    image_list1 = ImageData.query.with_entities(ImageData.image_name).order_by(ImageData.image_name.asc())
    image_list = [str(i[0]) for i in image_list1]
    return image_list
class Contact(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2,max=30)])
    email = EmailField('Email', validators=[DataRequired(), Length(min=2,max=30)])
    phone = TelField('Phone')
    order = SelectMultipleField('Select the picture(s) you wish to purchase', choices=db_image_list())
    message = TextAreaField('Your message', validators=[Length(min=2, max=150)])
    submit = SubmitField('Send')


class RequestResetForm(FlaskForm):
     email = EmailField('Email', validators=[DataRequired(), Length(min=2,max=30)])
     submit = SubmitField('Request Password Reset')

     def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. Register first')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords did not match!')])
    submit = SubmitField('Reset Password')