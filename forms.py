from flask_wtf import FlaskForm
from wtforms import TextField, StringField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField, SelectMultipleField, widgets, PasswordField
from wtforms.validators import DataRequired, Optional, ValidationError
import models

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class Add_Photo(FlaskForm):
    ncea = RadioField('ncea', choices=[('Level 2','Level 2'),('Level 3','Level 3'), ('Not for NCEA','Not for NCEA')], validators=[DataRequired()])
    tags = MultiCheckboxField('tags')
    new_tag = TextField('new_tag')
    locations = RadioField('locations')
    new_location = TextField('new_location')
    orientation = RadioField('orientation', choices=[('Portrait','Portrait'), ('Landscape','Landscape') ], validators=[DataRequired()])

class Filter_images(FlaskForm):
    options = MultiCheckboxField('options')

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
