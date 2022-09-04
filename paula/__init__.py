import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)
# app = application
app.config['SECRET_KEY']= '$2b$12$1EE9Ah/UmT7geARyKawRw.Kbqxr7sr1YJ8q0Tc8Y.xHoDqL42zkv6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'fredomondiq@gmail.com'
app.config['MAIL_PASSWORD'] = 'corzwiyjpnqupcij'
mail = Mail(app)


from paula import routes
