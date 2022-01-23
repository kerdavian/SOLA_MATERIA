from python_cms.db import BaseModel, db


class TagModel(BaseModel):
  __tablename__ = 'tags'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  tag_name = db.Column(db.String(50), nullable=False)

  posts = db.relationship('PostTagLink', back_populates='tag')

  def __init__(self, tag_name):
    self.tag_name = tag_name

  @classmethod
  def get_all(cls):
    return cls.query.all()

  @classmethod
  def get_by_name(cls, tag_name):
    return cls.query.filter_by(tag_name=tag_name).first()

  @classmethod
  def get_by_id(cls, tag_id):
    return cls.query.filter_by(tag_id=tag_id).first()