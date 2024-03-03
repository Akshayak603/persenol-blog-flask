# flask framework basically Flask is a class in flask module
from flask import Flask, render_template, request, session, redirect, flash
# we have a backend also if we dont pass date here it will automatically takes current timestamp in db
# but as we are trying to do these things through frontend so we are using datetime here
from datetime import datetime
# from werkzeug.utils import secure_filename
import os
import json
import math
# to implement mail functionality
from flask_mail import Mail
# cloud uploader
import cloudinary
import cloudinary.uploader
import cloudinary.api
# env
from dotenv import load_dotenv
# models
from models.model_file import db, Contacts, Posts

# for loacal config.json (development)
# with open('config.json', 'r') as c:
#     # it will be global
#     params = json.load(c)["params"]


# for production

# load env file
load_dotenv()

# using params
params = {}
# accessing env variables and ignoring local_ones in prod
# params["local_server"] = os.getenv('local_server')
params["local_uri"] = os.getenv("local_uri")
params["prod_uri"] = os.getenv("prod_uri")
params["tw_uri"] = os.getenv("tw_uri")
params["linkedin_uri"] = os.getenv("linkedin_uri")
params["gh_uri"] = os.getenv("gh_uri")
params["blog_name"] = os.getenv("blog_name")
params["tag_line"] = os.getenv("tag_line")
params["gmail-username"] = os.getenv("gmail_username")
params["gmail-password"] = os.getenv("gmail_password")
params["about-text"] = os.getenv("about_text")
params["no_of_posts"] = int(os.getenv("no_of_posts"))
params["admin_login_img"] = os.getenv("admin_login_img")
params['admin_user'] = os.getenv('admin_user')
params["admin_password"] = os.getenv('admin_password')
params['secret'] = os.getenv('secret')
params['cloudinary_name'] = os.getenv('cloudinary_name')
params['cloudinary_key'] = os.getenv('cloudinary_key')
params['cloudinary_secret'] = os.getenv('cloudinary_secret')
params["upload_folder"] = os.getenv('upload_folder')


local_server = False

app = Flask(__name__)  # creating instance of this class
app.secret_key = params['secret']  # needed for sessions in flask
# configuring our app to use variables

# single configuration
# app.config['UPLOAD_FOLDER'] = params['upload_path']  # for uploading file to local

# multi configuration we can access these via app.cofig['MAIL_SERVER]
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params["gmail-username"],
    MAIL_PASSWORD=params["gmail-password"]
)

# Configuring cloudinary
cloudinary.config(
    cloud_name=params['cloudinary_name'],
    api_key=params['cloudinary_key'],
    api_secret=params['cloudinary_secret']
)

# creating mail instance
mail = Mail(app)

# print(local_server)
# print(params["local_server"])
# print(params["local_uri"])

# Creating db connection  local=> sqlite prod=> postgres
if local_server:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["local_uri"]
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["prod_uri"]

# creating db instance
db.init_app(app)

# HOME
# crating endpoint
# here @ is a decorator which is passing our below fuction to some function


@app.route('/')
def home():
    # PAGINATION
    # posts = Posts.query.filter_by().all()
    posts= Posts.query.order_by(Posts.date.desc()).all()
    last = math.ceil(len(posts)/params["no_of_posts"])  # as we want 5.6~6
    # [0:params["no_of_posts"]

    # query params
    # here we are fetching page from query as at first it will be on first page and there is a chance page might be None
    page = request.args.get('page')
    # print(type(page))

    # so to handle this we use this and set page =1
    if not str(page).isnumeric():
        page = 1
    page = int(page)
    # to show posts on each page
    posts = posts[(page-1)*int(params["no_of_posts"]):(page-1)
                  * int(params["no_of_posts"])+int(params["no_of_posts"])]

    # First page means prev=# next=page+1
    if last == 1 or last == 0:
        prev = "#"
        # setting query as our function will fetch the page number from query so this is the to pass query to the URL "/?urf="
        next = "#"
    elif page == 1:
        prev = "#"
        # setting query as our function will fetch the page number from query so this is the to pass query to the URL "/?urf="
        next = "/?page="+str(page+1)
    # middle prev=page-1 next=page+1
    elif page == last:
        prev = "/?page="+str(page-1)
        next = "#"
    # last prev=page-1 next=#
    else:
        prev = "/?page="+str(page-1)
        next = "/?page="+str(page+1)

    # posts= Posts.query.filter_by().all()[:params["no_of_posts"]]
    # print(type(posts[0]))
    # print(type(posts))
    # to use template we use render_template under the hood we are using JINJA2
    return render_template('Views/index.html', params=params, posts=posts, prev=prev, next=next)

#about
@app.route('/about')
def about():
    # to use template we use render_template under the hood we are using JINJA2
    return render_template('Views/about.html', params=params)

