from os import environ, path, mkdir
from flask import Flask
from flask import Flask
from flask_login import LoginManager
from python_cms.db import db
from flask_ckeditor import CKEditor

from python_cms.blueprints.pages import pages_blueprint
from python_cms.blueprints.auth import auth_blueprint

from python_cms.models.user import UserModel
from python_cms.models.post import PostModel
from python_cms.models.category import CategoryModel
from python_cms.models.author import AuthorModel
from python_cms.models.tag import TagModel
from python_cms.models.post_tag import PostTagLink

app = Flask(__name__)
ROOT_PATH = app.root_path

# database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = environ.get(
    'SQLALCHEMY_TRACK_MODIFICATIONS')
db.init_app(app)

# this will enable autoreload if the html files change
app.jinja_env.auto_reload = True
app.secret_key = environ.get('SECRET_KEY')
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# https://flask-ckeditor.readthedocs.io/en/latest/index.html
app.config[
    'CKEDITOR_FILE_UPLOADER'] = 'pages.upload'  # this value can be endpoint or url
ckeditor = CKEditor(app)


@app.before_first_request
def create_tables():
  # create the files_upload folder if not exists. This is used by CKEditor images
  # and also the teaser image field when you create a blog post
  files_path = path.join(app.root_path, 'files_upload')
  if not path.exists(files_path):
    mkdir(files_path)
  # the app automatically creates the database tables before the first request, if
  # it does not exist
  db.create_all()


app.register_blueprint(pages_blueprint)
app.register_blueprint(auth_blueprint)


@login_manager.unauthorized_handler
def unauthorized():
  # This is what you get when you are not logged in but try to acccess a page
  # that can be only visited by authorized users. Could be changed to
  # a nice html template.
  return "You must be logged in to access this content.", 403


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
  return UserModel.get(user_id)


# this is only used in production. the flask run command ignores this.
# but when you deploy to heroku, this one will be used.
if __name__ == '__main__':
  # Threaded option to enable multiple instances for multiple user access
  # support
  app.run(threaded=True, port=80)
