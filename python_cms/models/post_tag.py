from python_cms.db import BaseModel, db


class PostTagLink(BaseModel):
  __tablename__ = 'post_tag'
  post_id = db.Column(db.ForeignKey('posts.id'), primary_key=True)
  tag_id = db.Column(db.ForeignKey('tags.id'), primary_key=True)
  tag_name = db.Column(db.String(50))

  post = db.relationship('PostModel', back_populates='tags')
  tag = db.relationship('TagModel', back_populates='posts')

  def __init__(self, post_id, tag_id, tag_name):
    self.post_id = post_id
    self.tag_id = tag_id
    self.tag_name = tag_name

  def save(self):
    db.session.add(self)
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @classmethod
  def get_by_tag_id(cls, tag_id):
    return cls.query.filter_by(tag_id=tag_id).all()

  @classmethod
  def get_by_post_id(cls, post_id):
    return cls.query.filter_by(post_id=post_id).all()

  @classmethod
  def get_by_post_name(cls, tag_name):
    return cls.query.filter_by(tag_name=tag_name).all()

  @classmethod
  def get_all(cls):
    return cls.query.all()
