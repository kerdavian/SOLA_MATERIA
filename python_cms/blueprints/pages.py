from fileinput import filename
from posixpath import split
from flask import Blueprint, render_template, request, url_for, send_from_directory
from flask.helpers import flash
from flask_login import login_required, current_user
from python_cms.models.user import UserModel
from werkzeug.utils import secure_filename, redirect
import os
from python_cms.models.post import PostModel
from python_cms.forms.post_form import PostForm
from python_cms.forms.contact_form import ContactForm
from python_cms.models.category import CategoryModel
from python_cms.models.author import AuthorModel
from python_cms.models.tag import TagModel
from python_cms.models.post_tag import PostTagLink
import python_cms
import html
from flask_ckeditor import upload_success, upload_fail
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from python_cms.db import BaseModel, db

import bleach  # https://bleach.readthedocs.io/en/latest/

pages_blueprint = Blueprint("pages", __name__)

now = datetime.now()


def get_post_author(posts, id):
  for post in posts:
    if post.author_id == id:
      name = post.author.name
      return name


@pages_blueprint.route("/")
def index():
  posts = PostModel.get_all()
  return render_template('index.html.j2', posts=posts)


@pages_blueprint.route("/posts/<string:category_name>")
def category(category_name):
  posts = PostModel.get_all()

  return render_template('category.html.j2',
                         posts=posts,
                         category=category_name)


@pages_blueprint.route("/posts/tag/<string:tag_id>")
def tag(tag_id):
  tag_posts = PostTagLink.get_by_tag_id(tag_id)
  posts = []
  for tag_post in tag_posts:
    posts.append(PostModel.get(tag_post.post_id))

  return render_template('tag_posts.html.j2',
                         posts=posts,
                         tag_name=tag_posts[0].tag_name)


@pages_blueprint.route('/mission')
def mission():
  return render_template('mission.html.j2')


@pages_blueprint.route('/about_authors')
def about_authors():
  auths = AuthorModel.get_all()
  for auth in auths:
    print(auth.name)
  return render_template('about_authors.html.j2', auths=auths)


@pages_blueprint.route('/connect_us')
def connect_us():
  return render_template('/connect_us.html.j2')


@pages_blueprint.route('/connection', methods=['GET', 'POST'])
def connection():
  form = ContactForm()
  if request.method == 'POST' and form.validate_on_submit():
    email = request.form.get("email")
    mail_content = request.form.get("message")
    subject = request.form.get("subject")
    mail_content = mail_content + "(" + email + ")"

    sender_address = 'solamateria@gmail.com'
    sender_pass = 'EgyedulAzAnyag'
    receiver_address = 'csampaie.5@gmail.com'

    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = subject

    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))

    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  #use gmail with port
    session.starttls()  #enable security
    session.login(sender_address,
                  sender_pass)  #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()

    return redirect(url_for('pages.connection'))

  return render_template('/connection.html.j2', form=form)


def subscribe():
  form = ContactForm()
  if request.method == 'POST' and form.validate_on_submit():
    email = request.form.get("email")
    mail_content = email
    subject = "Feliratkozás"

    sender_address = 'solamateria@gmail.com'
    sender_pass = 'EgyedulAzAnyag'
    receiver_address = 'csampaie.5@gmail.com'

    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = subject

    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))

    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  #use gmail with port
    session.starttls()  #enable security
    session.login(sender_address,
                  sender_pass)  #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()


@pages_blueprint.route('/author/<string:id>')
def auth_post(id):
  posts = PostModel.get_all()
  name = get_post_author(posts, id)
  return render_template('author_post.html.j2', posts=posts, id=id, name=name)


@pages_blueprint.route("/add", methods=['GET', 'POST'])
@login_required
def create_post():
  form = PostForm()
  all_tags = TagModel.get_all()

  form.category.choices = [(1, 'Filozófia'), (2, 'Tudomány'), (3, 'Politika'),
                           (4, 'Versus')]
  if request.method == 'POST' and form.validate_on_submit():

    tags_from_form = request.form.get('added_tags')
    tags = list(set(tags_from_form.split("-")[1:]))
    # tags = list(set(tags_from_form.split("-")))[1:]

    print(tags)
    unescaped_body = html.unescape(request.form.get('body'))
    clean_body = bleach.clean(unescaped_body,
                              tags=bleach.sanitizer.ALLOWED_TAGS +
                              ['div', 'br', 'p', 'h1', 'h2', 'img', 'h3'],
                              attributes=['src', 'alt', 'style'])
    title = request.form.get('title')

    body = clean_body
    file = request.files['teaser_image']
    if not file:
      flash('Kép nélkül nem tud postot létrehozni!', 'error')
      return render_template('create_post.html.j2', form=form, tags=all_tags)
    if not tags:
      flash('Adjon meg cimkét!', 'error')
      return render_template('create_post.html.j2', form=form, tags=all_tags)

    filename = secure_filename(file.filename)
    file.save(os.path.join(python_cms.ROOT_PATH, 'files_upload', filename))
    promoted = request.form.get('promoted')
    category_id = request.form.get('category')
    category = CategoryModel.get(category_id)
    # current date and time
    date_time = now.strftime("%d/%m/%Y")
    # print("-----------------", category.name)
    post = PostModel(title, body, current_user.get_id(), filename,
                     bool(promoted), category_id, category.name, date_time)

    post.save()

    posts = PostModel.get_all()
    print(posts[len(posts) - 1].id)
    for tag in tags:
      print(tag)
      tag_m = TagModel.get_by_name(tag)
      save_tag = PostTagLink(posts[len(posts) - 1].id, tag_m.id, tag)
      save_tag.save()

    flash(f'Post with title: {title} is created')
    return redirect(url_for('pages.create_post'))

  return render_template('create_post.html.j2', form=form, tags=all_tags)


