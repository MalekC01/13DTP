from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms.validators import DataRequired, Optional, ValidationError
import models

class Add_Photo(FlaskForm):
     def check_tag(form, field):
          pass

     ncea = RadioField('ncea', choices=[('Level 1','Level 1'),('Level 2','Level 2'), ('Not for NCEA','Not for NCEA')], validators=[DataRequired()])



     all_tags = models.Tags.query.filter_by(tag_name="portrait").all()
     print(all_tags)

     #tags = CheckboxField('tags', choices=[('Level 1','Level 1'),('Level 2','Level 2'), ('Not for NCEA','Not for NCEA')], validators=[DataRequired()])