from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Optional, ValidationError
import models

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class Add_Photo(FlaskForm):
    ncea = RadioField('ncea', choices=[('Level 1','Level 2'),('Level 2','Level 3'), ('Not for NCEA','Not for NCEA')], validators=[DataRequired()])
    tags = MultiCheckboxField('tags', validators=[DataRequired()])
    new_tag = TextField('new_tag')
    locations = RadioField('locations', validators=[DataRequired()])
    new_location = TextField('new_location')
    orientation = RadioField('ncea', choices=[('Portrait','Portrait'), ('Landscape','Landscape') ], validators=[DataRequired()])