@pages_blueprint.route('/files/<path:filename>')
def uploaded_files(filename):
  path = os.path.join(python_cms.ROOT_PATH, 'files_upload')
  return send_from_directory(path, filename)


@pages_blueprint.route("/post/<string:post_id>")
def single_post(post_id):
  post = PostModel.get(post_id)
  tags = PostTagLink.get_by_post_id(post_id)
  return render_template('post.html.j2', post=post, tags=tags)


@pages_blueprint.route('/upload', methods=['POST'])
def upload():
  f = request.files.get('upload')
  # Add more validations here
  extension = f.filename.split('.')[-1].lower()
  if extension not in ['jpg', 'gif', 'png', 'jpeg']:
    return upload_fail(message='Image only!')
  file_name = os.path.join(python_cms.ROOT_PATH, 'files_upload', f.filename)
  f.save(os.path.join(file_name))
  url = url_for('pages.uploaded_files', filename=f.filename)
  return upload_success(url=url)  # return upload_success call


@pages_blueprint.route('/post/delete/<string:post_id>')
@login_required
def delete_post(post_id):
  post = PostModel.get(post_id)
  if post.author_id != current_user.get_id():
    return "Csak bejelentkezett felhasználok törölhetnek postokat!", 403

  post_tags = PostTagLink.get_by_post_id(post_id)
  for post_tag in post_tags:
    post_tag.delete()

  post.delete()
  flash(f'A {post.title} című post törölve lett!')
  return redirect(url_for('pages.index'))


@pages_blueprint.route('/post/edit/<string:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
  post = PostModel.get(post_id)
  tags = PostTagLink.get_by_post_id(post_id)
  all_tags = TagModel.get_all()

  if post.author_id != current_user.get_id():
    return "Csak bejelentkezett felhasználók szerkeszthetik a posztot", 403

  form = PostForm()
  form.category.choices = [(1, 'Filozófia'), (2, 'Tudomány'), (3, 'Politika'),
                           (4, 'Versus')]

  if request.method == 'POST' and form.validate_on_submit():
    unescaped_body = html.unescape(request.form.get('body'))
    clean_body = bleach.clean(unescaped_body,
                              tags=bleach.sanitizer.ALLOWED_TAGS +
                              ['div', 'br', 'p', 'h1', 'h2', 'img', 'h3'],
                              attributes=['src', 'alt', 'style'])

    body = clean_body
    title = request.form.get('title')

    file = request.files['teaser_image']
    # print("----------------", file)

    # print("--------------", file)
    # if not file:
    #   flash('Kép nélkül nem tud postot létrehozni!')
    #   return render_template('edit_post.html.j2', form=form, post_id=post_id)
    filename = request.form.get('original_teaser_image')
    if not filename:
      file = request.files['teaser_image']
      filename = secure_filename(file.filename)

      # flash('Kép nélkül nem tud postot létrehozni!')
      # return render_template("edit.html.j2", form=form)
    print("---------------------", filename)
    post.teaser_image = filename

    # filename = secure_filename(file.filename)

    category_id = request.form.get('category')
    category = CategoryModel.get(category_id)
    promoted = request.form.get('promoted')
    post.title = title
    post.body = body
    post.author_id = current_user.get_id()

    post.promoted = bool(promoted)
    post.category_id = category_id
    post.category_name = category.name
    date_time = now.strftime("%d/%m/%Y")
    post.create_date = date_time

    post.save()

    # törölni kell az elözö tag-eke
    post_tags = PostTagLink.get_by_post_id(post_id)
    for post_tag in post_tags:
      post_tag.delete()
    # Hozzá kell adni az ujakat
    tags_from_form = request.form.get('added_tags')
    tags = list(set(tags_from_form.split("-")[1:]))
    for tag in tags:
      print(tag)
      tag_m = TagModel.get_by_name(tag)
      save_tag = PostTagLink(post_id, tag_m.id, tag)
      save_tag.save()

    flash(f'Post with title: {title} is created')
    return redirect(url_for('pages.index'))

  form.category.default = post.category_id
  form.process()
  form.title.data = post.title
  form.teaser_image.data = post.teaser_image
  form.body.data = post.body

  form.promoted = bool(post.promoted)
  return render_template('edit_post.html.j2',
                         form=form,
                         post=post,
                         post_id=post_id,
                         tags=all_tags)


# @pages_blueprint.route('/subscribe', methods=['POST'])
# def subscribe():
#   email = request.form.get("feliratkozas")

#   message = "Sikeres feliratkozás"
#   server = smtplib.SMTP("smtp.gmail.com", 587)
#   server.starttls()
#   server.login("csampaie.5@gmail.com", "ApentaF++")
#   server.sendmail("csampaie.5@gmail.com", email, message)

#   error_statemant = ""
#   if not email:
#     error_statemant = "Add meg az email címed"
#     return render_template("subscribe.html.j2", error_message=error_statemant)

#   return render_template("subscribe.html.j2", error_message=error_statemant)
