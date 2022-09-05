from sqlalchemy import ForeignKey
from main import db

Photo_tag = db.Table("Photo_tag", db.Model.metadata,
  db.Column("pid", db.Integer, db.ForeignKey('Photo.id')),
  db.Column("tid", db.Integer, db.ForeignKey('Tag.id'))
)

class Photo(db.Model):
  __tablename__ = "Photo"
  id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
  url = db.Column(db.String(), nullable=False)
  location = db.Column(db.Integer, db.ForeignKey('Location.id'))
  ncea = db.Column(db.String(), nullable=False)
  orientation = db.Column(db.String(), nullable=False)

  tags = db.relationship('Tag', secondary=Photo_tag, back_populates='photos')
  locations = db.relationship('Location', back_populates='photos')
  

class Tag(db.Model):
  __tablename__ = "Tag"
  id = db.Column(db.Integer(), primary_key=True, nullable=False, unique=True)
  tag_name = db.Column(db.String(), nullable=False)

  photos = db.relationship('Photo', secondary=Photo_tag, back_populates='tags')
  

class Location(db.Model):
  __tablename__ = "Location"
  id = db.Column(db.Integer(), primary_key=True, nullable=False, unique=True)
  location_name = db.Column(db.String(), nullable=False)

  photos = db.relationship('Photo', back_populates='locations')


class Users(db.Model):
  __tablename__ = "Users"
  id = db.Column(db.Integer(), primary_key=True, nullable=False, unique=True)
  username = db.Column(db.String(), nullable=False)
  password = db.Column(db.String(), nullable=False)