#contacts
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('Views/contact.html', params=params)

    if request.method == 'POST':
        '''Add entry to the db'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')
        entry = Contacts(name=name, phone_num=phone, msg=msg,
                         date=datetime.now(), email=email)
        # here db.session is used to execute db command
        db.session.add(entry)
        db.session.commit()
        phone_number = 'N/A'
        if phone:
            phone_number = phone
        message = f'{msg} \n\n Contact Email: {email} \n Phone: {phone_number}'
        mail.send_message("New messsage from " + name,
                          sender=email,
                          recipients=[params["gmail-username"]],
                          body=message)
        flash('Message sent! Thanks for your interest in our blog. We will get back to you soon.', category='success')
    # to use template we use render_template under the hood we are using JINJA2
    return redirect('/')

# Render Blog
# if youre passing string in your url then you need to pass that as a parameter in that function as it is a rule
@app.route('/<string:post_slug>/<string:sno>', methods=['GET'])
def post_route(post_slug, sno):
    # fetching data from db
    post = Posts.query.filter_by(sno=sno).first()
    img_url = ''
    if post:
        img_url = post.img_file['link']
    # print(type(post))
    # to use template we use render_template under the hood we are using JINJA2
    return render_template('Views/post.html', params=params, post=post, img_url=img_url)

# CRUD

# READ with login functionality
@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        # reading
        posts = Posts.query.all()
        return render_template('Views/dashboard.html', params=params, posts=posts)
    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('password')
        if (username == params["admin_user"] and userpass == params["admin_password"]):
            # set the session
            session['user'] = username
            posts = Posts.query.all()
            flash("You have been logged in successfully!")
            return render_template('Views/dashboard.html', params=params, posts=posts)

    return render_template('Views/login.html', params=params)

# logout thr user by default it takes get method
@app.route('/logout')
def logout():
    session.pop('user')
    flash('You have been logged out succesfully!')
    return redirect("/dashboard")


# add (CREATE)
@app.route('/add', methods=["GET", "POST"])
def add():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == "GET":
            # for creating
            return render_template('Views/addBlog.html', params=params)
        # CREATE
        if request.method == 'POST':
            '''sno,title,slug,subheading,content,date,img_file'''
            title = request.form.get('title')
            slug = request.form.get('slug')
            subheading = request.form.get('subheading')
            content = request.form.get('content')
            img_file_real = request.files['img_file']
            date = str(datetime.now().strftime("%Y-%m-%d %H:%M"))

            result = cloudinary.uploader.upload(
                img_file_real, folder=params['upload_folder'], resource_type="image")

            img_file = {'link': result['secure_url'],
                        'public_id': result['public_id']}

            new_blog = Posts(title=title, slug=slug, subheading=subheading,
                             content=content, img_file=img_file, date=date)
            db.session.add(new_blog)
            db.session.commit()
            flash("Your blog has been added successfully!")

    return redirect('/dashboard')


# EDIT (put by post)
@app.route('/edit/<string:sno>', methods=["GET", "POST"])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        # For editing template
        if Posts.query.filter_by(sno=sno).first() and request.method == 'GET':
            # print(request.method)
            post = Posts.query.filter_by(sno=sno).first()
            # print(pst)
            return render_template('Views/editBlog.html', params=params, post=post, sno=sno)

        # edit
        elif request.method == 'POST':
            '''sno,title,slug,subheading,content,date,img_file'''
            title = request.form.get('title')
            slug = request.form.get('slug')
            subheading = request.form.get('subheading')
            content = request.form.get('content')
            img_file_real = request.files['img_file']
            date = str(datetime.now().strftime("%Y-%m-%d %H:%M"))

            edit_blog = Posts.query.filter_by(sno=sno).first()

            img_file = ""
            if img_file_real:
                # delete previous image
                img_id = edit_blog.img_file['public_id']
                cloudinary.api.delete_resources(
                    [img_id], resource_type="image", type="upload")

                # upload new image
                result = cloudinary.uploader.upload(
                    img_file_real, folder=params['upload_folder'], resource_type="image")
                current_image_data = json.dumps(edit_blog.img_file)
                new_img_data = json.loads(current_image_data)
                # new_img_data['image_id']  = result['asset_id']
                # new_img_data['name']= result['public_id']
                new_img_data['link'] = result['secure_url']
                new_img_data['public_id'] = result['public_id']

                img_file = new_img_data

            else:
                current_image_data = json.dumps(edit_blog.img_file)
                new_img_data = json.loads(current_image_data)

                img_file = new_img_data

            edit_blog.title = title
            edit_blog.slug = slug
            edit_blog.subheading = subheading
            edit_blog.content = content
            edit_blog.img_file = img_file
            edit_blog.date = date
            db.session.commit()
            flash("Your blog has been edited successfully!")

    return redirect('/dashboard')

# DELETE


@app.route('/delete/<string:sno>')
def delete(sno):
    if 'user' in session and session['user'] == params["admin_user"]:
        del_blog = Posts.query.filter_by(sno=sno).first()
        if del_blog:
            img_id = del_blog.img_file['public_id']
            cloudinary.api.delete_resources(
                [img_id], resource_type="image", type="upload")
        db.session.delete(del_blog)
        db.session.commit()
        flash("Your blog has been deleted successfully!")
        return redirect("/dashboard")

# upload your file for backgrounds


@app.route('/upload', methods=["POST"])
def upload():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            f = request.files['upload']
            # path_to_upload = f'/blog_posts/{f}'
            # cloud
            cloudinary.uploader.upload(
                f, folder=params['upload_folder'], resource_type="image")

            # print(result['asset_id'])

            # securing file local
            # f.save(os.path.join(
            #     app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            # flash("Your file has been uploaded successfully!")
    return redirect('/dashboard')


@app.errorhandler(Exception)
def handle_404(error):
    print(error)
    return render_template('Views/404_error.html')
