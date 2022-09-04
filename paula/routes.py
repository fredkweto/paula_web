import os, secrets, smtplib
from email.message import EmailMessage
from tkinter import image_names
from paula import app, db, bcrypt, mail
from flask import flash, redirect, url_for, render_template, request, session
from paula.forms import (Contact, ImageForm, Register, Login, db_image_list, 
                        RequestResetForm, ResetPasswordForm)
from paula.model import ImageData, User
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    bestseller = ImageData.query.filter_by(category='Best Seller').order_by(ImageData.id.desc()).paginate(page=page, per_page=6)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc()).paginate(page=page, per_page=4)
    featured = ImageData.query.filter_by(category='Featured').order_by(ImageData.id.desc()).paginate(page=page, per_page=9)
    running = ImageData.query.filter_by(category='Running Banner').order_by(ImageData.id.desc()).paginate(page=page, per_page=3)
    lower = ImageData.query.filter_by(category='Lower Banner').order_by(ImageData.id.desc()).paginate(page=page, per_page=3)
    return render_template('home.html', special=special, 
                        featured=featured, bestseller=bestseller, running=running, lower=lower)


@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Register()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
        user = User(first=form.first.data, last=form.last.data, email=form.email.data, telephone=form.telephone.data, \
                    mobile=form.mobile.data, company=form.company.data, address1=form.address1.data, address2=form.address2.data, \
                    city=form.city.data, post_code=form.post_code.data, country=form.country.data, town=form.town.data, password=hashed_password, \
                    confirm_password=form.confirm_password.data, newsletter=form.newsletter.data, privacy=form.privacy.data)
        db.session.add(user)
        db.session.commit()
        flash (f"Account created for {form.first.data} {form.last.data}", 'success')
        return redirect(url_for('login'))
    page = request.args.get('page', 1, type=int)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc()).paginate(page=page, per_page=2)
    return render_template('register.html', special=special, form=form)


@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect (next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login Unsuccessful. Please check the email and password.", 'danger')
    page = request.args.get('page', 1, type=int)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc()).paginate(page=page, per_page=2)
    return render_template('logon.html', special=special, form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _ , f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join('paula\static\web_images', picture_fn)
    form_picture.save(picture_path)
    return picture_fn


@app.route("/input", methods=['POST', 'GET'])
@login_required
def input():
    form = ImageForm()
    if form.validate_on_submit():
        photo = save_picture(form.image.data)
        user = User.query.all()
        bestseller = ImageData(image_name=form.image_name.data, image_desc=form.image_desc.data, \
                    price=form.price.data, category=form.category.data, group=form.group.data, image=photo, user_id=current_user.id)
        db.session.add(bestseller)
        db.session.commit()
        flash(f'Image of {form.image_name.data} uploaded successfully', 'success')
        return redirect(url_for('home'))
    page = request.args.get('page', 1, type=int)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc()).paginate(page=page, per_page=2)
    all_images = ImageData.query.order_by(ImageData.id.desc()).paginate(page=page, per_page=19)
    return render_template('input.html', form=form, legend='Items Input', special=special, images=all_images)


@app.route("/post", methods=['POST', 'GET'])
def post():
    post = ImageData.query.all()
    return render_template('post.html', post=post)


@app.route("/post/<post_id>", methods=['POST', 'GET'])
def single_post(post_id):
    post = ImageData.query.get_or_404(post_id)
    return render_template('post.html', post=post)


@app.route("/input/update/<int:post_id>", methods=['POST', 'GET'])
@login_required
def update(post_id):
    post = ImageData.query.get_or_404(post_id)
    form = ImageForm()
    if form.validate_on_submit():
        post.image_name = form.image_name.data
        post.image_desc = form.image_desc.data
        post.price = form.price.data
        post.category = form.category.data
        form.image.data =  post.image
        db.session.commit()
        flash(f'Updated {form.image_name.data} successfully', 'success')
        return redirect(url_for('home', post_id=post.id))
    elif request.method == 'GET':
        form.image_name.data = post.image_name
        form.image_desc.data = post.image_desc
        form.price.data =  post.price
        form.category.data =  post.category
        form.image.data =  post.image
    page = request.args.get('page', 1, type=int)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc()).paginate(page=page, per_page=2)
    all_images = ImageData.query.order_by(ImageData.id.desc()).paginate(page=page, per_page=9)
    return render_template('input.html', form=form, legend=f'Update {post.image_name}', special=special, images=all_images)


