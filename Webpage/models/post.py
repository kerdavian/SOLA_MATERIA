from python_cms.db import BaseModel, db


class PostModel(BaseModel):
  __tablename__ = 'posts'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  title = db.Column(db.String(150), nullable=False)
  teaser_image = db.Column(db.String(80), nullable=False)
  body = db.Column(db.String(20000), nullable=False)
  author_id = db.Column(db.String(), db.ForeignKey('users.id'))
  promoted = db.Column(db.Boolean(), nullable=False)
  category_id = db.Column(db.Integer(), db.ForeignKey('category.id'))
  category_name = db.Column(db.String(), nullable=False)
  # one post can have only one author
  author = db.relationship('UserModel', back_populates='posts')
  category = db.relationship('CategoryModel', back_populates='posts')

  def __init__(self, title, body, user_id, teaser_image, promoted, category_id,
               category_name):
    self.title = title
    self.body = body
    self.author_id = user_id
    self.teaser_image = teaser_image
    self.promoted = promoted
    self.category_id = category_id
    self.category_name = category_name

  @classmethod
  def get(cls, post_id):
    return cls.query.filter_by(id=post_id).first()

  @classmethod
  def get_all(cls):
    return cls.query.all()

  def save(self):
    db.session.add(self)
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()
