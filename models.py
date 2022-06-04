from sqlalchemy import ForeignKey
from main import db


class Photo(db.Model):
  __tablename__ = "Photo"
  id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
  url = db.Column(db.String(), nullable=False)
  location = db.Column(db.String(), nullable=False)
  ncea = db.Column(db.Integer(), nullable=False)
  orientation = db.Column(db.String(), nullable=False)

  # def __repr__(self):
  #   return f'{self.name.upper()} Photo' 


class Tags(db.Model):
  __tablename__ = "Tags"
  id = db.Column(db.Integer(), primary_key=True, nullable=False, unique=True)
  tag_name = db.Column(db.String(), nullable=False)

   

class Photo_tag(db.Model):
  __tablename__ = "Photo_tag"
  pid = db.Column(db.Integer(), primary_key=True, nullable=False, unique=True)
  tid = db.Column(db.Integer(), primary_key=True, nullable=False, unique=True)


class Locations(db.Model):
  __tablename__ = "Locations"
  id = db.Column(db.Integer(), primary_key=True, nullable=False, unique=True)
  location_name = db.Column(db.String(), nullable=False)