@app.route("/delete/<int:post_id>", methods=['POST','GET'])
@login_required
def delete_post(post_id):
    form = ImageForm()
    page = request.args.get('page', 1, type=int)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc()).paginate(page=page, per_page=2)
    all_images = ImageData.query.order_by(ImageData.id.desc()).paginate(page=page, per_page=9)
    post = ImageData.query.get_or_404(post_id)
    try:
        os.unlink(os.path.join('paula\static\web_images', post.image))
        db.session.delete(post)
    except:
        db.session.delete(post)
    db.session.commit()
    flash('Your post has been successfully deleted', 'success')
    return redirect(url_for('input'))
    # return render_template('input.html', form=form, special=special, images=all_images, post=post)


@app.route("/gallery")
def gallery():
    page = request.args.get('page', 1, type=int)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc())
    gallery = ImageData.query.order_by(ImageData.id.desc()).paginate(page=page, per_page=6)
    return render_template('gallery.html', gallery=gallery, special=special, legend = 'Gallery')


@app.route("/Antic Images")
def antic_images():
    page = request.args.get('page', 1, type=int)
    antic = ImageData.query.filter_by(group='Antic Images').order_by(ImageData.id.desc()).paginate(page=page, per_page=6)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc()).paginate(page=page, per_page=2)
    return render_template('antic_images.html', gallery=antic, special=special, legend = 'Antic Images')


@app.route("/Drawing")
def Drawing():
    page = request.args.get('page', 1, type=int)
    Drawing = ImageData.query.filter_by(group='Drawing').order_by(ImageData.id.desc()).paginate(page=page, per_page=6)
    special = ImageData.query.filter_by(category='Drawing').order_by(ImageData.id.desc()).paginate(page=page, per_page=2)
    return render_template('Drawing.html', gallery=Drawing, special=special, legend = 'Drawing')


@app.route("/New Media")
def New_Media():
    page = request.args.get('page', 1, type=int)
    New_Media = ImageData.query.filter_by(group='New Media').order_by(ImageData.id.desc()).paginate(page=page, per_page=6)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc()).paginate(page=page, per_page=2)
    return render_template('New_Media.html', gallery=New_Media, special=special, legend = 'New Media')


@app.route("/Painting")
def Painting():
    page = request.args.get('page', 1, type=int)
    Painting = ImageData.query.filter_by(group='Painting').order_by(ImageData.id.desc()).paginate(page=page, per_page=6)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc()).paginate(page=page, per_page=2)
    return render_template('Painting.html', gallery=Painting, special=special, legend = 'Painting')


@app.route("/Fine Art")
def Fine_Art():
    page = request.args.get('page', 1, type=int)
    Fine_Art = ImageData.query.filter_by(group='Fine Art').order_by(ImageData.id.desc()).paginate(page=page, per_page=6)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc()).paginate(page=page, per_page=2)
    return render_template('Fine_Art.html', gallery=Fine_Art, special=special, legend = 'Fine Art')


@app.route("/Photography")
def Photography():
    page = request.args.get('page', 1, type=int)
    Photography = ImageData.query.filter_by(group='Photography').order_by(ImageData.id.desc()).paginate(page=page, per_page=6)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc()).paginate(page=page, per_page=2)
    return render_template('Photography.html', gallery=Photography, special=special, legend = 'Photography')


@app.route("/Decorative Art")
def Decorative_Art():
    page = request.args.get('page', 1, type=int)
    Decorative_Art = ImageData.query.filter_by(group='Decorative Art').order_by(ImageData.id.desc()).paginate(page=page, per_page=6)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc()).paginate(page=page, per_page=2)
    return render_template('Decorative_Art.html', gallery=Decorative_Art, special=special, legend = 'Decorative Art')

# EMAIL_ADDRESS = os.environ.get('USER_GOOGLE_EMAIL')
# EMAIL_PASSWORD = os.environ.get('USER_GOOGLE_PASSWORD')
def email_body(Email_Address, Email_password, name, email, phone, order, message):
    msg = EmailMessage()
    msg['Subject'] = f'New order message from {name}'
    msg['From'] = Email_Address
    msg['To'] = ['fredkweto@outlook.com','paulaonyango.po@gmail.com']

    msg.set_content(f''' 
        Name: {name}.
        Email: {email}.
        Phone: {phone}. 
        Pictures selected: {order}.
        Message: {message}.
    ''')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(Email_Address, Email_password)
        smtp.send_message(msg)
        print('Message sent')

