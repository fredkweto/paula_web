from datetime import datetime
from paula import db, login_manager, app
from flask_login import UserMixin
from itsdangerous.serializer import Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first = db.Column(db.Integer, nullable=False)
    last = db.Column(db.String(30))
    email = db.Column(db.String(20), unique=True)
    telephone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    company = db.Column(db.String(30))
    address1 = db.Column(db.Integer)
    address2 = db.Column(db.String(20))
    city = db.Column(db.String())
    post_code = db.Column(db.String(20))
    country = db.Column(db.String())
    town = db.Column(db.String())
    password = db.Column(db.String(), nullable=False)
    confirm_password = db.Column(db.String(), nullable=False)
    newsletter = db.Column(db.Integer)
    privacy = db.Column(db.Integer, nullable=False)
    images = db.relationship('ImageData', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.first}', '{self.email}', '{self.mobile}')"

        
class ImageData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(20), unique=True, nullable=False)
    image_desc = db.Column(db.String(150), nullable=False)
    price = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    group = db.Column(db.String(20), nullable=False)
    image = db.Column(db.String(20), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Image('{self.image_name}', '{self.image_desc}', '{self.price}', '{self.category}', '{self.group}', '{self.image}')"


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(), nullable=False)
    order = db.Column(db.String(), nullable=False)
    message = db.Column(db.Text(150), nullable=False)

    def __repr__(self):
        return f"Contact('{self.name}', '{self.email}', '{self.order}')"
