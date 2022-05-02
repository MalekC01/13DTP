from sqlalchemy import ForeignKey
from main import db

PhotoTags = db.Table('PhotoTags',
    db.Column('pid', db.Integer, db.ForeignKey('Photo.id')),
    db.Column('tid', db.Integer, db.ForeignKey('Tags.id'))
)

class Photo(db.Model):
  __tablename__ = "Photo"
  id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
  url = db.Column(db.String(), nullable=False)
  location = db.Column(db.String(), nullable=False)
  ncea = db.Column(db.Integer(), nullable=False)

  # def __repr__(self):
  #   return f'{self.name.upper()} Photo' 


class Tags(db.Model):
  __tablename__ = "Tags"
  id = db.Column(db.Integer(), primary_key=True, nullable=False, unique=True)
  Location = db.Column(db.String())
  Type = db.Column(db.String())
  Ncea = db.Column(db.Integer())

   

# class Photo_tag(db.Model):
#    __tablename__ = "Photo_tag"
#    pid = db.Column(db.Integer(), ForeignKey=True)