@app.route("/contact", methods=['POST','GET'])
def contact():
    db_image_list()
    form = Contact()
    if form.validate_on_submit():
        EMAIL_ADDRESS = 'fredomondiq@gmail.com'
        EMAIL_PASSWORD = 'corzwiyjpnqupcij'
        email_body(EMAIL_ADDRESS, EMAIL_PASSWORD,form.name.data, form.email.data, form.phone.data, form.order.data, form.message.data)
        flash(f'Thank you {form.name.data} for your order. We will update you on the status shortly. Good day!', 'success') #Add to admin management page. 
        return(redirect(url_for('contact')))
    page = request.args.get('page', 1, type=int)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc()).paginate(page=page, per_page=2)
    return render_template('contact.html', special=special, form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/about")
def about():
    page = request.args.get('page', 1, type=int)
    special = ImageData.query.filter_by(category='Special').order_by(ImageData.id.desc()).paginate(page=page, per_page=2)
    lower = ImageData.query.filter_by(category='Lower Banner').order_by(ImageData.id.desc()).paginate(page=page, per_page=3)
    return render_template('about.html', special=special, lower=lower)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, vistit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and chnage will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with password reset your password','info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', form=form)


@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid ior expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
        user.password = hashed_password
        db.session.commit()
        flash ("Your password has been updated!", 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', form=form)



# ................CHECKOUT..........................
@app.route('/')
def products():
    rows = ImageData.query.all()
    return render_template('products.html', products=rows)
 

# ADD TO CART --------
@app.route('/add', methods=['POST'])
def add_product_to_cart():
    _quantity = int(request.form['quantity'])
    _code = request.form['image_name']
    # validate the received values
    if _quantity and _code and request.method == 'POST':

        row = User.query.filter_by(image_names=_code).first()
                 
        itemArray = { row['code'] : {'name' : row['name'], 'code' : row['code'], 'quantity' : _quantity, 'price' : row['price'], 'image' : row['image'], 'total_price': _quantity * row['price']}}
                 
        all_total_price = 0
        all_total_quantity = 0
                 
        session.modified = True
        if 'cart_item' in session:
            if row['code'] in session['cart_item']:
                for key, value in session['cart_item'].items():
                    if row['code'] == key:
                        old_quantity = session['cart_item'][key]['quantity']
                        total_quantity = old_quantity + _quantity
                        session['cart_item'][key]['quantity'] = total_quantity
                        session['cart_item'][key]['total_price'] = total_quantity * row['price']
            else:
                session['cart_item'] = array_merge(session['cart_item'], itemArray)
         
            for key, value in session['cart_item'].items():
                individual_quantity = int(session['cart_item'][key]['quantity'])
                individual_price = float(session['cart_item'][key]['total_price'])
                all_total_quantity = all_total_quantity + individual_quantity
                all_total_price = all_total_price + individual_price
        else:
            session['cart_item'] = itemArray
            all_total_quantity = all_total_quantity + _quantity
            all_total_price = all_total_price + _quantity * row['price']
             
        session['all_total_quantity'] = all_total_quantity
        session['all_total_price'] = all_total_price
                 
        return redirect(url_for('products'))
    else:
        return 'Error while adding item to cart'
 
#  EMPTY CART -------/
@app.route('/empty')
def empty_cart():
    try:
        session.clear()
        return redirect(url_for('.products'))
    except Exception as e:
        print(e)
 
@app.route('/delete/<string:code>')
def delete_product(code):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True
         
        for item in session['cart_item'].items():
            if item[0] == code:    
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break
         
        if all_total_quantity == 0:
            session.clear()
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price
             
        return redirect(url_for('.products'))
    except Exception as e:
        print(e)
 
def array_merge( first_array , second_array ):
    if isinstance( first_array , list ) and isinstance( second_array , list ):
        return first_array + second_array
    elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
        return dict( list( first_array.items() ) + list( second_array.items() ) )
    elif isinstance( first_array , set ) and isinstance( second_array , set ):
        return first_array.union( second_array )
    return False