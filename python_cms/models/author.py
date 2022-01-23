from python_cms.db import BaseModel, db
from flask_login import UserMixin


class AuthorModel(BaseModel, UserMixin):
  __tablename__ = 'author'
  id = db.Column(db.String(80), primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  email = db.Column(db.String(80), nullable=False)
  tema = db.Column(db.String(80), nullable=False)
  vegzettseg = db.Column(db.String(80), nullable=False)
  bemutatkozas = db.Column(db.String(80), nullable=False)
  profile_pic = db.Column(db.String(80))

  def __init__(self, id, name, email, tema, vegzettseg, bemutatkozas,
               profile_pic):
    self.id = id
    self.name = name
    self.email = email
    self.tema = tema
    self.vegzettseg = vegzettseg
    self.bemutatkozas = bemutatkozas
    self.profile_pic = profile_pic

  @classmethod
  def get(cls, user_id):
    return cls.query.filter_by(id=user_id).first()

  @classmethod
  def get_all(cls):
    return cls.query.all()
